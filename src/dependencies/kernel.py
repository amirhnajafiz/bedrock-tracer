import os
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


def ensure_directories():
    """Check if the required directories are existing.

    The required directories are:
    - /sys
    - /lib/modules

    Raises
    ------
    RuntimeError
        If any of the required directories is not existing.
    """

    required_directories = ["/sys", "/lib/modules"]

    for directory in required_directories:
        if not os.path.exists(directory):
            raise RuntimeError(f"required directory '{directory}' not found.")
