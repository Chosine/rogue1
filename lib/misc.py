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
   