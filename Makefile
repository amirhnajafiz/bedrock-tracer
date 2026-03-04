PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

BEDROCK_BPFTRACE ?= v0.0.2-stable

.PHONY: all venv pip_install bt_scripts help cleanup test_shutdown

all: venv pip_install bt_scripts help

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

pip_install: venv
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install -e .

bt_scripts:
	rm -rf bpftrace
	git clone --depth 1 --branch $(BEDROCK_BPFTRACE) \
		https://github.com/amirhnajafiz/bedrock-bpftrace.git tmp
	cp -r tmp/bpftrace ./bpftrace
	cp tmp/tests/kernel_support.sh ./bpftrace
	rm -rf tmp

help:
	@echo "\n\nsetup finished."
	@echo "run: source $(VENV_DIR)/bin/activate"
	@echo "run: bdtrace --help"
	@echo ""

cleanup:
	rm -rf bpftrace

test_shutdown:
	sh tests/shutdown_integration_test.sh
