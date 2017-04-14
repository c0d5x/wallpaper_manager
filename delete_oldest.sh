#!/usr/bin/env bash

pwd="."

if [ ! -z "$1" ]; then
    pwd=$1
fi

cd $pwd
ls -tr|head|xargs rm -v
cd -
