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


def p