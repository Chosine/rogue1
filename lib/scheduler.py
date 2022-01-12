import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../lib')))
import init
import misc
from models import Transient
from misc import printdbg
import time
import random


class Scheduler(object):
    transient_key_scheduled = 'NEXT_SENT