#!/usr/bin/env bash

script_name="${0}"
script_dirname="$( dirname "${0}" )"
script_basename="$( basename "${0}" )"

vrun() {
	local level="${1}"; shift 1;
	[ "${verbosity:--1}" -ge "${level}" ] && { "${@}"; return "${?}"; }
	return 0;
}

dump_command()
{
	for arg in "${@}"; do
		printf "%q " "${arg}"
	done
	echo
}

pretend_run()
{
	if "${pretend}"; then
		dump_command "${@}" 1>&2
	else
		"${@}"
	fi
}

vlog() {
	local level="${1}"; shift 1;
	[ "${verbosity:--1}" -ge "${level}" ] && {
		1>&2 echo "$(date +%Y%m%d%H%M%S) ${script_basename}:${FUNCNAME[1]} ${$}" "${@}"
	}
	return 0;
}

vprun() {
	local level="${1}"; shift 1;
	[ "${verbosity:--1}" -ge "${level}" ] && {
		prefix="$(date +%Y%m%d%H%M%S) ${script_basename}:${FUNCNAME[1]} ${$}"
		"${@}" | sed 's|.*|'"${prefix}"' &|g' 1>&2;
		return "${PIPESTATUS[0]}";
	}
	return 0;
}

main_usage()
{
	[ "${#}" -gt 0 ] && {
		1>&2 echo "ERROR: ${@}"
	}
	1>&2 echo -e "${script_basename} [options] command"

	1>&2 echo -e "options:"

	local -a format=( printf " %-32s%s\n" )
	1>&2 "${format[@]}" "-h" "help"
	1>&2 "${format[@]}" "-v" "increase verbosity"
	1>&2 "${format[@]}" "-p" "pretend mode"
	return 0;
}

main()
{
	local argv=( "${@}" )
	local verbosity=0
	local verbose=false
	local pretend=false
	local something=""

	local OPTARG OPTERR="" option OPTIND
	while getopts "hvps:" option "${@}"
	do
		case "${option}" in
			h)
				"${FUNCNAME}_usage"
				return 0;
				;;
			v)
				verbosity=$(( ${verbosity} + 1 ))
				;;
			p)
				pretend=true
				;;
			*)
				"${FUNCNAME}_usage" "Invalid options [ OPTARG=${OPTARG}, OPTERR=${OPTERR}, option=${option} ]"
				return 1
				;;
		esac
	done
	shift $(( ${OPTIND} - 1 ))

	vrun 1 true && verbose=true

	vprun 1 declare -p script_name script_dirname script_basename argv
	vprun 1 declare -p option OPTERR OPTIND
	vprun 1 declare -p verbosity pretend verbose
	vlog 1 "\${#} == ${#} \${#argv[@]} = ${#argv[@]}"

	vlog 0 "entry ..."

    gitdir=laicheil-force2019

    if [ -e "${gitdir}" ]
    then
        vlog 0 "Already cloned ..."
    else
        [  -e  ] || {
            vlog 0 "cleaning bad ${gitdir}"
            rm -rv "${gitdir}"
        }
        git clone https://github.com/laicheil/force2019.git "${gitdir}"
    fi

    if python3 -c 'import laicheil.force2019;'
    then
        vlog 0 "Already installed ..."
    else
        vlog 0 "Could not find module, installing ..."
        pip3 install --user --upgrade --editable "${gitdir}"
    fi

    git -C ${gitdir} pull

	return 0
}

if ! $(return >/dev/null 2>&1)
then
	script_dirname=$( dirname "${0}" )
	script_basename=$( basename "${0}" )
	main "${@}"
	exit "${?}"
fi
