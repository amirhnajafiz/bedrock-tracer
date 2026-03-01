import json
import os
import shutil
from typing import Any, Dict


def create_dir(directory: str):
    """Create a directory.

    Create a new directory (delete existing and create new one).

    Parameters
    ----------
    directory : str
        Target directory path.
    """

    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)


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
