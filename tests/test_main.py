import unittest
import os

from atprototools import *

BSKY_USERNAME = os.environ.get("BSKY_USERNAME")
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")

class TestSessionLogin(unittest.TestCase):
    def test_login(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        self.assertIsNotNone(session.DID)

    def test_login_bad_username(self):
        with self.assertRaises(ValueError):
            Session("","")
