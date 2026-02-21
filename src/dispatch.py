import argparse
from typing import List

import handlers as hd
from resolver import resolve_docker, resolve_k8s
from tracer import Tracer


def _build_cgroup_tracers(args: argparse.Namespace, cgid: str) -> List[Tracer]:
    if args.procname:
        return hd.handle_cgroup_and_command(
            output_dir=args.out,
            cgid=cgid,
            filter_command=args.procname,
            rotate=args.rotate,
            rotate_size=args.rotate_size,
            no_memory_trace=args.no_memory_trace,
            quiet_mode=args.quiet_mode,
        )

    return hd.handle_cgroup(
        output_dir=args.out,
        cgid=cgid,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
        no_memory_trace=args.no_memory_trace,
        quiet_mode=args.quiet_mode,
    )


def mode_execute(args: argparse.Namespace) -> List[Tracer]:
    return hd.handle_execute(
        output_dir=args.out,
        execute=args.execute,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
        no_memory_trace=args.no_memory_trace,
        quiet_mode=args.quiet_mode,
    )


def mode_pid(args: argparse.Namespace) -> List[Tracer]:
    return hd.handle_pid(
        output_dir=args.out,
        pid=args.pid,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
        no_memory_trace=args.no_memory_trace,
        quiet_mode=args.quiet_mode,
    )


def mode_cgroup(args: argparse.Namespace) -> List[Tracer]:
    return _build_cgroup_tracers(args, args.cgroup)


def mode_docker(args: argparse.Namespace) -> List[Tracer]:
    cgroup = resolve_docker(args.docker_container)
    return _build_cgroup_tracers(args, cgroup)


def mode_k8s(args: argparse.Namespace) -> List[Tracer]:
    cgroup = resolve_k8s(args)
    return _build_cgroup_tracers(args, cgroup)


def mode_procname(args: argparse.Namespace) -> List[Tracer]:
    return hd.handle_command(
        output_dir=args.out,
        command=args.procname,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
        no_memory_trace=args.no_memory_trace,
        quiet_mode=args.quiet_mode,
    )
