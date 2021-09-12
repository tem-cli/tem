#!/usr/bin/env sh

[ -z "$EXE" ] && EXE=tem

print_help() {
    mid="┃ Command: $EXE $* ┃"
    top="$(echo "$mid" | sed 's_._━_g' | sed 's_.\(.*\)._┏\1┓_')"
    bot="$(echo "$mid" | sed 's_._━_g' | sed 's_.\(.*\)._┗\1┛_')"

    echo "$top"
    echo "$mid"
    echo "$bot"
    $EXE "$@" --help
}

print_help

for cmd_raw in "$(dirname "$TEM_EXECUTABLE")"/tem/cli/*.py; do
    cmd="$(basename ${cmd_raw%%.py})"
    print_help "$cmd"
done

print_help add
print_help rm
print_help put
print_help ls
print_help repo
print_help config
print_help init
print_help env
