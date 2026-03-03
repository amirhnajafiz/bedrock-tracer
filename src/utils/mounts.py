import os


def _ensure_mount(path: str):
    """Check if the target path is a mount point.

    Parameters
    ----------
    path : str
        The target path.

    Raises
    ------
    RuntimeError
        If the target path is not a mount point.
    """

    if not os.path.ismount(path):
        raise RuntimeError(f"{path} is not a mount point.")


def ensure_volumes():
    """Check if the required volumes are mounted.

    The required volumes are:
    - /sys
    - /lib/modules

    Raises
    ------
    RuntimeError
        If any of the required volumes is not mounted.
    """

    _ensure_mount("/sys")
    _ensure_mount("/lib/modules")
