# -*- coding: utf-8 -*-
import pdb
from pprint import pprint
import re
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../lib')))
import config
from models import Superblock, Proposal, GovernanceObject, Setting, Signal, Vote, Outcome
from models import VoteSignals, VoteOutcomes
from peewee import PeeweeException  # , OperationalError, IntegrityError
from gobyted import GoByteDaemon
import gobytelib
from decimal import Decimal
gobyted = GoByteDaemon.from_gobyte_conf(config.gobyte_conf)
import misc
# ==============================================================================
# do stuff here

pr = Proposal(
    name='proposal7',
    url='https://gobytecentral.com/proposal7',
    payment_address='yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV',
    payment_amount=39.23,
    start_epoch=1483250400,
    end_epoch=1491022800,
)

# sb = Superblock(
#     event_block_height = 62500,
#     payment_addresses = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJