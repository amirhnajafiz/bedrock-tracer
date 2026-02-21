import argparse
import logging
import os
import signal
import sys
from typing import Any, Callable, List

import dispatch as dp
from builder import build_parser
from matchbox import extinguish_tracing, ignite_tracing
from tracer import Tracer
from utils import must_support_bpftrace

# mode dispatch map
MODE_DISPATCH = {
    "execute": dp.mode_execute,
    "pid": dp.mode_pid,
    "cgroup": dp.mode_cgroup,
    "docker_container": dp.mode_docker,
    "k8s_pod": dp.mode_k8s,
    "procname": dp.mode_procname,
}


def run_tracers(args: argparse.Namespace, tracers: List[Tracer]) -> None:
    logging.debug(f"prepare to run {len(tracers)} tracers.")

    signal.signal(signal.SIGINT, extinguish_tracing(tracers=tracers))
    signal.signal(signal.SIGTERM, extinguish_tracing(tracers=tracers))

    logging.debug("term signal handlers bounded.")

    ignite_tracing(output_dir=args.out, tracers=tracers)


def resolve_mode(args: argparse.Namespace) -> Callable[[Any], List[Tracer]]:
    logging.debug("resolving mode")

    for key, handler in MODE_DISPATCH.items():
        if getattr(args, key):
            return handler
    raise RuntimeError("no tracing mode selected")


def start(args: argparse.Namespace) -> None:
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
    # build a parser and get input arguments
    parser = build_parser()
    args = parser.parse_args()

    # check system requirements
    must_support_bpftrace()

    # initialize variables
    init_vars(args)

    logging.info(f"configs:\n\t{vars(args)}")

    try:
        start(args)
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
