#!/usr/bin/env bash

# SIGTERM-handler
term_handler() {
  exit 0
}
trap term_handler SIGTERM

if [ ! -f /sentinel/gobyte.conf ]; then
  if [ -z "$RPCUSER" -o -z "$RPCPASSWORD" -o -z "$RPCPORT" ]; then
    echo "When no /sentinel/gobyte.conf is present, you must at least set RPCUSER, RPCPORT and RPCPASSWORD environment variables"
    exit 1
  fi

  echo "" > /sentinel/gobyte.conf
  if [ -n "$RPCUSER" ]; then
    echo "rpcuser=${RPCUSER}" >> /sentinel/gobyte.conf
  fi
  if [ -n "$RPCPASSWORD" ]; then
    echo "rpcpassword=${RPCPASSWORD}" >> /sentinel/gobyte.conf
  fi
  if [ -n "$RPCPORT" ]; then
    echo