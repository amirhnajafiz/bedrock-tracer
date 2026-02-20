import logging
import subprocess
import time
from typing import Tuple


def pod_container_id(
    namespace: str, pod: str, container_name: str, retries: int = 0
) -> Tuple[str, str]:
    """Find Kubernetes pod's container id based on its namespace, name, and container using crictl.

    :param namespace: kubernetes namespace
    :param pod: kubernetes pod name
    :param container_name: kubernetes pod's container name
    :param retries: number of retries for finding the container
    :return: container id
    """

    count = 0
    while retries == 0 or count < retries:
        count += 1

        logging.debug(
            "[kubernetes] container not found. waiting for cri to start the container ..."
        )

        try:
            result = subprocess.run(
                ["crictl", "ps", "--namespace", namespace],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            return ("", f"[kubernetes] error running crictl ps: {exc}")

        containerid = None
        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if len(parts) >= 11 and parts[9] == pod and parts[6] == container_name:
                containerid = parts[0]
                break

        if containerid:
            return (containerid, "")

        time.sleep(0.5)

    return ("", "[kubernetes] container not found, hit retries threshold.")
