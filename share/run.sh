#!/usr/bin/env bash

# SIGTERM-handler
term_handler() {
  exit 0
}
trap term_handler SIGTERM

if 