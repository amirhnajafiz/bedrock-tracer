import os
from typing import List


def _self_cgroup_signature() -> set[str]:
    """Get the cgroup signature of the current process.

    The cgroup signature is a set of cgroup paths that the process belongs to. It can be used to identify processes that are in the same container.

    Returns
    -------
    signature : set[str]
        A set of cgroup paths that the current process belongs to.
    """

    try:
        with open("/proc/self/cgroup", "r", encoding="utf-8") as f:
            return {line.strip().split(":")[-1] for line in f if line.strip()}
    except OSError:
        return set()


def _pid_cgroup_signature(pid: int) -> set[str]:
    """Get the cgroup signature of a process by its PID.

    Parameters
    ----------
    pid : int
        The PID of the process.

    Returns
    -------
    signature : set[str]
        A set of cgroup paths that the process belongs to.
    """

    try:
        with open(f"/proc/{pid}/cgroup", "r", encoding="utf-8") as f:
            return {line.strip().split(":")[-1] for line in f if line.strip()}
    except OSError:
        return set()


def _pid_ppid(pid: int) -> int | None:
    """Get the parent PID of a process by its PID.

    Parameters
    ----------
    pid : int
        The PID of the process.

    Returns
    -------
    ppid : int | None
        The parent PID of the process, or None if it cannot be determined.
    """

    try:
        with open(f"/proc/{pid}/status", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("PPid:"):
                    return int(line.split(":", 1)[1].strip())
    except (OSError, ValueError):
        return None
    return None


def _is_descendant_of(pid: int, ancestor_pid: int) -> bool:
    """Check if a process is a descendant of another process by their PIDs.

    Parameters
    ----------
    pid : int
        The PID of the process to check.
    ancestor_pid : int
        The PID of the potential ancestor process.

    Returns
    -------
    is_descendant : bool
        True if the process is a descendant of the ancestor process, False otherwise.
    """
    seen = set()
    current = pid

    while current and current not in seen:
        if current == ancestor_pid:
            return True

        seen.add(current)
        parent = _pid_ppid(current)

        if parent is None or parent <= 1:
            return False

        current = parent

    return False


def _normalize_script_tokens(scripts: List[str]) -> set[str]:
    """Normalize script paths to a set of tokens for matching.

    Parameters
    ----------
    scripts : List[str]
        A list of script paths.

    Returns
    -------
    tokens : set[str]
        A set of normalized tokens derived from the script paths for matching against process command lines.
    """

    tokens = set()

    for s in scripts:
        if not s:
            continue
        tokens.add(s)
        tokens.add(os.path.abspath(s))
        tokens.add(os.path.realpath(s))
        tokens.add(os.path.basename(s))

    return tokens


def bpftrace_processes_for_scripts(scripts: List[str]) -> List[tuple[int, str]]:
    """Find running bpftrace processes started by this cli instance in same container.

    Parameters
    ----------
    scripts : List[str]
        A list of script paths.

    Returns
    -------
    processes : List[tuple[int, str]]
        A list of tuples containing the PIDs and command lines of the found bpftrace processes.
    """

    if not scripts:
        return []

    # normalize the script paths to a set of tokens for matching
    script_tokens = _normalize_script_tokens(scripts)

    # get the current process PID and cgroup signature for filtering
    self_pid = os.getpid()
    self_cgroups = _self_cgroup_signature()

    processes: List[tuple[int, str]] = []

    # scan /proc for processes that match the criteria
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue

        pid = int(entry)
        if pid == self_pid:
            continue

        # hard boundary: same container cgroup
        if self_cgroups and _pid_cgroup_signature(pid) != self_cgroups:
            continue

        # hard boundary: spawned by this cli process tree
        if not _is_descendant_of(pid, self_pid):
            continue

        # soft boundary: command line contains bpftrace and any of the script tokens
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                raw = f.read()
        except OSError:
            continue

        if not raw:
            continue

        argv = [
            part.decode("utf-8", errors="ignore") for part in raw.split(b"\x00") if part
        ]
        if not argv:
            continue

        cmd = " ".join(argv)
        if "bpftrace" not in cmd:
            continue

        if any(tok and tok in cmd for tok in script_tokens):
            processes.append((pid, cmd))

    return processes
