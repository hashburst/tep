#!/bin/sh
set -eu
BASELINE="a97a17833074e9e44820fe8e90c151e8b22f37ad"
test "$(git rev-parse HEAD)" = "$BASELINE" || { echo "wrong baseline" >&2; exit 2; }
python3 -m unittest discover -s tests -p 'test_*.py'
