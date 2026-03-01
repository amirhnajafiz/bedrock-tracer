import logging
import subprocess
import time


def container_uid(
    namespace: str, pod: str, container_name: str, retries: int = 0
) -> str:
    """Find container uid of Kubernetes pod.

    Find Kubernetes pod's container id based on its namespace, name, and container using crictl.

    Parameters
    ----------
    namespace : str
        Kubernetes pod's namespace.
    pod : str
        Kubernetes pod's name.
    container_name : str
        Kubernetes pod's container name.
    retries : int
        Number of retries for finding the container.

    Returns
    -------
    containerid : str
        Container uuid from crictl.

    Raises
    ------
    RuntimeError
        If crictl fails.
    """

    count = 0
    while retries == 0 or count < retries:
        count += 1

        logging.debug(
            "[kubernetes] container not found. waiting for CRI to start the container ..."
        )

        try:
            result = subprocess.run(
                ["crictl", "ps", "--namespace", namespace],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"error running crictl ps: {exc}")

        containerid = None
        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if len(parts) >= 11 and parts[9] == pod and parts[6] == container_name:
                containerid = parts[0]
                break

        if containerid:
            return containerid

        time.sleep(0.5)

    raise RuntimeError(
        f"could not determine UUID for container '{container_name}', hit retires threshold."
    )
