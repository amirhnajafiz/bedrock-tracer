import argparse
import logging
import os
from typing import List, Optional

import dependencies.command
import dependencies.cri
import dependencies.path
import utils.files
import utils.units
from containers import cgroup_id_from_container_id, cgroup_id_from_pid
from containers.docker import container_pid
from containers.kubernetes import container_uid
from tracer import Tracer, import_tracing_scripts
from tracer.mono import MonoTracer
from tracer.rotation import RotateTracer


def _new_tracer(
    name: str,
    path: str,
    output_dir: str,
    rotate: bool,
    rotate_size: int,
) -> Tracer:
    """New tracer instance.

    Builds and returns a new tracer.

    Parameters
    ----------
    name : str
        Tracer name.
    path : str
        Tracer bpftrace script path.
    output_dir : str
        Tracer output logs directory path.
    rotate : bool
        Return a RotateTracer or MonoTracer.
    rotate_size : int
        RotateTracer log rotation size.

    Returns
    -------
    tracer : Tracer
        A RotateTracer or MonoTracer.

    Raises
    ------
    RuntimeError
        If the bpftrace script path doesn't exists.
    """

    logging.debug("searching for %s script.", path)

    # ensure the bpftrace script path exists
    dependencies.path.ensure_script(path)

    # create tracer output directory
    tracer_output_dir = os.path.join(output_dir, name)
    utils.files.create_dir(tracer_output_dir)

    logging.debug("tracer output directory: %s.", tracer_output_dir)

    # build tracer
    if rotate:
        tracer = RotateTracer(name, path, tracer_output_dir)
        tracer.with_rotate_size(rotate_size=rotate_size)
    else:
        tracer = MonoTracer(name, path, tracer_output_dir)

    logging.debug("rotate tracer created." if rotate else "mono tracer created.")

    return tracer


def _build_tracers(
    *,
    script_group: str,
    output_dir: str,
    args: Optional[List[str]] = None,
    options: Optional[List[str]] = None,
    rotate: bool = False,
    rotate_size: int = 100 * 1024 * 1024,
    disable_vfs: bool = False,
    disable_io: bool = False,
    disable_memory_map: bool = False,
    headless: bool = False,
) -> List[Tracer]:
    """Build and return tracers.

    Parse the input arguments, build, and return tracer instances.

    Parameters
    ----------
    script_group : str
        The bpftrace scripts directory and subdirectory.
    output_dir : str
        Tracer logs output directory.
    args : Optional[List[str]]
        Tracer arguments.
    options : Optional[List[str]]
        Tracer flags/options.
    rotate : bool
        Enable rotation.
    rotate_size : int
        Rotation size.
    disable_vfs : bool
        Disable VFS tracer.
    disable_io : bool
        Disable IO tracer.
    disable_memory_map : bool
        Disable memory map tracer.
    headless : bool
        Headless tracing mode.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances.
    """

    tracers = []

    # get tracing scripts
    scripts = import_tracing_scripts(
        script_group,
        disable_vfs=disable_vfs,
        disable_io=disable_io,
        disable_memory_map=disable_memory_map,
        headless=headless,
    )

    # build tracers
    for tname, tpath in scripts.items():
        logging.debug("building tracer for %s : %s", tname, tpath)

        tracer = _new_tracer(tname, tpath, output_dir, rotate, rotate_size)

        if args:
            tracer.with_args(args)

        if options:
            tracer.with_options(options)

        tracers.append(tracer)

    return tracers


def _common_kwargs(args: argparse.Namespace) -> dict:
    """Common keyword arguments for tracer builders.

    Parse and return common keyword arguments for tracer builders.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.

    Returns
    -------
    kwargs : dict
        Common keyword arguments for tracer builders.

    """

    # parse rotation size
    rs = utils.units.parse_bytes(args.rotate_size)

    return dict(
        output_dir=args.out,
        rotate=args.rotate,
        rotate_size=rs,
        disable_vfs=args.disable_vfs,
        disable_io=args.disable_io,
        disable_memory_map=args.disable_memory_map,
        headless=args.headless,
    )


