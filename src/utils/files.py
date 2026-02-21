import os
import shutil


def create_dir(directory: str):
    """Force create a new directory (delete existing and create new one).

    :param directory: target directory path
    """
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)


def get_tracing_scripts(
    dir_path: str, no_memory_trace: bool = False, quiet_mode: bool = False
) -> dict[str:str]:
    """Return the path of tracing scripts based on input directory path.

    :param dir_path: base directory of the target tracer
    """
    out = {
        "io": os.path.join(
            dir_path, "silent_io_trace.bt" if quiet_mode else "io_trace.bt"
        )
    }

    if not no_memory_trace:
        out["memory"] = os.path.join(
            dir_path, "silent_memory_trace.bt" if quiet_mode else "memory_trace.bt"
        )

    return out
