import argparse
import logging
import os
import signal
import sys

import dispatch as dp
from builder import build_parser
from matchbox import extinguish_tracing, ignite_tracing
from utils import must_support_bpftrace

MODE_DISPATCH = {
    "execute": dp.mode_execute,
    "pid": dp.mode_pid,
    "cgroup": dp.mode_cgroup,
    "docker_container": dp.mode_docker,
    "k8s_pod": dp.mode_k8s,
    "procname": dp.mode_procname,
}


def run_tracers(args, tracers):
    signal.signal(signal.SIGINT, extinguish_tracing(tracers=tracers))
    signal.signal(signal.SIGTERM, extinguish_tracing(tracers=tracers))
    ignite_tracing(output_dir=args.out, tracers=tracers)


def resolve_mode(args: argparse.Namespace):
    for key, handler in MODE_DISPATCH.items():
        if getattr(args, key):
            return handler
    raise RuntimeError("no tracing mode selected")


def start(args: argparse.Namespace):
    logging.debug("processing input arguments")

    handler = resolve_mode(args)
    tracers = handler(args)

    run_tracers(args, tracers)


def init_vars(args: argparse.Namespace):
    os.environ["BPFTRACE_MAX_STRLEN"] = args.max_str_len
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    )


def main():
    parser = build_parser()
    args = parser.parse_args()

    must_support_bpftrace()
    init_vars(args)

    logging.info(f"configs:\n\t{vars(args)}")

    try:
        start(args)
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
