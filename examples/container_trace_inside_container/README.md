# Container Trace Inside Container

Let's setup a target container for tracing:

```sh
docker run -d --name nginx-container nginx
```

Check if the container is running:

```sh
docker ps
# CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS     NAMES
# 9848db215d15   nginx     "/docker-entrypoint.…"   16 minutes ago   Up 16 minutes   80/tcp    nginx-container
```

Run bedrock as a process to trace the target container:

```sh
sudo $(which bdtrace) --debug --container nginx-container -o /tmp/bedrock/logs
# 2026-03-31 11:46:37,934 - root - DEBUG: output directory /tmp/bedrock/logs/20260331_114637 initialized.
# 2026-03-31 11:46:37,935 - root - INFO: configs:
# 	{'debug': True, 'out': '/tmp/bedrock/logs/20260331_114637', 'rotate': False, 'rotate_size': '100MB', 'filter': None, 'headless': False, 'disable_vfs': False, 'disable_io': False, 'disable_memory_map': False, 'version': 'v1', 'execute': None, 'pid': None, 'cgroup': None, 'procname': None, 'container': 'nginx-container', 'kubernetes__pod': None, 'kubernetes__container': None, 'kubernetes__namespace': None}
# 2026-03-31 11:46:37,935 - root - INFO: cli started.
# 2026-03-31 11:46:37,935 - root - DEBUG: selected container handler.
# 2026-03-31 11:46:37,935 - root - DEBUG: [docker] container not found or not running. waiting for docker daemon to start the container...
# 2026-03-31 11:46:37,951 - root - DEBUG: container nginx-container has pid 509836.
# 2026-03-31 11:46:37,951 - root - DEBUG: trying cgroup path for 509836: /sys/fs/cgroup/system.slice/docker-9848db215d158b83057aeb3cc9cdecbaeed6b6155254e29c69619fce9181006d.scope
# 2026-03-31 11:46:37,952 - root - DEBUG: container nginx-container has cgroup 105973.
# 2026-03-31 11:46:37,952 - root - DEBUG: building tracer for vfs : bpftrace/cgroup/v1/vfs_trace.bt
# 2026-03-31 11:46:37,953 - root - DEBUG: searching for bpftrace/cgroup/v1/vfs_trace.bt script.
# 2026-03-31 11:46:37,953 - root - DEBUG: tracer output directory: /tmp/bedrock/logs/20260331_114637/vfs.
# 2026-03-31 11:46:37,953 - root - DEBUG: mono tracer created.
# 2026-03-31 11:46:37,953 - root - DEBUG: building tracer for io : bpftrace/cgroup/v1/io_trace.bt
# 2026-03-31 11:46:37,953 - root - DEBUG: searching for bpftrace/cgroup/v1/io_trace.bt script.
# 2026-03-31 11:46:37,954 - root - DEBUG: tracer output directory: /tmp/bedrock/logs/20260331_114637/io.
# 2026-03-31 11:46:37,954 - root - DEBUG: mono tracer created.
# 2026-03-31 11:46:37,954 - root - DEBUG: building tracer for memory : bpftrace/cgroup/v1/memory_trace.bt
# 2026-03-31 11:46:37,954 - root - DEBUG: searching for bpftrace/cgroup/v1/memory_trace.bt script.
# 2026-03-31 11:46:37,954 - root - DEBUG: tracer output directory: /tmp/bedrock/logs/20260331_114637/memory.
# 2026-03-31 11:46:37,954 - root - DEBUG: mono tracer created.
# 2026-03-31 11:46:37,954 - root - DEBUG: prepare to run 3 tracers.
# 2026-03-31 11:46:37,954 - root - DEBUG: termination signal handlers are bounded for 2, 15 and 17.
# 2026-03-31 11:46:37,954 - root - DEBUG: using parameters for timestamp converts:
# 	ref wall: 1774971997.9546
# 	ref mono: 2919314.99
# 2026-03-31 11:46:37,954 - root - DEBUG: reference timestamps saved to: /tmp/bedrock/logs/20260331_114637/reference_timestamps.json
# 2026-03-31 11:46:37,954 - root - INFO: starting vfs ...
# 2026-03-31 11:46:37,955 - root - DEBUG: [vfs] starting tracer: bpftrace -o /tmp/bedrock/logs/20260331_114637/vfs/trace_0.log bpftrace/cgroup/v1/vfs_trace.bt 105973
# 2026-03-31 11:46:37,955 - root - DEBUG: [vfs] tracer started in thread 126513859000000.
# 2026-03-31 11:46:37,955 - root - INFO: starting io ...
# 2026-03-31 11:46:37,955 - root - DEBUG: [io] starting tracer: bpftrace -o /tmp/bedrock/logs/20260331_114637/io/trace_0.log bpftrace/cgroup/v1/io_trace.bt 105973
# 2026-03-31 11:46:37,955 - root - DEBUG: [io] tracer started in thread 126513850607296.
# 2026-03-31 11:46:37,955 - root - INFO: starting memory ...
# 2026-03-31 11:46:37,955 - root - DEBUG: [memory] starting tracer: bpftrace -o /tmp/bedrock/logs/20260331_114637/memory/trace_0.log bpftrace/cgroup/v1/memory_trace.bt 105973
# 2026-03-31 11:46:37,955 - root - DEBUG: [memory] tracer started in thread 126513842214592.
# 2026-03-31 11:46:37,957 - root - INFO: all tracers started.
# Attached 39 probes
# Attached 30 probes
# Attached 9 probes
```

