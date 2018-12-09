from donate.app import create_app
from donate.settings import TestConfig
from donate import models


def test_insert_empty_tx():
    app = create_app(TestConfig)
    tx = models.Transaction()
