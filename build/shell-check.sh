#!/bin/sh

SRCDIR="$(dirname "$0")/.."
cd "${SRCDIR}"

if [ -z "${VALIDATION_SHELL}" ]; then
	# prefer dash over bash for POSIX complaint
	[ -x /bin/dash ] && VALIDATION_SHELL="/bin/dash" || VALIDATION_SHELL="/bin/sh"
fi

EXTRA_ARGS=""
# if bash use POSIX parsing
"${VALIDATION_SHELL}" --version 2>&1 | grep -q bash && EXTRA_ARGS="${EXTRA_ARGS} --posix"

ret="$(
	find packaging build -type f \( -executable -or -name '*.sh' -or -name '*.bash' \) -and -not -name '*.py' | while read f; do
		read l < "${f}"
		shell="/bin/sh"
		candidate="${l#\#!}"
		candidate="${candidate# *}" # remove leading spaces
		candidate="${candidate% *}" # remove parameter
		[ "${candidate}" != "${l}" ] && shell="${candidate}"
		skip=
		case "${shell}" in
			/bin/sh) shell="${VALIDATION_SHELL} ${EXTRA_ARGS}" ;;
			/bin/bash) ;;
			/usr/bin/python*) skip=1 ;;
			*)
				echo "ERROR: Unknown shell '${shell}' for '${f}'"
				ret=1
			;;
		esac
		if [ -z "${skip}" ]; then
			${shell} -n "${f}" || ret=1
		fi
		echo "${ret}"
	done | tail -n 1
)"

exit ${ret}
