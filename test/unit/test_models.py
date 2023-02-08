import pytest
import os
import sys
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../lib')))

# setup/teardown?


# Proposal model
@pytest.fixture
def proposal():
    from model