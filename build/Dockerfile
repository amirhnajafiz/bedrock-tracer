# ------------------------------
# Using base image from amirhnajafiz/bedrock-bpftrace which includes bpftrace and its dependencies.
# ------------------------------
FROM ghcr.io/amirhnajafiz/bedrock-bpftrace:v0.0.2-stable

# Set environment variables for bpftrace and crictl versions
ARG BEDROCK_BPFTRACE=v0.0.2-stable
ENV BEDROCK_BPFTRACE=${BEDROCK_BPFTRACE}
ENV CRICTL_VERSION=v1.35.0

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/local/app

# -----------------------------
# Install crictl
# -----------------------------
RUN wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$CRICTL_VERSION/crictl-$CRICTL_VERSION-linux-amd64.tar.gz && \
    tar zxvf crictl-$CRICTL_VERSION-linux-amd64.tar.gz -C /usr/local/bin && \
    rm -f crictl-$CRICTL_VERSION-linux-amd64.tar.gz

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

# Default command — start inside venv automatically
CMD ["/bin/sh"]