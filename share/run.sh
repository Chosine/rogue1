#!/usr/bin/env bash

# SIGTERM-handler
term_handler() {
  exit 0
}
trap term_handler SIGTERM

if [ ! -f /sentinel/gobyte.conf ]; then
  if [ -z "$RPCUSER" -o -z "$RPCPASSWORD" -o -z "$RPCPO