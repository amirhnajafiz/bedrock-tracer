# Use official Ubuntu 24.04 as base image
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON=python3.12
ENV VENV_DIR=/usr/local/app/.venv
ENV PATH="$VENV_DIR/bin:$PATH"

ENV LIBBPF_VERSION=v1.5.0
ENV BPFTRACE_VERSION=v0.24.0
ENV CRICTL_VERSION=v1.35.0

ARG BEDROCK_BPFTRACE=v0.0.0-stable
ENV BEDROCK_BPFTRACE=${BEDROCK_BPFTRACE}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    linux-tools-generic \
    linux-tools-common \
    linux-headers-generic \
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
    apt-transport-https \
    gnupg \
    libseccomp2 \
    xz-utils \
    procps \
    strace \
    python3.12 \
    python3.12-venv \
    python3-pip \
    build-essential \
    cmake \
    flex \
    bison \
    libelf-dev zlib1g-dev \
    libfl-dev libedit-dev \
    pkg-config \
    libssl-dev \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Build and install libbpf
# -----------------------------
RUN git clone --branch ${LIBBPF_VERSION} --depth 1 https://github.com/libbpf/libbpf.git /tmp/libbpf && \
    cd /tmp/libbpf/src && \
    make && \
    make install && \
    ldconfig && \
    rm -rf /tmp/libbpf

# Ensure pkg-config finds libbpf
ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

# -----------------------------
# Build and install bpftrace
# -----------------------------
RUN git clone --branch ${BPFTRACE_VERSION} --depth 1 https://github.com/bpftrace/bpftrace.git /tmp/bpftrace && \
    cd /tmp/bpftrace && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    rm -rf /tmp/bpftrace

# -----------------------------
# Install crictl
# -----------------------------
RUN wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$CRICTL_VERSION/crictl-$CRICTL_VERSION-linux-amd64.tar.gz && \
    tar zxvf crictl-$CRICTL_VERSION-linux-amd64.tar.gz -C /usr/local/bin && \
    rm -f crictl-$CRICTL_VERSION-linux-amd64.tar.gz

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
