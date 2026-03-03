import os


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
