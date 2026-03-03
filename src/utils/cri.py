import os


def ensure_docker():
    """Check if the current environment is running in Docker.

    It needs to have the Docker socket mounted at /var/run/docker.sock to confirm that it's running in Docker.

    Raises
    ------
    RuntimeError
        If the current environment is not running in Docker.
    """

    if not os.path.exists("/run/docker.sock"):
        raise RuntimeError("Not running in Docker environment.")


def ensure_kubernetes():
    """Check if the current environment is running in Kubernetes.

    It needs to have the Kubernetes service account token file at /var/run/secrets/kubernetes.io/serviceaccount/token to confirm that it's running in Kubernetes.
    Also the /sys, /lib/modules, and crictl socket mounts are only needed when running in Kubernetes,
    so we can use the presence of the token file to determine if we're in Kubernetes or not.

    Raises
    ------
    RuntimeError
        If the current environment is not running in Kubernetes or if CRI socket is not found when running in Kubernetes.
    """

    if not os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
        raise RuntimeError("Not running in Kubernetes environment.")

    # check if CONTAINER_RUNTIME_ENDPOINT environment variable is set
    if "CONTAINER_RUNTIME_ENDPOINT" not in os.environ:
        raise RuntimeError(
            "CONTAINER_RUNTIME_ENDPOINT environment variable is not set."
        )

    # check if the container runtime socket exists
    container_runtime_socket = os.environ["CONTAINER_RUNTIME_ENDPOINT"].replace(
        "unix://", ""
    )
    if not os.path.exists(container_runtime_socket):
        raise RuntimeError(
            f"Container runtime socket '{container_runtime_socket}' not found."
        )
