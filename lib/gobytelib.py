import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import base58
import hashlib
import re
from decimal import Decimal
import simplejson
import binascii
from misc import printdbg, epoch2str
import time


def is_valid_gobyte_address(address, network='mainnet'):
    # Only public key addresses are allowed
    # A valid address is a RIPEMD-160 hash which contains 20 bytes
    # Prior to base58 encoding 1 version byte is prepended and
    # 4 checksum bytes are appended so the total number of
    # base58 encoded bytes should be 25.  This means the number of characters
    # in the encoding should be about 34 ( 25 * log2( 256 ) / log2( 58 ) ).
    gobyte_version = 112 if network == 'testnet' else 38

    # Check length (This is important because the base58 library has problems
    # with long addresses (which are invalid anyway).
    if ((len(address) < 26) or (len(address) > 35)):
        return False

    address_version = None

    try:
        decoded = base58.b58decode_chk(address)
        address_version = ord(decoded[0:1])
    except:
        # rescue from exception, not a valid GoByte address
        return False

    if (address_version != gobyte_version):
        return False

    return True


def hashit(data):
    return int(hashlib.sha256(data.encode('utf-8')).hexdigest(), 16)


# returns the masternode VIN of the elected winner
def elect_mn(**kwargs):
    current_block_hash = kwargs['block_hash']
    mn_list = kwargs['mnlist']

    # filter only enabled MNs
    enabled = [mn for mn in mn_list if mn.status == 'ENABLED']

    block_hash_hash = hashit(current_block_hash)

    candidates = []
    for mn in enabled:
        mn_vin_hash = hashit(mn.vin)
        diff = mn_vin_hash - block_hash_hash
        absdiff = abs(diff)
        candidates.append({'vin': mn.vin, 'diff': absdiff})

    candidates.sort(key=lambda k: k['diff'])

    try:
        winner = candidates[0]['vin']
    except:
        winner = None

    return winner


def parse_masternode_status_vin(status_vin_string):
    status_vin_string_regex = re.compile(r'CTxIn\(COutPoint\(([0-9a-zA-Z]+),\s*(\d+)\),')

    m = status_vin_string_regex.match(status_vin_string)

    # To Support additional format of string return from masternode status rpc.
    if m is None:
        status_output_string_regex = re.compile(r'([0-9a-zA-Z]+)-(\d+)')
        m = status_output_string_regex.match(status_vin_string)

    txid = m.group(1)
    index = m.gro