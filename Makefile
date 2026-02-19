.PHONY: all bt_scripts cleanup

all: bt_scripts

bt_scripts:
	git clone --depth 1 --branch v0.0.0 \
		https://github.com/amirhnajafiz/bedrock-bpftrace.git tmp
	cp -r tmp/bpftrace ./bpftrace
	rm -rf tmp

cleanup:
	rm -rf bpftrace
