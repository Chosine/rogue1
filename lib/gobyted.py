
"""
gobyted JSONRPC interface
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import config
import base58
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from masternode import Masternode
from decimal import Decimal
import time


class GoByteDaemon():
    def __init__(self, **kwargs):
        host = kwargs.get('host', '127.0.0.1')
        user = kwargs.get('user')
        password = kwargs.get('password')
        port = kwargs.get('port')

        self.creds = (user, password, host, port)

        # memoize calls to some gobyted methods
        self.governance_info = None
        self.gobject_votes = {}

    @property
    def rpc_connection(self):
        return AuthServiceProxy("http://{0}:{1}@{2}:{3}".format(*self.creds))

    @classmethod
    def from_gobyte_conf(self, gobyte_dot_conf):
        from gobyte_config import GoByteConfig
        config_text = GoByteConfig.slurp_config_file(gobyte_dot_conf)
        creds = GoByteConfig.get_rpc_creds(config_text, config.network)

        creds[u'host'] = config.rpc_host

        return self(**creds)

    def rpc_command(self, *params):
        return self.rpc_connection.__getattr__(params[0])(*params[1:])

    # common RPC convenience methods

    def get_masternodes(self):
        mnlist = self.rpc_command('masternodelist', 'full')
        return [Masternode(k, v) for (k, v) in mnlist.items()]

    def get_current_masternode_vin(self):
        from gobytelib import parse_masternode_status_vin

        my_vin = None

        try:
            status = self.rpc_command('masternode', 'status')
            mn_outpoint = status.get('outpoint') or status.get('vin')
            my_vin = parse_masternode_status_vin(mn_outpoint)
        except JSONRPCException as e:
            pass

        return my_vin

    def governance_quorum(self):
        # TODO: expensive call, so memoize this
        total_masternodes = self.rpc_command('masternode', 'count', 'enabled')
        min_quorum = self.govinfo['governanceminquorum']

        # the minimum quorum is calculated based on the number of masternodes
        quorum = max(min_quorum, (total_masternodes // 10))
        return quorum

    @property
    def govinfo(self):
        if (not self.governance_info):
            self.governance_info = self.rpc_command('getgovernanceinfo')
        return self.governance_info

    # governance info convenience methods
    def superblockcycle(self):
        return self.govinfo['superblockcycle']

    def last_superblock_height(self):
        height = self.rpc_command('getblockcount')
        cycle = self.superblockcycle()
        return cycle * (height // cycle)

    def next_superblock_height(self):
        return self.last_superblock_height() + self.superblockcycle()

    def is_masternode(self):
        return not (self.get_current_masternode_vin() is None)

    def is_synced(self):
        return self.rpc_command('mnsync', 'status')['IsSynced']

    def current_block_hash(self):
        height = self.rpc_command('getblockcount')
        block_hash = self.rpc_command('getblockhash', height)
        return block_hash

    def get_superblock_budget_allocation(self, height=None):
        if height is None:
            height = self.rpc_command('getblockcount')
        return Decimal(self.rpc_command('getsuperblockbudget', height))

    def next_superblock_max_budget(self):
        cycle = self.superblockcycle()
        current_block_height = self.rpc_command('getblockcount')

        last_superblock_height = (current_block_height // cycle) * cycle
        next_superblock_height = last_superblock_height + cycle

        last_allocation = self.get_superblock_budget_allocation(last_superblock_height)
        next_allocation = self.get_superblock_budget_allocation(next_superblock_height)

        next_superblock_max_budget = next_allocation

        return next_superblock_max_budget

    # "my" votes refers to the current running masternode
    # memoized on a per-run, per-object_hash basis
    def get_my_gobject_votes(self, object_hash):
        import gobytelib
        if not self.gobject_votes.get(object_hash):
            my_vin = self.get_current_masternode_vin()
            # if we can't get MN vin from output of `masternode status`,
            # return an empty list
            if not my_vin:
                return []

            (txid, vout_index) = my_vin.split('-')

            cmd = ['gobject', 'getcurrentvotes', object_hash, txid, vout_index]
            raw_votes = self.rpc_command(*cmd)
            self.gobject_votes[object_hash] = gobytelib.parse_raw_votes(raw_votes)

        return self.gobject_votes[object_hash]

    def is_govobj_maturity_phase(self):
        # 3-day period for govobj maturity
        maturity_phase_delta = 1662      # ~(60*24*3)/2.6
        if config.network == 'testnet':
            maturity_phase_delta = 24    # testnet

        event_block_height = self.next_superblock_height()