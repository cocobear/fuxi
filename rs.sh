#!/bin/bash
# scp -r fuxi root@fuxi:/tmp
rsync -rav -e ssh --include='*.py' --exclude='*.pyc' ./fuxi root@fuxi:/tmp
ssh root@fuxi   << remotessh
docker cp /tmp/fuxi 5c:/opt/fuxi
docker restart 5ce
remotessh
