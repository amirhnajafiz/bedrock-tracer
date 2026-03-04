import argparse
import logging
import signal
import sys

import dependencies.command
import dependencies.kernel
import utils.files
from builder import build_parser
from matchbox import extinguish_tracing, ignite_tracing
from resolver import resolve_mode


def start(args: argparse.Namespace) -> None:
    """Start cli.

    Parameters
    ----------
    args : argparser.Namespace
        Python argparser object that stores user input flags.
    """

    logging.info("starting cli ...")

    # get the handler for the selected tracing mode and run the tracers
    handler = resolve_mode(args)

    # get the tracers to run
    tracers = handler(args)

    logging.debug("prepare to run %d tracers.", len(tracers))

    # bind the termination signals to the extinguish_tracing handler with the tracers to stop
    signal.signal(signal.SIGINT, extinguish_tracing(tracers=tracers))
    signal.signal(signal.SIGTERM, extinguish_tracing(tracers=tracers))

    logging.debug(
        "termination signal handlers are bounded for %s and %s.",
        signal.SIGINT,
        signal.SIGTERM,
    )

    # run the tracers
    ignite_tracing(output_dir=args.out, tracers=tracers)

    logging.info("cli returning with exit code 0.")


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
        dependencies.kernel.ensure_kernel_support()
        dependencies.kernel.ensure_directories()
        dependencies.command.must_support_bpftrace()
    except Exception as e:
        logging.exception(e)
        sys.exit(1)

    # initialize variables
    init_vars(args)

    # export the configurations
    logging.info(f"configs:\n\t{vars(args)}")
    utils.files.write_reader_configs(args.out, vars(args))

    # start the cli
    try:
        start(args)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
