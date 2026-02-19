.PHONY: all bt_scripts

all: bt_scripts

bt_scripts:
	git subtree add --prefix=bpftrace \
		https://github.com/amirhnajafiz/bedrock-bpftrace.git \
		v0.0.0 \
		--squash
