
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