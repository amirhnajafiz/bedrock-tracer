import argparse
from typing import List, Optional

import resolver
import utils
from tracer import MonoTracer, RotateTracer, Tracer


def _new_tracer(
    name: str,
    path: str,
    output_dir: str,
    rotate: bool,
    rotate_size: int,
) -> Tracer:
    utils.ensure_script(path)

    if rotate:
        tracer = RotateTracer(name, path, output_dir)
        tracer.with_rotate_size(rotate_size=rotate_size)
    else:
        tracer = MonoTracer(name, path, output_dir)

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

    tracers = []

    scripts = utils.files.get_tracing_scripts(
        script_group,
        disable_vfs=disable_vfs,
        disable_io=disable_io,
        disable_memory_map=disable_memory_map,
        headless=headless,
    )

    for tname, tpath in scripts.items():
        tracer = _new_tracer(tname, tpath, output_dir, rotate, rotate_size)

        if args:
            tracer.with_args(args)

        if options:
            tracer.with_options(options)

        tracers.append(tracer)

    return tracers


def _common_kwargs(args: argparse.Namespace) -> dict:
    return dict(
        output_dir=args.out,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
        disable_vfs=args.disable_vfs,
        disable_io=args.disable_io,
        disable_memory_map=args.disable_memory_map,
        headless=args.headless,
    )


def _build_cgroup_mode(args: argparse.Namespace, cgid: str) -> List[Tracer]:
    if args.procname:
        return _build_tracers(
            script_group="bpftrace/cgroup_and_command",
            args=[cgid, args.procname],
            **_common_kwargs(args),
        )

    return _build_tracers(
        script_group="bpftrace/cgroup",
        args=[cgid],
        **_common_kwargs(args),
    )


def mode_execute(args: argparse.Namespace) -> List[Tracer]:
    return _build_tracers(
        script_group="bpftrace/execute",
        options=["-c", args.execute],
        **_common_kwargs(args),
    )


def mode_pid(args: argparse.Namespace) -> List[Tracer]:
    return _build_tracers(
        script_group="bpftrace/pid",
        args=[args.pid],
        **_common_kwargs(args),
    )


def mode_procname(args: argparse.Namespace) -> List[Tracer]:
    return _build_tracers(
        script_group="bpftrace/command",
        args=[args.procname],
        **_common_kwargs(args),
    )


def mode_cgroup(args: argparse.Namespace) -> List[Tracer]:
    return _build_cgroup_mode(args, args.cgroup)


def mode_docker(args: argparse.Namespace) -> List[Tracer]:
    cgroup = resolver.resolve_docker_container(container_name=args.container)
    return _build_cgroup_mode(args, cgroup)


def mode_k8s(args: argparse.Namespace) -> List[Tracer]:
    cgroup = resolver.resolve_k8s_pod(
        pod=args.kubernetes__pod,
        namespace=args.kubernetes__namespace,
        container_name=args.kubernetes__container,
    )
    return _build_cgroup_mode(args, cgroup)
