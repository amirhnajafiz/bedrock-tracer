import logging

from containers import cgroup_id_from_container_id, cgroup_id_from_pid
from containers.docker import container_pid
from containers.kubernetes import container_uid


def resolve_docker_container(container_name: str) -> str:
    """Resolve cgroup id of a docker container pod.

    Parameters
    ----------
    container_name : str
        Container name or uuid.

    Returns
    -------
    cgroup : str
        Container cgroup id.
    """

    pid = container_pid(container_name)

    logging.debug("container %s has pid %s.", container_name, pid)

    cgroup = cgroup_id_from_pid(pid)

    logging.debug("container %s has cgroup %s.", container_name, cgroup)

    return cgroup


def resolve_k8s_pod(namespace: str, pod: str, container_name: str) -> str:
    """Resolve cgroup id of a Kubernetes pod.

    Parameters
    ----------
    namespace : str
        Pod namespace name.
    pod : str
        Pod name.
    container_name : str
        Container name of the pod.

    Returns
    -------
    cgroup : str
        Container cgroup id.
    """

    container_id = container_uid(
        namespace=namespace,
        pod=pod,
        container_name=container_name,
    )

    logging.debug("container %s has uuid %s.", container_name, container_id)

    cgroup = cgroup_id_from_container_id(container_id)

    logging.debug("container %s has cgroup %s.", container_name, cgroup)

    return cgroup
