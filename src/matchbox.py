import logging
from typing import Callable, List

from tracer import Tracer
from utils.timestamp import export_reference_timestamps


def ignite_tracing(output_dir: str, tracers: List[Tracer]) -> None:
    """Start the tracers.

    Parameters
    ----------
    output_dir : str
        The output directory to store tracing results.
    tracers : List[Tracer]
        List of tracers to run.
    """

    # store the reference timestamps to convert raw clock numbers to datetime
    export_reference_timestamps(output_dir)

    # loop over tracers and start
    for tracer in tracers:
        logging.info(f"starting {tracer.name()} ...")
        tracer.start()

    logging.info("all tracers started.")

    # wait for all tracers
    for tracer in tracers:
        tracer.wait()

    logging.info("passing all waits.")


def extinguish_tracing(tracers: List[Tracer]) -> Callable:
    """Stop all tracers.

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

        logging.info("all tracers stopped.")

    return handle_shutdown
