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
    # in the encoding should be abo