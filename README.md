
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

Sentinel is "used" as a script called from cron every minute.

### Set up Cron

Set up a crontab entry to call Sentinel every minute:

    $ crontab -e

In the crontab editor, add the lines below, replacing '/path/to/sentinel' to the path where you cloned sentinel to:

    * * * * * cd /home/gobyte/sentinel && ./venv/bin/python bin/sentinel.py >/dev/null 2>&1

### Test Configuration

Test the config by running tests:

    $ ./venv/bin/py.test ./test

With all tests passing and crontab setup, Sentinel will stay in sync with gobyted and the installation is complete

## Configuration

An alternative (non-default) path to the `gobyte.conf` file can be specified in `sentinel.conf`:

    gobyte_conf=/home/gobyte/.gobytecore/gobyte.conf

## Troubleshooting

To view debug output, set the `SENTINEL_DEBUG` environment variable to anything non-zero, then run the script manually:

    $ SENTINEL_DEBUG=1 ./venv/bin/python bin/sentinel.py

## Maintainer

Dash [@nmarley](https://github.com/nmarley)
GoByte [GoByteDev](https://github.com/gobytecoin)

## Contributing

Please follow the [GoByteCore guidelines for contributing](https://github.com/gobytecoin/gobyte/blob/master/CONTRIBUTING.md).

Specifically:

* [Contributor Workflow](https://github.com/gobytecoin/gobyte/blob/master/CONTRIBUTING.md#contributor-workflow)

    To contribute a patch, the workflow is as follows:

    * Fork repository
    * Create topic branch
    * Commit patches

    In general commits should be atomic and diffs should be easy to read. For this reason do not mix any formatting fixes or code moves with actual code changes.