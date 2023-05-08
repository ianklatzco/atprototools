import unittest
import os
import random
import string

from atprototools import *

BSKY_USERNAME = os.environ.get("BSKY_USERNAME")
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")

class TestSessionLogin(unittest.TestCase):
    '''
    This test case uses a random invite code and a generic email and succeeds when registration fails due to
    an invalid invite code. 
    '''
    def test_registration(self):
        resp = register(''.join(random.choices(string.ascii_lowercase, k=15)), "Password1!", "bsky-social-hto7xan", "test@gmail.com")
        self.assertEqual(resp.status_code, 400)

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

    def test_get_profile(self):
        # TODO figure out this test library's persistent object and re-use the same session for all the tests
        # TODOTODO refresh the token since lifetime is probably a minute
        pass

    def test_upload_blob(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        self.assertIsNotNone(session.DID)
        resp = session.uploadBlob("tests/test.jpeg", "image/jpeg")
        self.assertEqual(resp.status_code, 200)
        pass

    def test_post_bloot(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        self.assertIsNotNone(session.DID)
        resp = session.postBloot("good meme", "tests/test.jpeg")
        self.assertEqual(resp.status_code, 200)
        # print(resp.json())
        pass

    def test_get_skyline(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        skyline_firstitem_text = session.getSkyline(1).json().get('feed')[0].get('post').get('record').get('text')
        self.assertIsNotNone(skyline_firstitem_text)
    
    def test_get_bloot_by_url(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)

        url1 = "https://staging.bsky.app/profile/did:plc:o2hywbrivbyxugiukoexum57/post/3jua5rlgrq42p" # did
        url2 = "https://staging.bsky.app/profile/klatz.co/post/3jua5rlgrq42p" # username

        ee = session.getBlootByUrl(url1).json()
        assert ee.get('posts') != None
        bb = session.getBlootByUrl(url2).json()
        assert bb.get('posts') != None

    def test_reply(self):
        session = Session(BSKY_USERNAME, BSKY_PASSWORD)
        # https://staging.bsky.app/profile/klatz.co/post/3jua5rlgrq42p
        first_post = {
            'cid': 'bafyreigyk6l24uiorkxhqyrridwru2bwdqcpnitclj267xh74qqxzhjfhu',
            'uri': 'at://did:plc:o2hywbrivbyxugiukoexum57/app.bsky.feed.post/3jua5rlgrq42p'
        }
        reply_ref = {"root": first_post, "parent": first_post}
        resp = session.postBloot("reply test", reply_to=reply_ref)
        self.assertEqual(resp.status_code, 200)
