import unittest
import os
import random
import string

from atprototools import *

BSKY_USERNAME = os.environ.get("BSKY_USERNAME")
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")

TEST_EMAIL = os.environ.get("TEST_EMAIL")
INVITE_CODE = os.environ.get("INVITE_CODE")

class TestSessionLogin(unittest.TestCase):
    def test_registration(self):
        session = register(''.join(random.choices(string.ascii_lowercase, k=15)), "Password1!", INVITE_CODE, TEST_EMAIL)

    def test_login(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        self.assertIsNotNone(session.DID)

    def test_login_bad_username(self):
        with self.assertRaises(ValueError):
            Session("","")

    def test_follow(self):
        # TODO login should go in a pre-setup
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        self.assertIsNotNone(session.DID)

        # TODO getProfile, check if following, unfollow if already following
        resp = session.follow("ik.bsky.social")
        self.assertEqual(resp.status_code, 200)
        pass

    def test_getProfile(self):
        # TODO figure out this test library's persistent object and re-use the same session for all the tests
        # TODOTODO refresh the token since lifetime is probably a minute
        pass

    def test_uploadBlob(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        self.assertIsNotNone(session.DID)
        resp = session.uploadBlob("tests/test.jpeg", "image/jpeg")
        self.assertEqual(resp.status_code, 200)
        pass

    def test_post_skoot(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        self.assertIsNotNone(session.DID)
        resp = session.post_skoot("good meme", "tests/test.jpeg")
        self.assertEqual(resp.status_code, 200)
        # print(resp.json())
        pass
