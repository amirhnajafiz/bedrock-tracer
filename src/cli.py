import argparse
import logging
import os
import signal
import sys

import handlers as hd
from containers import container_cgroup_id, container_cgroup_id_from_pid
from containers.docker import docker_container_pid
from containers.kubernetes import pod_container_id
from matchbox import extinguish_tracing, ignite_tracing
from utils import must_support_bpftrace


def start(args: argparse.Namespace):
    tracers = []

    logging.debug("start processing input arguments")

    # build the tracers based on input arguments
    if args.execute:
        tracers = hd.handle_execute(
            output_dir=args.out, 
            execute=args.execute, 
            rotate=args.rotate, 
            rotate_size=args.rotate_size
        )

        logging.debug("execute tracers built")
    elif args.pid:
        tracers = hd.handle_pid(
            output_dir=args.out, 
            pid=args.pid, 
            rotate=args.rotate, 
            rotate_size=args.rotate_size
        )

        logging.debug("pid tracers built")
    elif args.cgroup:
        if args.procname:
            tracers = hd.handle_cgroup_and_command(
                output_dir=args.out, 
                cgid=args.cgroup, 
                filter_command=args.procname, 
                rotate=args.rotate, 
                rotate_size=args.rotate_size
            )
        else:
            tracers = hd.handle_cgroup(
                output_dir=args.out, 
                cgid=args.cgroup, 
                rotate=args.rotate, 
                rotate_size=args.rotate_size
            )
        
        logging.debug("cgroup tracers built")
    elif args.docker_container:
        # get container pid
        container_pid, err = docker_container_pid(args.docker_container)
        if len(err) > 0:
            logging.error(err)
            sys.exit(1)

        logging.debug(f"found container pid: {container_pid}")

        # get cgroup from pid
        cgroup, err = container_cgroup_id_from_pid(container_pid)
        if len(err) > 0:
            logging.error(err)
            sys.exit(1)

        logging.debug(f"found container cgroup: {cgroup}")

        if args.procname:
            tracers = hd.handle_cgroup_and_command(
                output_dir=args.out, 
                cgid=cgroup, 
                filter_command=args.procname, 
                rotate=args.rotate, 
                rotate_size=args.rotate_size
            )
        else:
            tracers = hd.handle_cgroup(
                output_dir=args.out, 
                cgid=cgroup, 
                rotate=args.rotate, 
                rotate_size=args.rotate_size
            )
        
        logging.debug("cgroup tracers built")
    elif args.k8s_pod:
        container_id, err = pod_container_id(
            namespace=args.k8s_namespace, 
            pod=args.k8s_pod, 
            container_name=args.k8s_container
        )
        if len(err) > 0:
            logging.error(err)
            sys.exit(1)

        logging.debug(f"found container id: {container_id}")

        cgroup, err = container_cgroup_id(container_id)
        if len(err) > 0:
            logging.error(err)
            sys.exit(1)

        logging.debug(f"found container cgroup: {cgroup}")

        if args.procname:
            tracers = hd.handle_cgroup_and_command(
                output_dir=args.out, 
                cgid=cgroup, 
                filter_command=args.procname, 
                rotate=args.rotate, 
                rotate_size=args.rotate_size
            )
        else:
            tracers = hd.handle_cgroup(
                output_dir=args.out, 
                cgid=cgroup, 
                rotate=args.rotate, 
                rotate_size=args.rotate_size
            )
        
        logging.debug("cgroup tracers built")
    elif args.procname:
        tracers = hd.handle_command(
            output_dir=args.out, 
            command=args.procname, 
            rotate=args.rotate, 
            rotate_size=args.rotate_size
        )

        logging.debug("procname tracers built")
    else:
        logging.error("must run with --[execute|pid|cgroup|container|pod|procname]")
        sys.exit(0)

    # set the termination handlers
    signal.signal(signal.SIGINT, extinguish_tracing(tracers=tracers))
    signal.signal(signal.SIGTERM, extinguish_tracing(tracers=tracers))

    # start tracers
    ignite_tracing(output_dir=args.out, tracers=tracers)


def init_vars(args: argparse.Namespace):
    os.environ["BPFTRACE_MAX_STRLEN"] = args.max_str_len
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    )


def main():
    # create an argument parser
    parser = argparse.ArgumentParser(
        description="Bedrock tracer is ebpf-based file access pattern tracing tool."
    )

    # flags
    parser.add_argument(
        "-o",
        "--out",
        default="logs",
        help="directory path to export the tracing logs [default ./logs]",
    )
    parser.add_argument(
        "-m",
        "--max_str_len",
        default="150",
        help="bpftrace maximum string length in bytes [default 150]",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="displaying debug messages",
    )
    parser.add_argument(
        "-r",
        "--rotate",
        action="store_true",
        help="enable log rotation to chunk tracing output files",
    )
    parser.add_argument(
        "-s",
        "--rotate_size",
        type=int,
        default=100 * 1024 * 1024,
        help="log rotation rotate size [default 100MB]",
    )

    # regular tracing options
    parser.add_argument("--execute", help="execute a command and start tracing it")
    parser.add_argument(
        "--pid",
        help="trace an existing process using its PID (must be in running state)",
    )
    parser.add_argument(
        "--cgroup",
        help="trace processes with matching cgroup ID (must be a valid cgroup)",
    )
    parser.add_argument(
        "--procname",
        help="filter based on procname (works with cgroups, container, kubernetes, or itself)",
    )

    # docker tracing options
    parser.add_argument("--docker_container", help="docker container name to trace")

    # kubernetes tracing options
    parser.add_argument("--k8s_pod", help="kubernetes pod's name to trace")
    parser.add_argument(
        "--k8s_container", help="kubernetes pod's container name"
    )
    parser.add_argument(
        "--k8s_namespace", help="kubernetes pod's namespace"
    )

    # parse the arguments
    args = parser.parse_args()

    # must support bpftrace
    must_support_bpftrace()

    # init variables
    init_vars(args=args)

    logging.info(f"configs:\n\t{vars(args)}")

    # start processing the input
    start(args=args)
