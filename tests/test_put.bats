#!/usr/bin/env bats

. common.bats.in

REPO="$(realpath "$PWD")/_out/put_repo"
DESTDIR="$(realpath "$PWD")/_out/put_dest"
drys_put() { $EXE put -R "$REPO" "$@"; }

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'put'
    mkdir -p "$REPO" "$DESTDIR"
    rm -rf "$REPO"/* "$DESTDIR"/*
    ./prepare_files.sh files "$REPO"
fi

@test "drys put {FILE}" {
    cd "$DESTDIR"
    drys_put file1.txt
    [ "$(cat "$DESTDIR"/file1.txt)" = "$(cat "$REPO"/file1.txt)" ]
}

@test "drys put {FILE} [with -o xor -d]" {
    cd "$DESTDIR"

    drys_put file1.txt -o _file1.txt
    [ "$(cat "$DESTDIR"/_file1.txt)" = "$(cat "$REPO"/file1.txt)" ]

    drys_put file1.txt -d dir
    [ "$(cat "$DESTDIR"/dir/file1.txt)" = "$(cat "$REPO"/file1.txt)" ]
}

@test "drys put {DIR}" {
    cd "$DESTDIR"

    drys_put dir1
    compare_trees "$REPO"/dir1 "$DESTDIR"/dir1/**
}

# @test "drys put {}
# TODO both -o and -d error

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4