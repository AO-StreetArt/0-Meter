#!/bin/bash

python 0-meter.py ci/ping_bad.xml

if [ $? -eq 0 ]
then
  exit 1
else
  echo "Test Passed"
  exit 0
fi
