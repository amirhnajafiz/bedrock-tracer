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
usage: bdtrace [-h] [-o OUT] [-r] [--rotate_size ROTATE_SIZE] [--version VERSION] [--headless] [--disable_vfs] [--disable_io] [--disable_memory_map] [-d]
               (--execute EXECUTE | --pid PID | --cgroup CGROUP | --procname PROCNAME | --container CONTAINER | --kubernetes__pod KUBERNETES__POD) [--kubernetes__container KUBERNETES__CONTAINER]
               [--kubernetes__namespace KUBERNETES__NAMESPACE]

Bedrock is an ebpf-based file system tracing tool.

optional arguments:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     output directory (default ./logs)
  -r, --rotate          enable log rotation
  --rotate_size ROTATE_SIZE
                        log rotation size (default 100MB)
  --version VERSION     bedrock-bpftrace scripts version (default v1, which reduces output log size but increases the risk of missing events.)
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
                        set the kubernetes pod's namespac
```

### Root Access

Bedrock tracer tracing modes need root access. Try the following approach to use it with sudo:

```sh
sudo $(which bdtrace) --execute ls
```

## Docker Image

See the [`docker-compose.yaml`](docker-compose.yaml) as an example of building the docker image and using it.

## Design

The `cli` program is a process coordinator. It executes `bpftrace` commands as child processes. These commands are categorized as:

* VFS Tracing
* I/O Tracing
* mmap Tracing

When starting the `cli` program, each tracer will start a new child process within a thread. Threads are used in the `cli` program to make it a non-blocking program. Each thread pipes `stdout` and `stderr` of it's child process into a file or `cli`'s `stdout`.

The main process, created by `cli` program, monitors the child processes periodically. Three scenarios can happen:

1. The `bpftrace` command fails. With this scenario, the thread raises a failure by setting a failure event. The main process checks these events periodically and if a failure happens, it stops all other processes and starts the cleanup phase.
2. The `bpftrace` command finishes. With this scenario, the thread raises a stop event. The main process waits until the thread is finished. If all running threads are finished, then it starts the cleanup phase.
3. A `sigterm` signal is received. With this scenario, the main process raises a stop event to each thread. Each thread will terminate it's child process and raises a stop event (case 2).

During the cleanup phase, all `bpftrace` processes will be terminated to prevent kernel issues.
