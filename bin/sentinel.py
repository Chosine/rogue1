
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

    proposals = Proposal.approved_and_ranked(proposal_quorum=gobyted.governance_quorum(), next_superblock_max_budget=gobyted.next_superblock_max_budget())
    budget_max = gobyted.get_superblock_budget_allocation(event_block_height)
    sb_epoch_time = gobyted.block_height_to_epoch(event_block_height)

    sb = gobytelib.create_superblock(proposals, event_block_height, budget_max, sb_epoch_time)
    if not sb:
        printdbg("No superblock created, sorry. Returning.")
        return

    # find the deterministic SB w/highest object_hash in the DB
    dbrec = Superblock.find_highest_deterministic(sb.hex_hash())
    if dbrec:
        dbrec.vote(gobyted, VoteSignals.funding, VoteOutcomes.yes)

        # any other blocks which match the sb_hash are duplicates, delete them
        for sb in Superblock.select().where(Superblock.sb_hash == sb.hex_hash()):
            if not sb.voted_on(signal=VoteSignals.funding):
                sb.vote(gobyted, VoteSignals.delete, VoteOutcomes.yes)

        printdbg("VOTED FUNDING FOR SB! We're done here 'til next superblock cycle.")
        return
    else:
        printdbg("The correct superblock wasn't found on the network...")

    # if we are the elected masternode...
    if (gobyted.we_are_the_winner()):
        printdbg("we are the winner! Submit SB to network")
        sb.submit(gobyted)


def check_object_validity(gobyted):
    # vote (in)valid objects
    for gov_class in [Proposal, Superblock]:
        for obj in gov_class.select():
            obj.vote_validity(gobyted)


def is_gobyted_port_open(gobyted):
    # test socket open before beginning, display instructive message to MN
    # operators if it's not
    port_open = False
    try:
        info = gobyted.rpc_command('getgovernanceinfo')
        port_open = True
    except (socket.error, JSONRPCException) as e:
        print("%s" % e)

    return port_open


def main():
    gobyted = GoByteDaemon.from_gobyte_conf(config.gobyte_conf)
    options = process_args()

    # print version and return if "--version" is an argument
    if options.version:
        print("GoByte Sentinel v%s" % config.sentinel_version)
        return

    # check gobyted connectivity
    if not is_gobyted_port_open(gobyted):
        print("Cannot connect to gobyted. Please ensure gobyted is running and the JSONRPC port is open to Sentinel.")
        return

    # check gobyted sync
    if not gobyted.is_synced():
        print("gobyted not synced with network! Awaiting full sync before running Sentinel.")
        return

    # ensure valid masternode
    if not gobyted.is_masternode():
        print("Invalid Masternode Status, cannot continue.")
        return

    # register a handler if SENTINEL_DEBUG is set
    if os.environ.get('SENTINEL_DEBUG', None):
        import logging
        logger = logging.getLogger('peewee')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    if options.bypass:
        # bypassing scheduler, remove the scheduled event
        printdbg("--bypass-schedule option used, clearing schedule")
        Scheduler.clear_schedule()

    if not Scheduler.is_run_time():
        printdbg("Not yet time for an object sync/vote, moving on.")
        return

    if not options.bypass:
        # delay to account for cron minute sync
        Scheduler.delay()

    # running now, so remove the scheduled event
    Scheduler.clear_schedule()

    # ========================================================================
    # general flow:
    # ========================================================================
    #
    # load "gobject list" rpc command data, sync objects into internal database
    perform_gobyted_object_sync(gobyted)

    # auto vote network objects as valid/invalid
    # check_object_validity(gobyted)

    # vote to delete expired proposals
    prune_expired_proposals(gobyted)

    # create a Superblock if necessary
    attempt_superblock_creation(gobyted)

    # schedule the next run
    Scheduler.schedule_next_run()


def signal_handler(signum, frame):
    print("Got a signal [%d], cleaning up..." % (signum))
    Transient.delete('SENTINEL_RUNNING')
    sys.exit(1)


def cleanup():
    Transient.delete(mutex_key)


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bypass-scheduler',
                        action='store_true',
                        help='Bypass scheduler and sync/vote immediately',
                        dest='bypass')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='Print the version (GoByte Sentinel vX.X.X) and exit')
