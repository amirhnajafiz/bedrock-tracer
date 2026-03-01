import json
import os
import shutil
from typing import Any, Dict


def create_dir(directory: str):
    """Create directory.

    Create a new directory (delete existing and create new one).

    Parameters
    ----------
    directory : str
        Target directory path.
    """

    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)


def get_tracing_scripts(
    dir_path: str,
    disable_vfs: bool = False,
    disable_io: bool = False,
    disable_memory_map: bool = False,
    headless: bool = False,
) -> Dict[str, str]:
    """Get tracing scripts by dir_path.

    Return the path of tracing scripts based on input directory path.

    Parameters
    ----------
    dir_path : str
        The bpftrace scripts directory and subdirectory.
    disable_vfs : bool
        Disable VFS tracer.
    disable_io : bool
        Disable IO tracer.
    disable_memory_map : bool
        Disable memory map tracer.
    headless : bool
        Headless tracing mode.

    Returns
    -------
    out : Dict
        Map of tracing group and tracing script.
    """

    out = {}

    if not disable_vfs:
        out["vfs"] = os.path.join(
            dir_path, "headless_vfs_trace.bt" if headless else "vfs_trace.bt"
        )

    if not disable_io:
        out["io"] = os.path.join(
            dir_path, "headless_io_trace.bt" if headless else "io_trace.bt"
        )

    if not disable_memory_map:
        out["memory"] = os.path.join(
            dir_path, "headless_memory_trace.bt" if headless else "memory_trace.bt"
        )

    return out


def write_reader_configs(dir_path: str, configs: Dict[str, Any]) -> None:
    """Write reader configuration.

    Export reader config file into a JSON file called `reader.json`.

    Parameters
    ----------
    dir_path : str
        Base directory path.
    """

    with open(os.path.join(dir_path, "reader.json"), "w") as file:
        json.dump(configs, file, indent=4)
