import simplejson
import binascii
import sys
import pdb
from pprint import pprint
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../lib')))
import gobytelib
# ============================================================================
usage = "%s <hex>" % sys.argv[0]

obj = None
if len(sys.argv) < 2:
    print(usage)
    sys.exit(1)
else