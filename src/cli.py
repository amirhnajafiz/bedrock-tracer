import argparse
import datetime
import logging
import os
import signal
import subprocess
import threading
import time
from typing import Callable, List

import dependencies.command
import dependencies.kernel
import utils.files
from builder import build_parser
from resolver import resolve_mode
from tracer.tracer import Tracer
from utils.timestamp import export_reference_timestamps


def _find_bpftrace_processes_for_scripts(scripts: List[str]) -> List[tuple[int, str]]:
    """Find running bpftrace processes matching the tracer scripts.

    Parameters
    ----------
    scripts : List[str]
        List of bpftrace script paths to match.

    Returns
    -------
    processes : List[tuple[int, str]]
        List of tuples containing the PID and command of matching bpftrace processes.
    """

    if not scripts:
        return []

    # run ps command to get all processes with their command lines
    result = subprocess.run(
        ["ps", "-axo", "pid=,command="],
        capture_output=True,
        text=True,
        check=False,
    )

    # if the command failed, return empty list
    if result.returncode != 0:
        return []

    # parse the output and filter for bpftrace processes that match the scripts
    processes = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue

        try:
            pid = int(parts[0])
        except ValueError:
            continue

        cmd = parts[1]
        if "bpftrace" not in cmd:
            continue

        if any(script in cmd for script in scripts):
            processes.append((pid, cmd))

    return processes


def _force_cleanup_bpftrace(tracers: List[Tracer]) -> None:
    """Force cleanup any residual bpftrace process that belongs to current tracers.

    Parameters
    ----------
    tracers : List[Tracer]
        List of tracers to find the corresponding bpftrace processes.
    """

    # get the script paths from the tracers to find the corresponding bpftrace processes
    scripts = [os.path.abspath(tracer.script_path()) for tracer in tracers]
    leftovers = _find_bpftrace_processes_for_scripts(scripts)

    # first try to terminate the processes gracefully with SIGTERM
    for pid, cmd in leftovers:
        logging.warning("force-terminating residual bpftrace (pid=%d): %s", pid, cmd)
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue

    if leftovers:
        time.sleep(0.2)

    # if there are still leftovers, force-kill them with SIGKILL
    leftovers = _find_bpftrace_processes_for_scripts(scripts)
    for pid, cmd in leftovers:
        logging.error("force-killing residual bpftrace (pid=%d): %s", pid, cmd)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            continue


def _shutdown_wrapper(
    tracers: List[Tracer], shutdown_event: threading.Event
) -> Callable:
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
        shutdown_event.set()

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
    shutdown_event = threading.Event()

    logging.debug("prepare to run %d tracers.", len(tracers))

    # bind the termination signals to the stop handler with the tracers to stop
    signal.signal(
        signal.SIGINT,
        _shutdown_wrapper(tracers=tracers, shutdown_event=shutdown_event),
    )
    signal.signal(
        signal.SIGTERM,
        _shutdown_wrapper(tracers=tracers, shutdown_event=shutdown_event),
    )

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

    # wait for tracers to finish or termination signal to stop them
    shutdown_deadline = None
    while True:
        running = False
        for tracer in tracers:
            tracer.wait(timeout=0.2)
            if tracer.is_alive():
                running = True

        if not running:
            break

        if not shutdown_event.is_set():
            continue

        if shutdown_deadline is None:
            shutdown_deadline = time.time() + 5

        for tracer in tracers:
            tracer.stop()

        if time.time() >= shutdown_deadline:
            alive = [tracer.name() for tracer in tracers if tracer.is_alive()]
            if alive:
                logging.error(
                    "shutdown timeout while waiting for tracer threads: %s", alive
                )
            break

    # force cleanup any residual bpftrace processes that belongs to current tracers
    _force_cleanup_bpftrace(tracers)

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
