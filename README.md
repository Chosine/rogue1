
# GoByte Sentinel

[![Build Status](https://travis-ci.org/gobytecoin/sentinel.svg?branch=master)](https://travis-ci.org/gobytecoin/sentinel)

> An automated governance helper for GoByte Masternodes.

Sentinel is an autonomous agent for persisting, processing and automating GoByte governance objects and tasks. It is a Python application which runs alongside the GoByteCore instance on each GoByte Masternode.

## Table of Contents
- [Install](#install)
  - [Dependencies](#dependencies)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Maintainer](#maintainer)
- [Contributing](#contributing)
- [License](#license)

## Install

These instructions cover installing Sentinel on Ubuntu 18.04 / 20.04.

### Dependencies

Update system package list and install dependencies:

    $ sudo apt-get update
    $ sudo apt-get -y install git python3 virtualenv

Make sure Python version 3.6.x or above is installed:

    python3 --version

Make sure the local GoByteCore daemon running is at least version 0.15.0.

    $ gobyted --version | head -n1

### Install Sentinel

Clone the Sentinel repo and install Python dependencies.

    $ git clone https://github.com/gobytecoin/sentinel.git && cd sentinel
    $ virtualenv -p $(which python3) ./venv
    $ ./venv/bin/pip install -r requirements.txt

## Usage