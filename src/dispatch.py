import argparse

import handlers as hd
from resolver import resolve_docker, resolve_k8s


def _build_cgroup_tracers(args: argparse.Namespace, cgid: str):
    if args.procname:
        return hd.handle_cgroup_and_command(
            output_dir=args.out,
            cgid=cgid,
            filter_command=args.procname,
            rotate=args.rotate,
            rotate_size=args.rotate_size,
        )

    return hd.handle_cgroup(
        output_dir=args.out,
        cgid=cgid,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
    )


def mode_execute(args):
    return hd.handle_execute(
        output_dir=args.out,
        execute=args.execute,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
    )


def mode_pid(args):
    return hd.handle_pid(
        output_dir=args.out,
        pid=args.pid,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
    )


def mode_cgroup(args):
    return _build_cgroup_tracers(args, args.cgroup)


def mode_docker(args):
    cgroup = resolve_docker(args.docker_container)
    return _build_cgroup_tracers(args, cgroup)


def mode_k8s(args):
    cgroup = resolve_k8s(args)
    return _build_cgroup_tracers(args, cgroup)


def mode_procname(args):
    return hd.handle_command(
        output_dir=args.out,
        command=args.procname,
        rotate=args.rotate,
        rotate_size=args.rotate_size,
    )
