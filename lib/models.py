
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import init
import time
import datetime
import re
import simplejson
from peewee import IntegerField, CharField, TextField, ForeignKeyField, DecimalField, DateTimeField
import peewee
import playhouse.signals
import misc
import gobyted
from misc import (printdbg, is_numeric)
import config
from bitcoinrpc.authproxy import JSONRPCException
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

# our mixin
from governance_class import GovernanceClass

db = config.db
db.connect()


# TODO: lookup table?
GOBYTED_GOVOBJ_TYPES = {
    'proposal': 1,
    'superblock': 2,
}
GOVOBJ_TYPE_STRINGS = {
    1: 'proposal',
    2: 'trigger',  # it should be trigger here, not superblock
}

# schema version follows format 'YYYYMMDD-NUM'.
#
# YYYYMMDD is the 4-digit year, 2-digit month and 2-digit day the schema
# changes were added.
#
# NUM is a numerical version of changes for that specific date. If the date
# changes, the NUM resets to 1.
SCHEMA_VERSION = '20170111-1'

# === models ===


class BaseModel(playhouse.signals.Model):
    class Meta:
        database = db

    @classmethod
    def is_database_connected(self):
        return not db.is_closed()


class GovernanceObject(BaseModel):
    parent_id = IntegerField(default=0)
    object_creation_time = IntegerField(default=int(time.time()))
    object_hash = CharField(max_length=64)
    object_parent_hash = CharField(default='0')
    object_type = IntegerField(default=0)
    object_revision = IntegerField(default=1)
    object_fee_tx = CharField(default='')
    yes_count = IntegerField(default=0)
    no_count = IntegerField(default=0)
    abstain_count = IntegerField(default=0)
    absolute_yes_count = IntegerField(default=0)

    class Meta:
        db_table = 'governance_objects'

    # sync gobyted gobject list with our local relational DB backend
    @classmethod
    def sync(self, gobyted):
        golist = gobyted.rpc_command('gobject', 'list')

        # objects which are removed from the network should be removed from the DB
        try:
            for purged in self.purged_network_objects(list(golist.keys())):
                # SOMEDAY: possible archive step here
                purged.delete_instance(recursive=True, delete_nullable=True)
        except Exception as e:
            printdbg("Got an error while purging: %s" % e)

        for item in golist.values():
            try:
                (go, subobj) = self.import_gobject_from_gobyted(gobyted, item)
            except Exception as e:
                printdbg("Got an error upon import: %s" % e)

    @classmethod
    def purged_network_objects(self, network_object_hashes):
        query = self.select()
        if network_object_hashes:
            query = query.where(~(self.object_hash << network_object_hashes))
        return query

    @classmethod
    def import_gobject_from_gobyted(self, gobyted, rec):
        import decimal
        import gobytelib
        import binascii
        import gobject_json

        object_hash = rec['Hash']

        gobj_dict = {
            'object_hash': object_hash,
            'object_fee_tx': rec['CollateralHash'],
            'absolute_yes_count': rec['AbsoluteYesCount'],
            'abstain_count': rec['AbstainCount'],
            'yes_count': rec['YesCount'],
            'no_count': rec['NoCount'],
        }

        # deserialise and extract object
        json_str = binascii.unhexlify(rec['DataHex']).decode('utf-8')
        dikt = gobject_json.extract_object(json_str)

        subobj = None

        type_class_map = {
            1: Proposal,
            2: Superblock,
        }
        subclass = type_class_map[dikt['type']]

        # set object_type in govobj table
        gobj_dict['object_type'] = subclass.govobj_type

        # exclude any invalid model data from gobyted...
        valid_keys = subclass.serialisable_fields()
        subdikt = {k: dikt[k] for k in valid_keys if k in dikt}

        # get/create, then sync vote counts from gobyted, with every run
        govobj, created = self.get_or_create(object_hash=object_hash, defaults=gobj_dict)
        if created:
            printdbg("govobj created = %s" % created)
        count = govobj.update(**gobj_dict).where(self.id == govobj.id).execute()
        if count:
            printdbg("govobj updated = %d" % count)
        subdikt['governance_object'] = govobj

        # get/create, then sync payment amounts, etc. from gobyted - GoByted is the master
        try:
            newdikt = subdikt.copy()
            newdikt['object_hash'] = object_hash
            if subclass(**newdikt).is_valid() is False:
                govobj.vote_delete(gobyted)
                return (govobj, None)

            subobj, created = subclass.get_or_create(object_hash=object_hash, defaults=subdikt)
        except Exception as e:
            # in this case, vote as delete, and log the vote in the DB
            printdbg("Got invalid object from gobyted! %s" % e)
            govobj.vote_delete(gobyted)
            return (govobj, None)

        if created:
            printdbg("subobj created = %s" % created)
        count = subobj.update(**subdikt).where(subclass.id == subobj.id).execute()
        if count:
            printdbg("subobj updated = %d" % count)

        # ATM, returns a tuple w/gov attributes and the govobj
        return (govobj, subobj)

    def vote_delete(self, gobyted):
        if not self.voted_on(signal=VoteSignals.delete, outcome=VoteOutcomes.yes):
            self.vote(gobyted, VoteSignals.delete, VoteOutcomes.yes)
        return

    def get_vote_command(self, signal, outcome):
        cmd = ['gobject', 'vote-conf', self.object_hash,
               signal.name, outcome.name]
        return cmd

    def vote(self, gobyted, signal, outcome):
        import gobytelib

        # At this point, will probably never reach here. But doesn't hurt to
        # have an extra check just in case objects get out of sync (people will
        # muck with the DB).
        if (self.object_hash == '0' or not misc.is_hash(self.object_hash)):
            printdbg("No governance object hash, nothing to vote on.")
            return

        # have I already voted on this gobject with this particular signal and outcome?
        if self.voted_on(signal=signal):
            printdbg("Found a vote for this gobject/signal...")
            vote = self.votes.where(Vote.signal == signal)[0]

            # if the outcome is the same, move on, nothing more to do
            if vote.outcome == outcome:
                # move on.
                printdbg("Already voted for this same gobject/signal/outcome, no need to re-vote.")
                return