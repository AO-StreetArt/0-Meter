#!/bin/bash

python 0-meter.py ci/ping.xml

if [ $? -eq 0 ]
then
  exit 1
else
  exit 0
fi
