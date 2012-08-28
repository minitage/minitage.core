#!/usr/bin/env bash
if [[ ! -f bootstrap.py ]];then
    cd $(dirname $0)/..
fi
ps aux|grep -- 'bin/buildout'|awk '{print $2}'|xargs kill -9
bin/buildout  $@
