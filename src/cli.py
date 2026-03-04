import argparse
import datetime
import logging
import os
import signal
from typing import Callable, List

import dependencies.command
import dependencies.kernel
import utils.files
from builder import build_parser
from resolver import resolve_mode
from tracer import Tracer
from utils.timestamp import export_reference_timestamps


def _shutdown_wrapper(tracers: List[Tracer]) -> Callable:
    """Shutdown wrapper.

    Returns a function that can be used as a signal handler to stop the tracers gracefully.

    Parameters
    ----------
    tracers : List[Tracer]
        List of running tracers.

    Returns
    -------
    handle_shutdown : Callable
        The termination function.
    """

    # return a handle_shutdown function to bind it to termination signals
    def handle_shutdown(signum, _):
        if signum is not None:
            logging.info(f"received signal {signum}, shutting down safely ...")

        # loop over tracers and stop them
        for tracer in tracers:
            logging.info(f"stopping {tracer.name()} ...")
            tracer.stop()

        logging.info("all tracers stopped gracefully.")

    return handle_shutdown


def _start(args: argparse.Namespace) -> None:
    """Start cli.

    Parameters
    ----------
    args : argparser.Namespace
        Python argparser object that stores user input flags.
    """

    logging.info("cli started.")

    # get the handler for the selected tracing mode and run the tracers
    handler = resolve_mode(args)

    # get the tracers to run
    tracers = handler(args)

    logging.debug("prepare to run %d tracers.", len(tracers))

    # bind the termination signals to the stop handler with the tracers to stop
    signal.signal(signal.SIGINT, _shutdown_wrapper(tracers=tracers))
    signal.signal(signal.SIGTERM, _shutdown_wrapper(tracers=tracers))

    logging.debug(
        "termination signal handlers are bounded for %s and %s.",
        signal.SIGINT,
        signal.SIGTERM,
    )

    # store the reference timestamps to convert raw clock numbers to datetime
    export_reference_timestamps(args.out)

    # loop over tracers and start
    for tracer in tracers:
        logging.info(f"starting {tracer.name()} ...")
        tracer.start()

    logging.info("all tracers started.")

    # wait for all tracers
    for tracer in tracers:
        tracer.wait()

    logging.info("cli finished.")


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

    # reset the args.out by adding the timestamp to the path
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    args.out = os.path.join(args.out, timestamp)

    # create the output directory
    utils.files.create_dir(args.out)
    logging.debug("output directory %s initialized.", args.out)


def main() -> int:
    # build a parser to get input arguments
    parser = build_parser()
    args = parser.parse_args()

    try:
        # check system requirements
        dependencies.kernel.ensure_kernel_support()
        dependencies.kernel.ensure_directories()
        dependencies.command.must_support_bpftrace()

        # initialize variables
        init_vars(args)

        # export the configurations
        logging.info(f"configs:\n\t{vars(args)}")
        utils.files.write_reader_configs(args.out, vars(args))

        # start the cli
        _start(args)

    except Exception as e:
        logging.exception(e)
        return 1

    finally:
        logging.info("exiting.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
