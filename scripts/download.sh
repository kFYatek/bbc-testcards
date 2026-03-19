#!/bin/sh
set -e
REPODIR="$(dirname "$(dirname "$0")")"
TMPDIR=

remove_tmpdir() {
    rm -rf "$TMPDIR"
}

trap remove_tmpdir EXIT
TMPDIR="$(mktemp -d)"

cd "$REPODIR"
REPODIR="$PWD"
cd sources

if [ ! -f 'This Is BBC HD_20130326_0120.ts' ]; then
    curl -L 'https://dl.dropbox.com/s/pk4bvdnqd6yttyn/This%20Is%20BBC%20HD_20130326_0120.zip' \
        -o "$TMPDIR/This Is BBC HD_20130326_0120.zip"
    unzip "$TMPDIR/This Is BBC HD_20130326_0120.zip" 'This Is BBC HD_20130326_0120.ts'
fi

if [ ! -f 'Test Card C.gif' -o ! -f 'Test Card D.gif' ]; then
    curl -L 'https://github.com/WhatTheBlock/innounp/releases/download/v0.50/innounp.exe' \
        -o "$TMPDIR/innounp.exe"
    curl 'http://www.rtrussell.co.uk/tccgen/tcsetup.exe' -o "$TMPDIR/tcsetup.exe"
    wine "$TMPDIR/innounp.exe" -e "$TMPDIR/tcsetup.exe" '{app}\samples\Test Card ?.gif'
fi

if [ ! -f 'd0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg' ]; then
    curl -L \
        'https://tvark.org/media/1998i/2020-05-15/d0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg' \
        -o 'd0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg'
fi

if [ ! -f '8633vid_dat.zip' ]; then
    curl -L \
        'https://github.com/KarstenHervoeHansen/PTV/raw/aa169cac40d4fee87b41b449101e41e98e928121/PT5230/PT8633/video_data/8633vid_dat.zip' \
        -o '8633vid_dat.zip'
fi
