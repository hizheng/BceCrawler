#!/bin/bash

target='huangzheng01@lingxu-worker-online002-whdx.qiyi.virtual:/opt/cronjobs/'
env='dev'
if [[ ! -z $1 ]];then
    env=$1
fi
scp -r ../bce-crawler "$target$env"
