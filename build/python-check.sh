#!/bin/sh

SRCDIR="$(dirname "$0")/.."

cd "${SRCDIR}"

ret=0
FILES="$(
	find build packaging -name '*.py' | while read f; do
		[ -e "${f}.in" ] || echo "${f}"
	done
)"
flake8 --ignore=E501,W503 ${FILES} || ret=1
echo "All files checked."
exit ${ret}
