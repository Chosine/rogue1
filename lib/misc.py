import time
from datetime import datetime
import re
import sys
import os


def is_numeric(strin):
    import decimal

    strin = str(strin)

    # Decimal allows spaces in input, but we don't
    if strin.strip() != strin:
        return False
    try:
        value = decimal.Decimal(strin)
    except decimal.InvalidOperation as e:
        return False

    return True


def printdbg(str):
    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(now()))
    logstr = "{} {}".format(ts, str)
    if os.environ.get('SENTINEL_DEBUG', None):
        print(logstr)

    sys.stdout.flush()


def is_hash(s):
    m = re.match('^[a-f0-9]{64}$