def _build_cgroup_mode(args: argparse.Namespace, cgid: str) -> List[Tracer]:
    """Build and return tracers for cgroup mode.

    Parse the input arguments, build, and return tracer instances for cgroup mode.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.
    cgid : str
        Cgroup ID.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances for cgroup mode.
    """

    if args.filter:
        return _build_tracers(
            script_group=os.path.join("bpftrace", "cgroup_and_command", args.version),
            args=[cgid, args.filter],
            **_common_kwargs(args),
        )

    return _build_tracers(
        script_group=os.path.join("bpftrace", "cgroup", args.version),
        args=[cgid],
        **_common_kwargs(args),
    )


def mode_execute(args: argparse.Namespace) -> List[Tracer]:
    """Build and return tracers for execute mode.

    Parse the input arguments, build, and return tracer instances for execute mode.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances for execute mode.
    """

    return _build_tracers(
        script_group=os.path.join("bpftrace", "execute", args.version),
        options=["-c", args.execute],
        **_common_kwargs(args),
    )


def mode_pid(args: argparse.Namespace) -> List[Tracer]:
    """Build and return tracers for PID mode.

    Parse the input arguments, build, and return tracer instances for PID mode.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances for PID mode.
    """

    return _build_tracers(
        script_group=os.path.join("bpftrace", "pid", args.version),
        args=[args.pid],
        **_common_kwargs(args),
    )


def mode_procname(args: argparse.Namespace) -> List[Tracer]:
    """Build and return tracers for process name mode.

    Parse the input arguments, build, and return tracer instances for process name mode.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances for process name mode.
    """

    return _build_tracers(
        script_group=os.path.join("bpftrace", "command", args.version),
        args=[args.procname],
        **_common_kwargs(args),
    )


def mode_cgroup(args: argparse.Namespace) -> List[Tracer]:
    """Build and return tracers for cgroup mode.

    Parse the input arguments, build, and return tracer instances for cgroup mode.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances for cgroup mode.
    """

    return _build_cgroup_mode(args, args.cgroup)


def mode_docker(args: argparse.Namespace) -> List[Tracer]:
    """Build and return tracers for Docker mode.

    Parse the input arguments, build, and return tracer instances for Docker mode.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances for Docker mode.
    """

    # ensure Docker is available
    dependencies.command.must_support_docker()
    dependencies.cri.ensure_docker_env()

    # extract container arguments
    container_name = args.container

    # resolve container pid
    pid = container_pid(container=container_name)
    logging.debug("container %s has pid %s.", container_name, pid)

    # resolve cgroup from pid
    cgroup = cgroup_id_from_pid(pid)
    logging.debug("container %s has cgroup %s.", container_name, cgroup)

    return _build_cgroup_mode(args, cgroup)


def mode_k8s(args: argparse.Namespace) -> List[Tracer]:
    """Build and return tracers for Kubernetes mode.

    Parse the input arguments, build, and return tracer instances for Kubernetes mode.

    Parameters
    ----------
    args : argparse.Namespace
        The input arguments.

    Returns
    -------
    tracers : List[Tracer]
        A list of tracer instances for Kubernetes mode.
    """

    # ensure Kubernetes is available
    dependencies.command.must_support_crictl()
    dependencies.cri.ensure_kubernetes_env()

    # extract kubernetes arguments
    namespace = args.kubernetes__namespace
    pod = args.kubernetes__pod
    container_name = args.kubernetes__container

    # resolve container uid
    container_id = container_uid(
        namespace=namespace,
        pod=pod,
        container_name=container_name,
    )
    logging.debug("container %s has uuid %s.", args.kubernetes__container, container_id)

    # resolve cgroup from container uid
    cgroup = cgroup_id_from_container_id(container_id)
    logging.debug("container %s has cgroup %s.", args.kubernetes__container, cgroup)

    return _build_cgroup_mode(args, cgroup)
