import os
import stat
import socket


DOCKER_SOCKET = "/var/run/docker.sock"
KUBERNETES_SA_TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"


def ensure_docker_env():
    """Check if the current environment is running in Docker.

    It checks for the presence of the Docker socket at /var/run/docker.sock to confirm that it's running in Docker.

    Raises
    ------
    RuntimeError
        If the current environment is not running in Docker.
    """

    # check if the Docker socket exists
    if not os.path.exists(DOCKER_SOCKET):
        raise RuntimeError("Not running in Docker environment.")
    
    # check if the Docker socket is a socket file
    if not stat.S_ISSOCK(os.stat(DOCKER_SOCKET).st_mode):
        raise RuntimeError("Docker socket not found, is it mounted correctly?")
    
    # try to connect to the Docker socket to ensure it's working
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(DOCKER_SOCKET)
        client.close()
    except Exception as e:
        raise RuntimeError("Failed to connect to Docker socket, is it working correctly?") from e


def ensure_kubernetes_env():
    """Check if the current environment is running in Kubernetes.

    It needs to have the Kubernetes service account token file at /var/run/secrets/kubernetes.io/serviceaccount/token to confirm that it's running in Kubernetes.
    Also the /sys, /lib/modules, and crictl socket mounts are only needed when running in Kubernetes,
    so we can use the presence of the token file to determine if we're in Kubernetes or not.

    Raises
    ------
    RuntimeError
        If the current environment is not running in Kubernetes or if CRI socket is not found when running in Kubernetes.
    """

    if not os.path.exists(KUBERNETES_SA_TOKEN_PATH):
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
