import os
import tempfile

import pytest

from donate import donate


@pytest.fixture
def client():
    db_fd, donate.app.config['DATABASE'] = tempfile.mkstemp()
    donate.app.config['TESTING'] = True
    client = donate.app.test_client()

    with donate.app.app_context():
        donate.init_db()

    yield client

    os.close(db_fd)
    os.unlink(donate.app.config['DATABASE'])
