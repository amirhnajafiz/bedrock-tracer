# Bedrock Tracer

Bedrock is an eBPF-based tracing tool for monitoring file access through:

- VFS operations
- regular I/O operations
- memory map operations

It can trace workloads running directly on the host or inside containers.

## What you can trace?

Bedrock supports tracing by:

- a running PID (`--pid`)
- a process name (`--procname`)
- executing and tracing a command (`--execute`)
- a cgroup id (`--cgroup`)
- a container id/name (`--container`)
- a Kubernetes pod (`--kubernetes__pod`)

## Local Installation

After cloning this repository:

```sh
make
source .venv/bin/activate
```

Verify installation:

```sh
bdtrace --help
```

> NOTE: bdtrace needs privileged access for tracing.

## Quick Start

Trace a command:

```sh
sudo $(which bdtrace) --execute ls
```

Trace a running process:

```sh
sudo $(which bdtrace) --pid <PID>
```

Trace by process name:

```sh
sudo $(which bdtrace) --procname <PROCESS_NAME>
```

## CLI Help

Print full CLI help:

```sh
bdtrace --help
```

Main options:

- `-o, --out`: output directory (default: `./logs`)
- `-r, --rotate`: enable log rotation
- `--rotate_size`: log rotation size (default: `100MB`)
- `--version`: bpftrace scripts version (default: `v1`)
- `--headless`: disable metadata capture
- `--disable_vfs`: disable VFS tracer
- `--disable_io`: disable I/O tracer
- `--disable_memory_map`: disable mmap tracer
- `-d, --debug`: enable debug logs

Trace target selectors (choose one):

- `--execute <COMMAND>`
- `--pid <PID>`
- `--cgroup <CGROUP_ID>`
- `--procname <NAME>`
- `--container <CONTAINER>`
- `--kubernetes__pod <POD>` (optional: `--kubernetes__namespace`, `--kubernetes__container`)

## Docker Usage

Bedrock can run fully inside a Docker container. Because tracing depends on kernel interfaces, run the container with elevated privileges and host mounts.

Build the image:

```sh
docker build -f build/Dockerfile -t bedrock-tracer .
```

Run a trace command and write logs to a host directory:

```sh
mkdir -p logs
docker run --rm \
  --privileged \
  --pid=host \
  -v /sys:/sys:rw \
  -v /lib/modules:/lib/modules:ro \
  -v "$(pwd)/logs:/logs" \
  bedrock-tracer \
  bdtrace --execute ls -o /logs/trace_ls
```

Run help inside the image:

```sh
docker run --rm bedrock-tracer bdtrace --help
```

For additional containerized examples (including end-to-end and Kubernetes-oriented runs), see `docker-compose.yaml`.

## Docker Troubleshooting

### `Operation not permitted` or attach failures

Cause: container is missing required privileges for eBPF tracing.

Fix: run with both `--privileged` and `--pid=host`.

### `No such file or directory` for kernel paths

Cause: required host kernel paths are not mounted.

Fix: mount these paths into the container:

```sh
-v /sys:/sys:rw -v /lib/modules:/lib/modules:ro
```

### Trace starts but no events are captured

Cause: target process ended quickly, or filters do not match the real workload.

Fix:

- start with `--execute <command>` to validate baseline tracing
- verify PID/process/container values are correct
- run with `-d` to enable debug logs

### `bpftrace` program fails on startup

Cause: host kernel and available tracepoints/kprobes may not support the selected script version.

Fix:

- try `--version v0` or `--version v1`
- run a minimal command first: `bdtrace --execute ls`
- verify host compatibility using scripts in `bpftrace/kernel_support.sh`

### Output directory issues

Cause: output path is not writable from inside the container.

Fix:

- bind mount a writable host directory (for example `$(pwd)/logs:/logs`)
- pass `-o /logs/<trace_name>` in `bdtrace`

## Root Access

All tracing modes require root privileges.

If `bdtrace` is installed in a virtual environment, use:

```sh
sudo $(which bdtrace) --execute ls
```

## Design

The `cli` program is a process coordinator. It launches multiple `bpftrace` commands as child processes, grouped by tracer type:

- VFS tracer
- I/O tracer
- mmap tracer

Each tracer runs in its own thread so the coordinator remains non-blocking. Each thread pipes child `stdout` and `stderr` either to files or to the coordinator's `stdout`.

The main process periodically monitors child state:

1. A tracer fails: the thread raises a failure event, and the main process stops all remaining tracers before cleanup.
2. A tracer exits normally: the thread raises a stop event; once all tracers have stopped, cleanup starts.
3. A `SIGTERM` is received: the main process signals all tracer threads to stop, then proceeds to cleanup.

During cleanup, all `bpftrace` child processes are terminated to avoid leaving stale tracing processes attached to the kernel.
