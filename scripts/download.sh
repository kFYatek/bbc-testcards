#!/bin/sh
set -e
REPODIR="$(dirname "$(dirname "$0")")"
TMPDIR=

remove_tmpdir() {
    rm -rf "$TMPDIR"
}

trap remove_tmpdir EXIT
TMPDIR="$(mktemp -d)"

cd "$REPODIR/sources"

if [ ! -f 'This Is BBC HD_20130326_0120.ts' ]; then
    pushd "$TMPDIR"
        wget 'https://dl.dropbox.com/s/pk4bvdnqd6yttyn/This Is BBC HD_20130326_0120.zip'
    popd
    unzip "$TMPDIR/This Is BBC HD_20130326_0120.zip" 'This Is BBC HD_20130326_0120.ts'
fi

if [ ! -f 'Test Card C.gif' -o ! -f 'Test Card D.gif' ]; then
    pushd "$TMPDIR"
        wget 'https://github.com/WhatTheBlock/innounp/releases/download/v0.50/innounp.exe'
        wget 'http://www.rtrussell.co.uk/tccgen/tcsetup.exe'
    popd
    wine "$TMPDIR/innounp.exe" -e "$TMPDIR/tcsetup.exe" '{app}\samples\Test Card ?.gif'
fi

if [ ! -f 'd0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg' ]; then
    wget 'https://tvark.org/media/1998i/2020-05-15/d0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg'
fi
