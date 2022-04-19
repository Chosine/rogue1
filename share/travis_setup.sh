#!/bin/bash
set -evx

mkdir ~/.gobytecore

# safety check
if [ ! -f ~/.gobytecore/.gobyte.conf ]; then
  