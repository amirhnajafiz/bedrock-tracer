import shutil


def must_support_bpftrace():
    """Check if bpftrace is supported.

    Raises
    -----
    RuntimeError
        If bpftrace is not installed.
    """

    if shutil.which("bpftrace") is None:
        raise RuntimeError("bpftrace not found in PATH. Please install bpftrace.")


def must_support_docker():
    """Check if Docker is supported.

    Raises
    -----
    RuntimeError
        If Docker is not installed.
    """

    if shutil.which("docker") is None:
        raise RuntimeError("Docker not found in PATH. Please install Docker.")


def must_support_crictl():
    """Check if crictl is supported.

    Raises
    -----
    RuntimeError
        If crictl is not installed.
    """

    if shutil.which("crictl") is None:
        raise RuntimeError("crictl not found in PATH. Please install crictl.")
