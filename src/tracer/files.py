import os
from typing import Dict


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
