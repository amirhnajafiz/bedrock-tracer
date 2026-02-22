import argparse
from typing import List, Optional

from resolver import resolve_docker, resolve_k8s
from tracer import MonoTracer, RotateTracer, Tracer
from utils import ensure_script
from utils.files import get_tracing_scripts

### helper functions ###


def _new_tracer(
    name: str,
    path: str,
    output_dir: str,
    rotate: bool,
    rotate_size: int,
) -> Tracer:
    ensure_script(path)

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
    memory_trace: bool = False,
    headless: bool = False,
) -> List[Tracer]:

    tracers = []

    scripts = get_tracing_scripts(
        script_group,
        memory_trace=memory_trace,
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
        memory_trace=args.memory_trace,
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


### main functions ###


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
    cgroup = resolve_docker(args.docker_container)
    return _build_cgroup_mode(args, cgroup)


def mode_k8s(args: argparse.Namespace) -> List[Tracer]:
    cgroup = resolve_k8s(args)
    return _build_cgroup_mode(args, cgroup)
