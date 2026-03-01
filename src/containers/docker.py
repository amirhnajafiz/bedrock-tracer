import logging
import subprocess
import time


def container_pid(container: str, retries: int = 0) -> str:
    """Find a container's PID using docker inspect.

    Parameters
    ----------
    container : str
        Container name or uuid.
    retries : int
        Maximum number of retries

    Returns
    -------
    pid : str
        Container's PID.

    Raises
    ------
    RuntimeError
        If docker inspect fails.
    """

    count = 0
    while retries == 0 or count < retries:
        count += 1

        logging.debug(
            "[docker] container not found or not running. waiting for docker daemon to start the container..."
        )

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
                return pid

        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"failed docker inspect: {exc}")

        time.sleep(0.5)

    raise RuntimeError(
        f"could not determine PID for container '{container}', hit retires threshold."
    )
