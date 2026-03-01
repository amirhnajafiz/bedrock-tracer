import logging
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
            line = f.readline().strip()
            cgroup_path = line.split(":")[-1]
    except Exception as e:
        raise RuntimeError(f"could not read cgroup file: {e}")

    full_path = f"/sys/fs/cgroup{cgroup_path}"

    logging.debug("cgroup path for %s is found %s.", pid, full_path)

    try:
        stat_proc = subprocess.run(
            ["stat", "-c", "%i", full_path],
            capture_output=True,
            text=True,
            check=True,
        )

        return stat_proc.stdout.strip()
    except Exception as e:
        raise RuntimeError(f"could not stat cgroup path {full_path}: {e}")
