import logging
import os
import re
import subprocess


def cgroup_id_from_container_id(container_id: str) -> str:
    """Find a container's cgroup id using its container uid.

    Parameters
    ----------
    container_id : str
        The container uuid.

    Returns
    -------
    cgroupid : str
        The container cgroup id.

    Raises
    ------
    RuntimeError
        If cgroup path is not found or stat process fails.
    """

    try:
        find_proc = subprocess.run(
            ["find", "/sys/fs/cgroup/", "-type", "d", "-name", f"*{container_id}*"],
            capture_output=True,
            text=True,
            check=True,
        )

        path = find_proc.stdout.strip().splitlines()[0]
    except Exception as e:
        raise RuntimeError(f"could not find cgroup path: {e}")

    logging.debug("cgroup path for %s is found %s.", container_id, path)

    try:
        stat_proc = subprocess.run(
            ["stat", "-c", "%i", path], capture_output=True, text=True, check=True
        )

        cgroupid = stat_proc.stdout.strip()

        return cgroupid
    except Exception as e:
        raise RuntimeError(f"could not determine cgroupid for {path}: {e}")


def cgroup_id_from_pid(pid: str) -> str:
    """Find a process's cgroup id using its pid.

    Parameters
    ----------
    pid : str
        The process pid.

    Returns
    -------
    cgroupid : str
        The container cgroup id.

    Raises
    ------
    RuntimeError
        If cgroup path is not found or stat process fails.
    """

    try:
        with open(f"/proc/{pid}/cgroup", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        raise RuntimeError(f"could not read cgroup file: {e}")

    if not lines:
        raise RuntimeError(f"could not read cgroup file: no entries for pid {pid}")

    candidates = []
    rel_paths = []

    for line in lines:
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue

        _, controllers, cgroup_path = parts

        # keep path inside cgroup mount even if /proc/<pid>/cgroup has a leading ../
        rel_path = re.sub(r"^(\.\./)+", "", cgroup_path.lstrip("/"))

        if rel_path:
            rel_paths.append(rel_path)
            candidates.append(os.path.join("/sys/fs/cgroup", rel_path))
        else:
            candidates.append("/sys/fs/cgroup")

        if controllers:
            for controller in controllers.split(","):
                controller = controller.strip()
                if not controller:
                    continue
                controller_dir = controller.removeprefix("name=")
                if rel_path:
                    candidates.append(
                        os.path.join("/sys/fs/cgroup", controller_dir, rel_path)
                    )
                else:
                    candidates.append(os.path.join("/sys/fs/cgroup", controller_dir))

    # preserve order, remove duplicates
    candidates = list(dict.fromkeys(candidates))

    last_error = None
    for full_path in candidates:
        logging.debug("trying cgroup path for %s: %s", pid, full_path)
        try:
            stat_proc = subprocess.run(
                ["stat", "-c", "%i", full_path],
                capture_output=True,
                text=True,
                check=True,
            )
            return stat_proc.stdout.strip()
        except Exception as e:
            last_error = e

    # fallback: search by the leaf cgroup directory when path prefixes differ
    for rel_path in dict.fromkeys(rel_paths):
        leaf = os.path.basename(rel_path)
        if not leaf:
            continue
        try:
            find_proc = subprocess.run(
                ["find", "/sys/fs/cgroup", "-type", "d", "-name", leaf],
                capture_output=True,
                text=True,
                check=True,
            )
            match = find_proc.stdout.strip().splitlines()
            if not match:
                continue

            full_path = match[0]
            logging.debug("fallback cgroup path for %s resolved to %s", pid, full_path)

            stat_proc = subprocess.run(
                ["stat", "-c", "%i", full_path],
                capture_output=True,
                text=True,
                check=True,
            )
            return stat_proc.stdout.strip()
        except Exception as e:
            last_error = e

    raise RuntimeError(
        f"could not stat any cgroup path for pid {pid}; tried {candidates}: {last_error}"
    )
