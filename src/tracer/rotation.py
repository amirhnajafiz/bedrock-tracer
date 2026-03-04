import logging
import os
import select
import subprocess

from . import Tracer


class RotateTracer(Tracer):
    """RotateTracer runs a single bpftrace script and exports the logs using a log rotation method."""

    def with_rotate_size(
        self,
        rotate_size: int = 100 * 1024 * 1024,
    ) -> None:
        """With rotate size limit (default is 100Mb per file).

        Parameters
        ----------
        rotate_size : int
            The file size for rotate.
        """

        # rotate parameters
        self._rotate_size = rotate_size
        self._file_index = 0
        self._current_size = 0

        # file handle
        self._f = None

    def __open_new_file(self) -> None:
        """Rotate output file."""

        # close previous file if exists
        if self._f:
            self._f.close()

        filename = os.path.join(self._output_dir, f"trace_{self._file_index}.log")
        logging.info(f"[{self._tid}] rotating to {filename}.")

        # open new file
        self._f = open(filename, "w", buffering=1)
        self._current_size = 0
        self._file_index += 1

    def __write_line(self, line: str) -> None:
        """Write a single line.

        Parameters
        ----------
        line : str
            The input line to write into the file.
        """

        data = line.encode()

        # check if we need to rotate before writing the line
        if self._current_size + len(data) > self._rotate_size:
            self.__open_new_file()

        # write the line and update the current size
        self._f.write(line)
        self._f.flush()
        self._current_size += len(data)

    def start_tracer(self) -> None:
        """Start bpftrace and rotate logs while reading stdout."""

        # build bpftrace command
        bt_cmd = ["bpftrace"] + self._options + [self._script] + self._args
        logging.debug(f"[{self._tid}] starting tracer: {' '.join(bt_cmd)}")

        # setup first output file
        self.__open_new_file()

        try:
            # start bpftrace process with unbuffered output
            with self._proc_lock:
                self._proc = subprocess.Popen(
                    ["stdbuf", "-oL", "-eL"] + bt_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    start_new_session=True,
                )

            # read until process ends or stop requested
            while True:
                # stop is requested
                if self._stop_event.is_set():
                    logging.debug(f"[{self._tid}] stopping tracer.")
                    self._terminate_process_group()

                    break

                # use select to wait for output with a timeout, allowing us to check the stop event periodically
                rlist, _, _ = select.select(
                    [self._proc.stdout, self._proc.stderr], [], [], 0.1
                )

                for stream in rlist:
                    line = stream.readline()
                    if not line:
                        continue  # EOF or no data, continue to check for stop event

                    if stream == self._proc.stdout:
                        self.__write_line(line)
                    else:
                        logging.warning(f"[{self._tid}] tracer stderr:\n{line.strip()}")

                # check if the process has ended
                if self._proc.poll() is not None:
                    # process has ended, read remaining output
                    for line in self._proc.stdout:
                        self.__write_line(line)
                    for line in self._proc.stderr:
                        logging.warning(f"[{self._tid}] tracer stderr:\n{line.strip()}")
                    break

        except Exception as e:
            logging.error(f"[{self._tid}] tracer failed: {e}")

        finally:
            # ensure the process is terminated and file is closed
            self._terminate_process_group()

            if self._f:
                self._f.close()

            logging.debug(f"[{self._tid}] exiting tracer.")
