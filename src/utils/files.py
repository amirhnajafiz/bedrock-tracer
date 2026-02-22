import json
import os
import shutil
from typing import Any, Dict


def create_dir(directory: str):
    """Force create a new directory (delete existing and create new one).

    :param directory: target directory path
    """
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)


def get_tracing_scripts(
    dir_path: str, memory_trace: bool = False, headless: bool = False
) -> Dict[str, str]:
    """Return the path of tracing scripts based on input directory path.
    """
    out = {
        "io": os.path.join(
            dir_path, "headless_io_trace.bt" if headless else "io_trace.bt"
        )
    }

    if memory_trace:
        out["memory"] = os.path.join(
            dir_path, "headless_memory_trace.bt" if headless else "memory_trace.bt"
        )

    return out


def write_reader_configs(dir_path: str, configs: Dict[str, Any]) -> None:
    """Export reader config file into a json file.

    :param dir_path: base directory
    """
    with open(os.path.join(dir_path, "reader.json"), "w") as file:
        json.dump(configs, file, indent=4)
