PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: all venv pip_install bt_scripts cleanup

all: venv pip_install bt_scripts

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

pip_install: venv
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install -e .

bt_scripts:
	git clone --depth 1 --branch v0.0.0 \
		https://github.com/amirhnajafiz/bedrock-bpftrace.git tmp
	cp -r tmp/bpftrace ./bpftrace
	rm -rf tmp

cleanup:
	rm -rf bpftrace
