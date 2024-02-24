#!/bin/bash

unset KUBECONFIG

cd .. && docker build -f docker/Dockerfile.latest \
             -t yz181x/chatgpt-on-wechat .

docker tag yz181x/chatgpt-on-wechat yz181x/chatgpt-on-wechat:$(date +%y%m%d)
