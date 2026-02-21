from containers import container_cgroup_id, container_cgroup_id_from_pid
from containers.docker import docker_container_pid
from containers.kubernetes import pod_container_id


def resolve_docker(container_name: str) -> str:
    pid, err = docker_container_pid(container_name)
    if err:
        raise RuntimeError(err)

    cgroup, err = container_cgroup_id_from_pid(pid)
    if err:
        raise RuntimeError(err)

    return cgroup


def resolve_k8s(namespace: str, pod: str, container_name: str) -> str:
    container_id, err = pod_container_id(
        namespace=namespace,
        pod=pod,
        container_name=container_name,
    )
    if err:
        raise RuntimeError(err)

    cgroup, err = container_cgroup_id(container_id)
    if err:
        raise RuntimeError(err)

    return cgroup
