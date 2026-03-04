import logging
import os
import subprocess
import time

from . import Tracer


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
            logging.error(f"[{self._tid}] tracer failed: {e}")

        finally:
            self._terminate_process_group()

            logging.debug(f"[{self._tid}] exiting tracer")
