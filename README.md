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
usage: bdtrace [-h] [-o OUT] [-r] [--rotate_size ROTATE_SIZE] [--headless] [--disable_vfs] [--disable_io] [--disable_memory_map] [-d]
               (--execute EXECUTE | --pid PID | --cgroup CGROUP | --procname PROCNAME | --container CONTAINER | --kubernetes__pod KUBERNETES__POD)
               [--kubernetes__container KUBERNETES__CONTAINER] [--kubernetes__namespace KUBERNETES__NAMESPACE]

Bedrock is an ebpf-based file system tracing tool.

options:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     output directory (default ./logs)
  -r, --rotate          enable log rotation
  --rotate_size ROTATE_SIZE
                        log rotation size (default 100MB)
  --headless            enable headless tracing mode (not capturing metadata)
  --disable_vfs         disable vfs tracer
  --disable_io          disable io tracer
  --disable_memory_map  disable memory map tracer
  -d, --debug           enable debug logs
  --execute EXECUTE     execute and trace
  --pid PID             trace an existing pid
  --cgroup CGROUP       trace with matching cgroup
  --procname PROCNAME   trace by matching process command name
  --container CONTAINER
                        trace a docker container
  --kubernetes__pod KUBERNETES__POD
                        trace a kubernetes pod
  --kubernetes__container KUBERNETES__CONTAINER
                        set kubernetes container to trace
  --kubernetes__namespace KUBERNETES__NAMESPACE
                        set the kubernetes pod's namespace
```

### Root Access

Bedrock tracer tracing modes need root access. Try the following approach to use it with sudo:

```sh
sudo $(which bdtrace) --execute ls
```

## Docker Image

See the [`docker-compose.yaml`](docker-compose.yaml) as an example of building the docker image and using it.
