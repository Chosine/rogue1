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


def is_vali