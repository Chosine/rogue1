
#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../lib')))
import init
import config
import misc
from gobyted import GoByteDaemon
from models import Superblock, Proposal, GovernanceObject
from models import VoteSignals, VoteOutcomes, Transient
import socket
from misc import printdbg
import time
from bitcoinrpc.authproxy import JSONRPCException
import signal
import atexit
import random
from scheduler import Scheduler
import argparse


# sync gobyted gobject list with our local relational DB backend
def perform_gobyted_object_sync(gobyted):
    GovernanceObject.sync(gobyted)


def prune_expired_proposals(gobyted):
    # vote delete for old proposals
    for proposal in Proposal.expired(gobyted.superblockcycle()):
        proposal.vote(gobyted, VoteSignals.delete, VoteOutcomes.yes)


def attempt_superblock_creation(gobyted):
    import gobytelib

    if not gobyted.is_masternode():
        print("We are not a Masternode... can't submit superblocks!")