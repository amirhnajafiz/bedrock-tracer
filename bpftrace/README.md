# Bedrock BPFtrace

Bedrock BPFtrace is a repository of bpftrace scripts used by the Bedrock tracer. All tracing scripts are generated from Python + Jinja2 templates and exported in .bt format.

## Overview

This repository contains the BPFtrace programs required for Bedrock’s tracing engine. Templates are written in Python using Jinja2 and compiled into ready-to-run .bt scripts.

## Installation & Script Generation

After cloning the repository, generate the tracing scripts with:

```sh
make
```

> Make sure to have Python3 and Python-venv installed on your machine.

Once completed, the generated .bt files will be available in the bpftrace/ directory.

## Script Categories

The repository generates tracing scripts across five categories:

* Tracing by PID
* Tracing by process name (command)
* Execute and trace a command
* Tracing by cgroup
* Tracing by process name within a cgroup

Each category includes two tracing modes:

1. Basic I/O tracing: Tracks standard I/O operations such as read and write.
2. Memory-mapped I/O tracing: Tracks I/O operations performed via memory mapping.

### Silent Mode

A silent mode is also available. When enabled, metadata collection is omitted to reduce log volume. This mode is useful for high-level I/O monitoring where detailed file access patterns are not required.
