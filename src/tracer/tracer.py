import logging
import os
import signal
import subprocess
import threading
import time
from abc import ABC
from typing import List


class Tracer(ABC):
    """Tracer is an abstract class of the tracing logic."""

    def __init__(
        self, tid: str, script: str, output_dir: str, termination_timeout: int = 2
    ):
        """Tracer constructor.

        Parameters
        ----------
        tid : str
            The tracer id for debugging.
        script : str
            The bpftrace script full path.
        output_dir : str
            The output directory to export tracing logs.
        termination_timeout : int
            Tracer termination timeout in seconds.
        """

        self._tid = tid  # tracer id
        self._script = script  # bpftrace script
        self._tto = termination_timeout
        self._output_dir = output_dir

        self._options = []  # bpftrace options
        self._args = []  # bpftrace input arguments
        self._proc = None
        self._proc_lock = threading.Lock()

        self._stop_event = None
        self._t = None

    def with_options(self, options: List[str]) -> None:
        """Add options to the tracer.

        Parameters
        ----------
        options : List
            List of options to append the current options.
        """

        self._options += options

    def with_args(self, args: List[str]) -> None:
        """Add args to the tracer.

        Parameters
        ----------
        args : List
            List of args to append the current args.
        """

        self._args += args

    def start(self) -> None:
        """Start a tracer by calling the __start_tracer in a thread."""

        self._stop_event = threading.Event()
        self._t = threading.Thread(target=self.start_tracer, args=(), daemon=True)
        self._t.start()

        logging.debug(f"[{self._tid}] tracer started in thread {self._t.ident}.")

    def stop(self) -> None:
        """Stop the tracer by terminating its process and thread."""

        if self._stop_event:
            self._stop_event.set()

        self._terminate_process_group()

    def _terminate_process_group(self) -> None:
        """Terminate the tracer process group safely if it exists."""

        with self._proc_lock:
            proc = self._proc

        if not proc or proc.poll() is not None:
            return

        try:
            pgid = os.getpgid(proc.pid)
        except ProcessLookupError:
            return

        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            return

        try:
            proc.wait(timeout=self._tto)
            return
        except subprocess.TimeoutExpired:
            logging.debug(f"[{self._tid}] killing tracer.")

        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            return

        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            logging.error(f"[{self._tid}][ERROR] failed to kill tracer process group.")

    def wait(self, timeout: float = 0.2) -> None:
        """Wait for the tracing process to finish.

        Parameters
        ----------
        timeout : float | None
            Optional timeout in seconds.
        """

        if self._t:
            self._t.join(timeout=timeout)

    def is_alive(self) -> bool:
        """Check whether the tracer thread is alive."""

        return bool(self._t and self._t.is_alive())

    def name(self) -> str:
        """Get the name of the tracer.

        Returns
        -------
        tid : str
            Tracer id.
        """

        return self._tid

    def script_path(self) -> str:
        """Get the tracer script path.

        Returns
        -------
        script : str
            bpftrace script path.
        """

        return self._script

    def start_tracer(self):
        """Start the tracer in a new process and wait until its over or the stop event is received."""

        raise NotImplementedError("start_tracer must be implemented by subclasses.")


class MonoTracer(Tracer):
    """MonoTracer runs a single bpftrace script and exports the logs into one file."""

    def start_tracer(self) -> None:
        """Start tracer in a new process and wait until its over or the stop event is received."""

        # set output file option
        self.with_options(["-o", os.path.join(self._output_dir, "trace_0.log")])

        # create the bpftrace command
        bt_command = ["bpftrace"] + self._options + [self._script] + self._args
        logging.debug(
            "[{}] starting tracer: {}".format(self._tid, " ".join(bt_command))
        )

        try:
            # run a new process
            with self._proc_lock:
                self._proc = subprocess.Popen(
                    bt_command,
                    start_new_session=True,
                )

            while self._proc.poll() is None:
                # stop is requested
                if self._stop_event.is_set():
                    logging.debug(f"[{self._tid}] stopping tracer.")
                    self._terminate_process_group()

                    return

                time.sleep(0.5)

        except Exception as e:
            logging.error(f"[{self._tid}] failed: {e}")

        finally:
            self._terminate_process_group()

            logging.debug(f"[{self._tid}] exiting tracer")
