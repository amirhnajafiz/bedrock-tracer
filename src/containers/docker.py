import logging
import subprocess
import time
from typing import Tuple


def docker_container_pid(container: str, retries: int = 0) -> Tuple[str, str]:
    """Find Docker container PID based on its name or ID.

    :param container: docker container name or id
    :param retries: number of retries (0 = infinite)
    :return: (pid, error_message)
    """

    count = 0
    while retries == 0 or count < retries:
        count += 1

        logging.debug("[docker] container not found or not running. waiting...")

        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Pid}}", container],
                capture_output=True,
                text=True,
                check=True,
            )

            pid = result.stdout.strip()

            # docker returns "0" if container exists but is not running
            if pid and pid != "0":
                return (pid, "")

        except subprocess.CalledProcessError as exc:
            return ("", f"[docker] failed to call inspect: {exc}")

        time.sleep(0.5)

    return (
        "",
        f"[docker] could not determine PID for container '{container}', hit retires threshold.",
    )
