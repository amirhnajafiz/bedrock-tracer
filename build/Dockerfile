# Use official Ubuntu 24.04 as base image
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON=python3.12
ENV VENV_DIR=/usr/local/app/.venv
ENV PATH="$VENV_DIR/bin:$PATH"

ARG BEDROCK_BPFTRACE=v0.0.0-stable
ENV BEDROCK_BPFTRACE=${BEDROCK_BPFTRACE}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bpftrace \
    linux-tools-generic \
    linux-tools-common \
    linux-headers-generic \
    libbpf-dev \
    llvm \
    clang \
    iproute2 \
    git \
    ca-certificates \
    make \
    g++ \
    kmod \
    wget \
    curl \
    xz-utils \
    procps \
    strace \
    python3.12 \
    python3.12-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/local/app

# Copy project files
COPY requirements.txt .
COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/

# Clone bpftrace scripts (equivalent to bt_scripts target)
RUN git clone --depth 1 --branch $BEDROCK_BPFTRACE \
    https://github.com/amirhnajafiz/bedrock-bpftrace.git tmp && \
    cp -r tmp/bpftrace ./bpftrace && \
    rm -rf tmp

# Create virtual environment
RUN $PYTHON -m venv $VENV_DIR

# Upgrade pip and install dependencies (equivalent to pip_install target)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Make test script executable
RUN chmod +x tests/tracings_test.sh

# Default command — start inside venv automatically
CMD ["/bin/sh"]
