# Bedrock Tracer

Bedrock is an eBPF-based tracing tool that monitors file access patterns over regular I/O operations and memory map operations. This is a cloud-native tracer that enables tracing in regular or container-based platforms.

The tool enables tracing by:

* A running PID.
* A specific command name.
* Executing a process and tracing it.
* A specific cgroup id (used for containers).
* A specific command with a specific cgroup id (used for containers).

## Install

After cloning into the repository, run:

```sh
make
source .venv/bin/activate
```

Verify the installation:

```sh
$ bdtrace --help
usage: bdtrace [-h] [-o OUT] [-m MAX_STR_LEN] [-d] [-r] [-q] [-n] [-s ROTATE_SIZE]
               (--execute EXECUTE | --pid PID | --cgroup CGROUP | --docker_container DOCKER_CONTAINER | --k8s_pod K8S_POD | --procname PROCNAME)
               [--k8s_container K8S_CONTAINER] [--k8s_namespace K8S_NAMESPACE]

Bedrock tracer is ebpf-based file access pattern tracing tool.

options:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     output directory (default ./logs)
  -m MAX_STR_LEN, --max_str_len MAX_STR_LEN
                        ebpf maximum string lenght (default 150)
  -d, --debug           enable debug logs
  -r, --rotate          enable log rotation
  -q, --quiet_mode      enable queit tracing mode
  -n, --no_memory_trace
                        disable memory tracer
  -s ROTATE_SIZE, --rotate_size ROTATE_SIZE
                        log rotation size (default 100MB)
  --execute EXECUTE     execute and trace
  --pid PID             trace an existing pid
  --cgroup CGROUP       trace with matching cgroup
  --docker_container DOCKER_CONTAINER
                        trace docker container
  --k8s_pod K8S_POD     trace kubernetes pod
  --procname PROCNAME   trace by matching process command name
  --k8s_container K8S_CONTAINER
                        set kubernetes container to trace
  --k8s_namespace K8S_NAMESPACE
                        set the kubernetes pod's namespace
```

### Root Access

Bedrock tracer tracing modes need root access. Try the following approach to use it with sudo:

```sh
sudo $(which bdtrace) --execute ls
```

## Docker Image

See the [`docker-compose.yaml`](docker-compose.yaml) as an example of building the docker image and using it.
