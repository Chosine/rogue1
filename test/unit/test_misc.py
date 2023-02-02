import pytest
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../lib')))
import misc


def test_is_numeric():
    assert misc.is_numeric('45') is True
 