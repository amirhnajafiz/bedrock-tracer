import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bedrock tracer is ebpf-based file access pattern tracing tool."
    )

    # common flags
    parser.add_argument(
        "-o", "--out", default="logs", help="output directory (default ./logs)"
    )
    parser.add_argument(
        "--max_str_len",
        default="150",
        help="ebpf maximum string lenght (default 150)",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logs")
    parser.add_argument(
        "-r", "--rotate", action="store_true", help="enable log rotation"
    )
    parser.add_argument(
        "--headless", action="store_true", help="enable headless tracing mode (not capturing metadata)"
    )
    parser.add_argument(
        "--memory_trace", action="store_true", help="enable memory map tracer"
    )
    parser.add_argument(
        "--rotate_size",
        type=int,
        default=100 * 1024 * 1024,
        help="log rotation size (default 100MB)",
    )

    # mutually exclusive tracing modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--execute", help="execute and trace")
    group.add_argument("--pid", help="trace an existing pid")
    group.add_argument("--cgroup", help="trace with matching cgroup")
    group.add_argument("--docker_container", help="trace docker container")
    group.add_argument("--k8s_pod", help="trace kubernetes pod")
    group.add_argument("--procname", help="trace by matching process command name")

    # k8s extras
    parser.add_argument("--k8s_container", help="set kubernetes container to trace")
    parser.add_argument("--k8s_namespace", help="set the kubernetes pod's namespace")

    return parser
