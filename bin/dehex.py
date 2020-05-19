import binascii
import sys

usage = "%s <hex>" % sys.argv[0]

if len(sys.argv) < 2:
    print(usage)
else: