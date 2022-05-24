# -*- coding: utf-8 -*-
import pytest
import sys
import os
import time
os.environ['SENTINEL_ENV'] = 'test'
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../test_sentinel.conf'))
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../lib')))
import misc
import config
from models import GovernanceObject, Proposal, Vote


# clear DB tables before each execution
def setup():
    # clear tables first
    Vote.delete().execute()
    Proposal.delete().execute()
    GovernanceObject.delete().execute()


def teardown():
    pass


# list of proposal govobjs to import for testing
@pytest.fixture
def go_list_proposals():
    items = [
        {u'AbsoluteYesCount': 1000,
         u'AbstainCount': 7,
         u'CollateralHash': u'acb67ec3f3566c9b94a26b70b36c1f74a010a37c0950c22d683cc50da324fdca',
         u'DataHex': u'5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20323132323532303430302c20226e616d65223a20226465616e2d6d696c6c65722d35343933222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c20227374617