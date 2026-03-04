import argparse
import logging
from typing import Any, Callable, List

import dispatch as dp
from tracer.tracer import Tracer

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
