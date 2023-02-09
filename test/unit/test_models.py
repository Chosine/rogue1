import pytest
import os
import sys
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../lib')))

# setup/teardown?


# Proposal model
@pytest.fixture
def proposal():
    from models import Proposal
    return Proposal()


def test_proposal(proposal):
    d = proposal.get_dict()
    assert isinstance(d, dict)

    fields = 