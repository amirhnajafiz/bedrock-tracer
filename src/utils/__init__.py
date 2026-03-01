import os
import shutil


def must_support_bpftrace():
    """Check if bpftrace is supported.

    Raises
    -----
    RuntimeError
        If bpftrace is not installed.
    """

    if shutil.which("bpftrace") is None:
        raise RuntimeError("bpftrace not found in PATH. Please install bpftrace.")


def ensure_script(path: str):
    """Check if the target script exists.

    Parameters
    ----------
    path : str
        The target script path.

    Raises
    ------
    RuntimeError
        If the script file is not found.
    """

    if not os.path.isfile(path):
        raise RuntimeError(f"required script '{path}' not found.")
