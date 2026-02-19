PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: all setup venv deps generate clean distclean

all: generate

setup: deps

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

deps: venv
	$(VENV_PIP) install -r requirements.txt

generate: deps
	$(VENV_PYTHON) gen_bpftrace.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache

distclean: clean
	rm -rf $(VENV_DIR)
	find bpftrace -type f -name "*.bt" -delete
