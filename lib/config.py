"""
    Set up defaults and read sentinel.conf
"""
import sys
import os
from gobyte_config import GoByteConfig

default_sentinel_config = os.path.normpath(
    os.path.jo