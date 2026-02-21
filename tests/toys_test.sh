#!/usr/bin/env sh
# file: tests/toyes_test.sh

# build the toys into binary files
cd tests/toys
make all
cd ../..

# run the tracer on the copy toy
bdtrace --execute "./tests/toys/bin/copy ./tests/toys/src/copy.c /tmp/copied.c" --debug --out "/tmp/flak-toy-copy"

# run the tracer on the mmap toy
bdtrace --execute "./tests/toys/bin/mmap ./tests/toys/src/mmap.c /tmp/mapped.c" --debug --out "/tmp/flak-toy-mmap"

# cleanup
rm -f /tmp/copied.c
rm -f /tmp/mapped.c
