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
         u'DataHex': u'5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20323132323532303430302c20226e616d65223a20226465616e2d6d696c6c65722d35343933222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6465616e2d6d696c6c65722d35343933227d5d5d',
         u'DataString': u'[["proposal", {"end_epoch": 2122520400, "name": "dean-miller-5493", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://gobytecentral.org/dean-miller-5493"}]]',
         u'Hash': u'dfd7d63979c0b62456b63d5fc5306dbec451180adee85876cbf5b28c69d1a86c',
         u'IsValidReason': u'',
         u'NoCount': 25,
         u'YesCount': 1025,
         u'fBlockchainValidity': True,
         u'fCachedDelete': False,
         u'fCachedEndorsed': False,
         u'fCachedFunding': False,
         u'fCachedValid': True},
        {u'AbsoluteYesCount': 1000,
         u'AbstainCount': 29,
         u'CollateralHash': u'3efd23283aa98c2c33f80e4d9ed6f277d195b72547b6491f43280380f6aac810',
         u'DataHex': u'5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20323132323532303430302c20226e616d65223a20226665726e616e64657a2d37363235222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6665726e616e64657a2d37363235227d5d5d',
         u'DataString': u'[["proposal", {"end_epoch": 2122520400, "name": "fernandez-7625", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://gobytecentral.org/fernandez-7625"}]]',
         u'Hash': u'0523445762025b2e01a2cd34f1d10f4816cf26ee1796167e5b029901e5873630',
         u'IsValidReason': u'',
         u'NoCount': 56,
         u'YesCount': 1056,
         u'fBlockchainValidity': True,
         u'fCachedDelete': False,
         u'fCachedEndorsed': False,
         u'fCachedFunding': False,
         u'fCachedValid': True},
    ]

    return items


# Proposal
@pytest.fixture
def proposal():
    # NOTE: no governance_object_id is set
    pobj = Proposal(
        start_epoch=1483250400,  # 2017-01-01
        end_epoch=2122520400,
        name="wine-n-cheeze-party",
        url="https://gobytecentral.com/wine-n-cheeze-party",
        payment_address="yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
        payment_amount=13
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return pobj


def test_proposal_is_valid(proposal):
    from gobyted import GoByteDaemon
    import gobytelib
    gobyted = GoByteDaemon.from_gobyte_conf(config.gobyte_conf)

    orig = Proposal(**proposal.get_dict())  # make a copy

    # fixture as-is should be valid
    assert proposal.is_valid() is True

    # ============================================================
    # ensure end_date not greater than start_date
    # ============================================================
    proposal.end_epoch = proposal.start_epoch
    assert proposal.is_valid() is False

    proposal.end_epoch = proposal.start_epoch - 1
    assert proposal.is_valid() is False

    proposal.end_epoch = proposal.start_epoch + 0
    assert proposal.is_valid() is False

    proposal.end_epoch = proposal.start_epoch + 1
    assert proposal.is_valid() is True

    # reset
    proposal = Proposal(**orig.get_dict())

    # ============================================================
    # ensure valid proposal name
    # ============================================================

    proposal.name = '   heya!@209h '
    assert proposal.is_valid() is False

    proposal.name = "anything' OR 'x'='x"
    assert proposal.is_valid() is False

    proposal.name = ' '
    assert proposal.is_valid() is False

    proposal.name = ''
    assert proposal.is_valid() is False

    proposal.name = '0'
    assert proposal.is_valid() is True

    proposal.name = 'R66-Y'
    assert proposal.is_valid() is True

    proposal.name = 'valid-name'
    assert proposal.is_valid() is True

    proposal.name = '   mostly-valid-name'
    assert proposal.is_valid() is False

    proposal.name = 'also-mostly-valid-name   '
    assert proposal.is_valid() is False

    proposal.name = ' similarly-kinda-valid-name '
    assert proposal.is_valid() is False

    proposal.name = 'dean miller 5493'
    assert proposal.is_valid() is False

    proposal.name = 'dean-millerà-5493'
    assert proposal.is_valid() is False

    proposal.name = 'dean-миллер-5493'
    assert proposal.is_valid() is False

    # binary gibberish
    proposal.name = gobytelib.deserialise('22385c7530303933375c75303363375c75303232395c75303138635c75303064335c75303163345c75303264385c75303236615c75303134625c75303163335c75303063335c75303362385c75303266615c75303261355c75303266652f2b5c75303065395c75303164655c75303136655c75303338645c75303062385c75303138635c75303064625c75303064315c75303038325c75303133325c753032333222')
    assert proposal.is_valid() is False

    # reset
    proposal = Proposal(**orig.get_dict())

    # ============================================================
    # ensure valid payment address
    # ============================================================
    proposal.payment_address = '7'
    assert proposal.is_valid() is False

    proposal.payment_address = 'YYE8KWYAUU5YSWSYMB3Q3RYX8XTUU9Y7UI'
    assert proposal.is_valid() is False

    proposal.payment_address = 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Uj'
    assert proposal.is_valid() is False

    prop