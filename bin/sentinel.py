
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
        return

    # query votes for this specific ebh... if we have voted for this specific
    # ebh, then it's voted on. since we track votes this is all done using joins
    # against the votes table
    #
    # has this masternode voted on *any* superblocks at the given event_block_height?
    # have we voted FUNDING=YES for a superblock for this specific event_block_height?

    event_block_height = gobyted.next_superblock_height()

    if Superblock.is_voted_funding(event_block_height):
        # printdbg("ALREADY VOTED! 'til next time!")

        # vote down any new SBs because we've already chosen a winner
        for sb in Superblock.at_height(event_block_height):
            if not sb.voted_on(signal=VoteSignals.funding):
                sb.vote(gobyted, VoteSignals.funding, VoteOutcomes.no)

        # now return, we're done
        return

    if not gobyted.is_govobj_maturity_phase():
        printdbg("Not in maturity phase yet -- will not attempt Superblock")
        return
