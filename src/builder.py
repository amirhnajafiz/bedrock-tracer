import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bedrock tracer is ebpf-based file access pattern tracing tool."
    )

    # common flags
    parser.add_argument("-o", "--out", default="logs")
    parser.add_argument("-m", "--max_str_len", default="150")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-r", "--rotate", action="store_true")
    parser.add_argument("-q", "--quiet_mode", action="store_true")
    parser.add_argument("-n", "--no_memory_trace", action="store_true")
    parser.add_argument(
        "-s",
        "--rotate_size",
        type=int,
        default=100 * 1024 * 1024,
    )

    # mutually exclusive tracing modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--execute")
    group.add_argument("--pid")
    group.add_argument("--cgroup")
    group.add_argument("--docker_container")
    group.add_argument("--k8s_pod")
    group.add_argument("--procname")

    # k8s extras
    parser.add_argument("--k8s_container")
    parser.add_argument("--k8s_namespace")

    return parser