Or, run bedrock as another container to trace the target container:

```sh
docker build -f build/Dockerfile -t bedrock-tracer .
docker run --rm --privileged --pid=host -v /sys:/sys:rw -v /lib/modules:/lib/modules:ro -v "/tmp/bedrock/logs:/logs" -v /var/run/docker.sock:/var/run/docker.sock bedrock-tracer bdtrace --debug nginx-container -o /logs
# 2026-03-31 15:39:12,914 - root - DEBUG: output directory logs/20260331_153912 initialized.
# 2026-03-31 15:39:12,914 - root - INFO: configs:
# 	{'debug': True, 'out': 'logs/20260331_153912', 'rotate': False, 'rotate_size': '100MB', 'filter': None, 'headless': False, 'disable_vfs': False, 'disable_io': False, 'disable_memory_map': False, 'version': 'v1', 'execute': None, 'pid': None, 'cgroup': None, 'procname': None, 'container': 'nginx-container', 'kubernetes__pod': None, 'kubernetes__container': None, 'kubernetes__namespace': None}
# 2026-03-31 15:39:12,915 - root - INFO: cli started.
# 2026-03-31 15:39:12,915 - root - DEBUG: selected container handler.
# 2026-03-31 15:39:12,915 - root - DEBUG: [docker] container not found or not running. waiting for docker daemon to start the container...
# 2026-03-31 15:39:12,929 - root - DEBUG: container nginx-container has pid 509836.
# 2026-03-31 15:39:12,930 - root - DEBUG: trying cgroup path for 509836: /sys/fs/cgroup/docker-9848db215d158b83057aeb3cc9cdecbaeed6b6155254e29c69619fce9181006d.scope
# 2026-03-31 15:39:12,938 - root - DEBUG: fallback cgroup path for 509836 resolved to /sys/fs/cgroup/system.slice/docker-9848db215d158b83057aeb3cc9cdecbaeed6b6155254e29c69619fce9181006d.scope
# 2026-03-31 15:39:12,939 - root - DEBUG: container nginx-container has cgroup 105973.
# 2026-03-31 15:39:12,940 - root - DEBUG: building tracer for vfs : bpftrace/cgroup/v1/vfs_trace.bt
# 2026-03-31 15:39:12,940 - root - DEBUG: searching for bpftrace/cgroup/v1/vfs_trace.bt script.
# 2026-03-31 15:39:12,940 - root - DEBUG: tracer output directory: logs/20260331_153912/vfs.
# 2026-03-31 15:39:12,940 - root - DEBUG: mono tracer created.
# 2026-03-31 15:39:12,940 - root - DEBUG: building tracer for io : bpftrace/cgroup/v1/io_trace.bt
# 2026-03-31 15:39:12,940 - root - DEBUG: searching for bpftrace/cgroup/v1/io_trace.bt script.
# 2026-03-31 15:39:12,940 - root - DEBUG: tracer output directory: logs/20260331_153912/io.
# 2026-03-31 15:39:12,940 - root - DEBUG: mono tracer created.
# 2026-03-31 15:39:12,940 - root - DEBUG: building tracer for memory : bpftrace/cgroup/v1/memory_trace.bt
# 2026-03-31 15:39:12,940 - root - DEBUG: searching for bpftrace/cgroup/v1/memory_trace.bt script.
# 2026-03-31 15:39:12,940 - root - DEBUG: tracer output directory: logs/20260331_153912/memory.
# 2026-03-31 15:39:12,940 - root - DEBUG: mono tracer created.
# 2026-03-31 15:39:12,940 - root - DEBUG: prepare to run 3 tracers.
# 2026-03-31 15:39:12,940 - root - DEBUG: termination signal handlers are bounded for 2, 15 and 17.
# 2026-03-31 15:39:12,940 - root - DEBUG: using parameters for timestamp converts:
# 	ref wall: 1774971552.9408703
# 	ref mono: 2918869.97
# 2026-03-31 15:39:12,941 - root - DEBUG: reference timestamps saved to: logs/20260331_153912/reference_timestamps.json
# 2026-03-31 15:39:12,941 - root - INFO: starting vfs ...
# 2026-03-31 15:39:12,941 - root - DEBUG: [vfs] starting tracer: bpftrace -o logs/20260331_153912/vfs/trace_0.log bpftrace/cgroup/v1/vfs_trace.bt 105973
# 2026-03-31 15:39:12,941 - root - DEBUG: [vfs] tracer started in thread 125253114660544.
# 2026-03-31 15:39:12,941 - root - INFO: starting io ...
# 2026-03-31 15:39:12,941 - root - DEBUG: [io] starting tracer: bpftrace -o logs/20260331_153912/io/trace_0.log bpftrace/cgroup/v1/io_trace.bt 105973
# 2026-03-31 15:39:12,941 - root - DEBUG: [io] tracer started in thread 125253106267840.
# 2026-03-31 15:39:12,942 - root - INFO: starting memory ...
# 2026-03-31 15:39:12,942 - root - DEBUG: [memory] starting tracer: bpftrace -o logs/20260331_153912/memory/trace_0.log bpftrace/cgroup/v1/memory_trace.bt 105973
# 2026-03-31 15:39:12,942 - root - DEBUG: [memory] tracer started in thread 125253097858752.
# 2026-03-31 15:39:12,942 - root - INFO: all tracers started.
# Attached 39 probes
# Attached 30 probes
# Attached 9 probes
```
