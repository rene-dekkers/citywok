#!/bin/bash
if [ $# -ne 1 ]; then
	echo "Usage: $0 <language>"
	exit 2
fi
pybabel-python3 init -i messages.pot -d translations -l $1
