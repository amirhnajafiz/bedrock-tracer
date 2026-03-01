# ============================
# Stage 1 — Builder
# ============================
FROM ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON=python3.12
ENV VENV_DIR=/usr/local/app/.venv
ENV PATH="$VENV_DIR/bin:$PATH"

ENV LIBBPF_VERSION=v1.5.0
ENV BPFTRACE_VERSION=v0.24.0
ENV CRICTL_VERSION=v1.35.0

ARG BEDROCK_BPFTRACE=v0.0.1-stable
ENV BEDROCK_BPFTRACE=${BEDROCK_BPFTRACE}

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    linux-tools-generic \
    libbpfcc-dev \
    bpfcc-tools \
    libcereal-dev \
    llvm-18 \
    llvm-18-dev \
    clang-18 \
    libclang-18-dev \
    pahole \
    libgtest-dev \
    libgmock-dev \
    libdw-dev \
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
    build-essential \
    cmake \
    flex \
    bison \
    xxd \
    libelf-dev zlib1g-dev \
    libfl-dev libedit-dev \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Build and install libbpf
# requirements: git, cmake
# -----------------------------
RUN git clone --depth 1 --branch ${LIBBPF_VERSION} \
    https://github.com/libbpf/libbpf.git /tmp/libbpf && \
    make -C /tmp/libbpf/src -j$(nproc) && \
    make -C /tmp/libbpf/src install PREFIX=/usr LIBDIR=/usr/lib/x86_64-linux-gnu && \
    rm -rf /tmp/libbpf

# -----------------------------
# Build and install bpftrace
# requirements: libbpfcc-dev bpfcc-tools libcereal-dev bison flex xxd llvm-18 llvm-18-dev
#               clang-18 libclang-18 pahole libgtest-dev libgmock-dev libdw-dev libelf-dev
# -----------------------------
RUN git clone --depth 1 --branch ${BPFTRACE_VERSION} \
    https://github.com/bpftrace/bpftrace.git /tmp/bpftrace && \
    cmake -S /tmp/bpftrace -B /tmp/bpftrace/build \
        -DCMAKE_BUILD_TYPE=Release \
        -DLLVM_DIR=/usr/lib/llvm-18/lib/cmake/llvm \
        -DClang_DIR=/usr/lib/llvm-18/lib/cmake/clang && \
    cmake --build /tmp/bpftrace/build -j$(nproc) && \
    cmake --install /tmp/bpftrace/build && \
    strip /usr/local/bin/bpftrace && \
    rm -rf /tmp/bpftrace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iproute2 \
    git \
    strace \
    python3.12 \
    python3.12-venv \
    python3-pip \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# ============================
# Stage 2 — Runtime
# ============================
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libelf1 \
    zlib1g \
    libedit2 \
    libssl3 \
    libdw1 \
    libseccomp2 \
    libbpfcc-dev \
    bpfcc-tools \
    kmod \
    procps \
    ca-certificates \
    clang-18 \
    libclang-18-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

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

COPY --from=builder /usr/local /usr/local
COPY --from=builder /usr/lib/x86_64-linux-gnu/libbpf* /usr/lib/x86_64-linux-gnu/

# Default command — start inside venv automatically
CMD ["/bin/sh"]
