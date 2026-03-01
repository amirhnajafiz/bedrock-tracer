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

    Raises
    ------
    RuntimeError
        If pid or cgroup is not found.
    """

    pid, err = container_pid(container_name)
    if err:
        raise RuntimeError(err)

    logging.debug("container %s has pid %s.", container_name, pid)

    cgroup, err = cgroup_id_from_pid(pid)
    if err:
        raise RuntimeError(err)

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

    Raises
    ------
    RuntimeError
        If uuid or cgroup is not found.
    """

    container_id, err = container_uid(
        namespace=namespace,
        pod=pod,
        container_name=container_name,
    )
    if err:
        raise RuntimeError(err)

    logging.debug("container %s has uuid %s.", container_name, container_id)

    cgroup, err = cgroup_id_from_container_id(container_id)
    if err:
        raise RuntimeError(err)

    logging.debug("container %s has cgroup %s.", container_name, cgroup)

    return cgroup
