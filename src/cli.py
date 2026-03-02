import argparse
import logging
import signal
import sys
from typing import Any, Callable, List

import dispatch as dp
import utils
import utils.files
from builder import build_parser
from matchbox import extinguish_tracing, ignite_tracing
from tracer import Tracer

# MODE Dispatch maps the cli flags to Python Callables.
# Callables are a part of dispatch.py module. They have `mode_*` prefix
# and accept the argparser parameters to run a Callable based on user input.
_MODE_DISPATCH = {
    "execute": dp.mode_execute,
    "pid": dp.mode_pid,
    "cgroup": dp.mode_cgroup,
    "procname": dp.mode_procname,
    "container": dp.mode_docker,
    "kubernetes__pod": dp.mode_k8s,
}


def run_tracers(args: argparse.Namespace, tracers: List[Tracer]) -> None:
    """Take a list of tracers and start them.

    Run tracers accept a list of tracers type and sets termination handlers before
    passing the tracers to matchbox module.

    Parameters
    ----------
    args : argparser.Namespace
        Python argparser object that stores user input flags.
    tracers : List[Tracer]
        List of tracers that is returned by handler.
    """

    logging.debug("prepare to run %d tracers.", len(tracers))

    signal.signal(signal.SIGINT, extinguish_tracing(tracers=tracers))
    signal.signal(signal.SIGTERM, extinguish_tracing(tracers=tracers))

    logging.debug(
        "termination signal handlers are bounded for %s and %s.",
        signal.SIGINT,
        signal.SIGTERM,
    )

    ignite_tracing(output_dir=args.out, tracers=tracers)


def resolve_mode(args: argparse.Namespace) -> Callable[[Any], List[Tracer]]:
    """Resolve tracer mode.

    Resolve tracing mode using the user input flags and MODE_DISPATCH.

    Parameters
    ----------
    args : argparser.Namespace
        Python argparser object that stores user input flags.

    Returns
    -------
    handler : Callable
        A handler that returns a list of tracers to pass to run_tracers function.

    Raises
    ------
    RuntimeError
        If none of the required flags are set.
    """

    for key, handler in _MODE_DISPATCH.items():
        if getattr(args, key):
            logging.debug("selected %s handler.", key)

            return handler
    raise RuntimeError("no tracing mode selected!")


def start(args: argparse.Namespace) -> None:
    """Start cli.

    Parameters
    ----------
    args : argparser.Namespace
        Python argparser object that stores user input flags.
    """

    handler = resolve_mode(args)
    tracers = handler(args)

    run_tracers(args, tracers)


def init_vars(args: argparse.Namespace) -> None:
    """Initialize variables.

    Sets some global variables such as logger and output directory.

    Parameters
    ----------
    args : argparser.Namespace
        Python argparser object that stores user input flags.
    """

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    )

    # create the output directory
    utils.files.create_dir(args.out)
    logging.debug("output directory %s initialized.", args.out)


def main():
    # build a parser to get input arguments
    parser = build_parser()
    args = parser.parse_args()

    # check system requirements
    try:
        utils.ensure_kernel_support()
        utils.must_support_bpftrace()
    except Exception as e:
        logging.exception(e)
        sys.exit(1)

    # initialize variables
    init_vars(args)

    # export the configurations
    logging.info(f"configs:\n\t{vars(args)}")
    utils.files.write_reader_configs(args.out, vars(args))

    try:
        start(args)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
