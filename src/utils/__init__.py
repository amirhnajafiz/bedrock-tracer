import os
import shutil
import subprocess


def ensure_kernel_support():
    """Check if the kernel supports eBPF.

    Check if the kernel supports eBPF by running /usr/local/bedrock/kernel_support.sh.
    This script checks all the needed kernel features for Bedrock to work properly.

    Raises
    ------
    RuntimeError
        If the kernel does not support eBPF or if the support check script is not found.
    """

    possible_directories = ["/usr/local/bedrock", "bpftrace"]

    script_path = None
    for d in possible_directories:
        script_path = os.path.join(d, "kernel_support.sh")
        if os.path.exists(script_path):
            break

    if not os.path.exists(script_path):
        raise RuntimeError(f"kernel support script '{script_path}' not found.")

    result = subprocess.run([script_path], capture_output=True, text=True)
    if result.returncode != 0:
        output = result.stdout.strip()
        error = result.stderr.strip()
        raise RuntimeError(f"kernel support check failed: \n{output}\n{error}")


def must_support_bpftrace():
    """Check if bpftrace is supported.

    Raises
    -----
    RuntimeError
        If bpftrace is not installed.
    """

    if shutil.which("bpftrace") is None:
        raise RuntimeError("bpftrace not found in PATH. Please install bpftrace.")


def ensure_script(path: str):
    """Check if the target script exists.

    Parameters
    ----------
    path : str
        The target script path.

    Raises
    ------
    RuntimeError
        If the script file is not found.
    """

    if not os.path.isfile(path):
        raise RuntimeError(f"required script '{path}' not found.")
