import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bedrock is an ebpf-based file system tracing tool."
    )

    # common flags
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logs")
    parser.add_argument(
        "-o", "--out", default="logs", help="output directory (default ./logs)"
    )
    parser.add_argument(
        "-r", "--rotate", action="store_true", help="enable log rotation"
    )
    parser.add_argument(
        "--rotate_size",
        default="100MB",
        help="log rotation size (e.g. \"100MB\", \"10KB\", \"102400\") (default 100MB)",
    )
    parser.add_argument(
        "--filter", 
        help="filter events by a bpftrace comm expression (e.g. 'comm == \"bash\"')",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="enable headless tracing mode (not capturing metadata)",
    )
    parser.add_argument("--disable_vfs", action="store_true", help="disable vfs tracer")
    parser.add_argument(
        "--disable_io",
        action="store_true",
        help="disable io tracer",
    )
    parser.add_argument(
        "--disable_memory_map", action="store_true", help="disable memory map tracer"
    )
    parser.add_argument(
        "--version",
        default="v1",
        help="bedrock-bpftrace scripts version (default v1, which reduces output log size but increases the risk of missing events.)",
    )

    # mutually exclusive tracing modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--execute", help="execute and trace")
    group.add_argument("--pid", help="trace an existing pid")
    group.add_argument("--cgroup", help="trace with matching cgroup")
    group.add_argument("--procname", help="trace by matching process command name")
    group.add_argument("--container", help="trace a docker container")
    group.add_argument("--kubernetes__pod", help="trace a kubernetes pod")

    # k8s extras
    parser.add_argument(
        "--kubernetes__container", help="set kubernetes container to trace"
    )
    parser.add_argument(
        "--kubernetes__namespace", help="set the kubernetes pod's namespace"
    )

    return parser
