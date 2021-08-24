
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import models
from bitcoinrpc.authproxy import JSONRPCException
import misc
import re
from misc import printdbg
import time


# mixin for GovObj composed classes like proposal and superblock, etc.
class GovernanceClass(object):
    only_masternode_can_submit = False

    # lazy
    @property
    def go(self):
        return self.governance_object

    # pass thru to GovernanceObject#vote
    def vote(self, gobyted, signal, outcome):
        return self.go.vote(gobyted, signal, outcome)

    # pass thru to GovernanceObject#voted_on
    def voted_on(self, **kwargs):
        return self.go.voted_on(**kwargs)

    def vote_validity(self, gobyted):
        if self.is_valid():
            printdbg("Voting valid! %s: %d" % (self.__class__.__name__, self.id))
            self.vote(gobyted, models.VoteSignals.valid, models.VoteOutcomes.yes)
        else:
            printdbg("Voting INVALID! %s: %d" % (self.__class__.__name__, self.id))
            self.vote(gobyted, models.VoteSignals.valid, models.VoteOutcomes.no)