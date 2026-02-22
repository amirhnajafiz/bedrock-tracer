from containers import cgroup_id_from_container_id, cgroup_id_from_pid
from containers.docker import container_pid
from containers.kubernetes import container_uid


def resolve_docker_container(container_name: str) -> str:
    """Resolve cgroup id of a docker container pod.

    :param container_name: name or uid
    :return: cgroup id
    """

    pid, err = container_pid(container_name)
    if err:
        raise RuntimeError(err)

    cgroup, err = cgroup_id_from_pid(pid)
    if err:
        raise RuntimeError(err)

    return cgroup


def resolve_k8s_pod(namespace: str, pod: str, container_name: str) -> str:
    """Resolve cgroup id of a Kubernetes pod.

    :param namespace: pod namespace
    :param pod: pod name
    :param container_name: container name inside pod
    :return: cgroup id
    """

    container_id, err = container_uid(
        namespace=namespace,
        pod=pod,
        container_name=container_name,
    )
    if err:
        raise RuntimeError(err)

    cgroup, err = cgroup_id_from_container_id(container_id)
    if err:
        raise RuntimeError(err)

    return cgroup
