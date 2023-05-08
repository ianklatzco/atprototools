import requests
import datetime
import os
import unittest

# ATP_HOST = "https://bsky.social"
# ATP_AUTH_TOKEN = ""
# DID = "" # leave blank
# TODO prob makes sense to have username here too, and then always assume username + did are populated
# two use cases: library calls login() (swap to a class later) and cli user uses a shell variable.
# in either case login() should populate these globals within this file.
# maybe PASSWORD shouldn't hang around, but you have bigger problems if you're relying on python encapsulation for security.

# TODO annotate all requests.get/post with auth header


class Session():
    def __init__(self, username, password, pds = None):
        if pds: # check if pds is not empty
            self.ATP_HOST = pds # use the given value
        else:
            self.ATP_HOST = "https://bsky.social" # use bsky.social by default
        self.ATP_AUTH_TOKEN = ""
        self.DID = ""
        self.USERNAME = username

        data = {"identifier": username, "password": password}
        resp = requests.post(
            self.ATP_HOST + "/xrpc/com.atproto.server.createSession",
            json=data
        )

        self.ATP_AUTH_TOKEN = resp.json().get('accessJwt')
        if self.ATP_AUTH_TOKEN == None:
            raise ValueError("No access token, is your password wrong? Do      export BSKY_PASSWORD='yourpassword'")

        self.DID = resp.json().get("did")
        # TODO DIDs expire shortly and need to be refreshed for any long-lived sessions

    def reinit(self):
        """Check if the session needs to be refreshed, and refresh if so."""
        # TODO
        # if a request failed, use refreshJWT
        resp = self.get_profile("klatz.co")

        if resp.status_code == 200:
            # yay!
            # do nothing lol
            pass
        else: # re-init
            # what is the endpoint
            pass
                        

    def rebloot(self, url):
        """Rebloot a bloot given the URL."""
        # sample url from desktop
        # POST https://bsky.social/xrpc/com.atproto.repo.createRecord
        # https://staging.bsky.app/profile/klatz.co/post/3jruqqeygrt2d
        '''
        {
            "collection":"app.bsky.feed.repost",
            "repo":"did:plc:n5ddwqolbjpv2czaronz6q3d",
            "record":{
                "subject":{
                        "uri":"at://did:plc:scx5mrfxxrqlfzkjcpbt3xfr/app.bsky.feed.post/3jszsrnruws27",
                        "cid":"bafyreiad336s3honwubedn4ww7m2iosefk5wqgkiity2ofc3ts4ii3ffkq"
                        },
                "createdAt":"2023-04-10T17:38:10.516Z",
                "$type":"app.bsky.feed.repost"
            }
        }
        '''

        person_youre_reblooting = self.resolveHandle(url.split('/')[-3]).json().get('did') # its a DID
        url_identifier = url.split('/')[-1]

        # import pdb; pdb.set_trace()
        bloot_cid = self.getBlootByUrl(url).json().get('thread').get('post').get('cid')

        # subject -> uri is the maia one (thing rt'ing, scx)
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        timestamp = timestamp.isoformat().replace('+00:00', 'Z')

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        data = {
            "collection": "app.bsky.feed.repost",
            "repo": "{}".format(self.DID),
            "record": {
                "subject": {
                    "uri":"at://{}/app.bsky.feed.post/{}".format(person_youre_reblooting, url_identifier),
                    "cid":"{}".format(bloot_cid) # cid of the bloot to rebloot
                },
                "createdAt": timestamp,
                "$type": "app.bsky.feed.repost"
            }
        }

        resp = requests.post(
            self.ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
            json=data,
            headers=headers
        )

        return resp

    def resolveHandle(self, username):
        """Get the DID given a username, aka getDid."""
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}
        resp = requests.get(
            self.ATP_HOST + "/xrpc/com.atproto.identity.resolveHandle?handle={}".format(username),
            headers=headers
        )
        return resp
    
    def getSkyline(self,n = 10):
        """Fetch the logged in account's following timeline ("skyline")."""
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}
        resp = requests.get(
            self.ATP_HOST + "/xrpc/app.bsky.feed.getTimeline?limit={}".format(n),
            headers=headers
        )
        return resp
    
    def getBlootByUrl(self, url):
        """Get a bloot's HTTP response data when given the URL."""
        # https://staging.bsky.app/profile/shinyakato.dev/post/3ju777mfnfv2j
        "https://bsky.social/xrpc/app.bsky.feed.getPostThread?uri=at%3A%2F%2Fdid%3Aplc%3Ascx5mrfxxrqlfzkjcpbt3xfr%2Fapp.bsky.feed.post%2F3jszsrnruws27A"
        "at://did:plc:scx5mrfxxrqlfzkjcpbt3xfr/app.bsky.feed.post/3jszsrnruws27"
        "https://staging.bsky.app/profile/naia.bsky.social/post/3jszsrnruws27"

        # getPosts
        # https://bsky.social/xrpc/app.bsky.feed.getPosts?uris=at://did:plc:o2hywbrivbyxugiukoexum57/app.bsky.feed.post/3jua5rlgrq42p

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        username_of_person_in_link = url.split('/')[-3]
        if not "did:plc" in username_of_person_in_link:
            did_of_person_in_link = self.resolveHandle(username_of_person_in_link).json().get('did')
        else:
            did_of_person_in_link = username_of_person_in_link

        url_identifier = url.split('/')[-1] # the random stuff at the end, better hope there's no query params

        uri = "at://{}/app.bsky.feed.post/{}".format(did_of_person_in_link, url_identifier)

        resp = requests.get(
            self.ATP_HOST + "/xrpc/app.bsky.feed.getPosts?uris={}".format(uri),
            headers=headers
        )

        return resp
    
    def uploadBlob(self, blob_path, content_type):
        """Upload bytes data (a "blob") with the given content type."""
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN, "Content-Type": content_type}
        with open(blob_path, 'rb') as f:
            image_bytes = f.read()
            resp = requests.post(
                self.ATP_HOST + "/xrpc/com.atproto.repo.uploadBlob",
                data=image_bytes,
                headers=headers
            )
        return resp

    def postBloot(self, postcontent, image_path = None, timestamp=None, reply_to=None):
        """Post a bloot."""
        #reply_to expects a dict like the following
        # {
        #     #root is the main original post
        #     "root": {
        #         "cid": "bafyreig7ox2h5kmcmjukbxfpopy65ggd2ymhbnldcu3fx72ij3c22ods3i", #CID of root post
        #         "uri": "at://did:plc:nx3kofpg4oxmkonqr6su5lw4/app.bsky.feed.post/3juhgsu4tpi2e" #URI of root post
        #     },
        #     #parent is the comment you want to reply to, if you want to reply to the main post directly this should be same as root
        #     "parent": {
        #         "cid": "bafyreie7eyj4upwzjdl2vmzqq4gin3qnuttpb6nzi6xybgdpesfrtcuguu",
        #         "uri": "at://did:plc:mguf3p2ana5qzs7wu3ss4ghk/app.bsky.feed.post/3jum6axhxff22"
        #     }
        #}
        if not timestamp:
            timestamp = datetime.datetime.now(datetime.timezone.utc)
        timestamp = timestamp.isoformat().replace('+00:00', 'Z')

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        data = {
            "collection": "app.bsky.feed.post",
            "$type": "app.bsky.feed.post",
            "repo": "{}".format(self.DID),
            "record": {
                "$type": "app.bsky.feed.post",
                "createdAt": timestamp,
                "text": postcontent
            }
        }

        if image_path:
            data['record']['embed'] = {}
            image_resp = self.uploadBlob(image_path, "image/jpeg")
            x = image_resp.json().get('blob')
            image_resp = self.uploadBlob(image_path, "image/jpeg")
            data["record"]["embed"]["$type"] = "app.bsky.embed.images"
            data['record']["embed"]['images'] = [{
                "alt": "",
                "image": image_resp.json().get('blob')
            }]
        if reply_to:
            data['record']['reply'] = reply_to
        resp = requests.post(
            self.ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
            json=data,
            headers=headers
        )

        return resp

    def deleteBloot(self, did,rkey):
        # rkey: post slug
        # i.e. /profile/foo.bsky.social/post/AAAA
        # rkey is AAAA
        data = {"collection":"app.bsky.feed.post","repo":"did:plc:{}".format(did),"rkey":"{}".format(rkey)}
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}
        resp = requests.post(
            self.ATP_HOST + "/xrpc/com.atproto.repo.deleteRecord",
            json = data,
            headers=headers
        )
        return resp

    def getArchive(self, did_of_car_to_fetch=None):
        """Get a .car file containing all bloots.
        
        TODO is there a putRepo?
        TODO save to file
        """

        if did_of_car_to_fetch == None:
            did_of_car_to_fetch = self.DID

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        resp = requests.get(
            self.ATP_HOST + "/xrpc/com.atproto.sync.getRepo?did={}".format(did_of_car_to_fetch),
            headers = headers
        )

        return resp

    def getLatestBloot(self, accountname):
        """Return the most recent bloot from the specified account."""
        return self.getLatestNBloots(accountname, 1)

    def getLatestNBloots(self, username, n=5):
        """Return the most recent n bloots from the specified account."""
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}
        resp = requests.get(
            self.ATP_HOST + "/xrpc/app.bsky.feed.getAuthorFeed?actor={}&limit={}".format(username, n),
            headers = headers
        )

        return resp

    # [[API Design]] TODO one implementation should be highly ergonomic (comfy 2 use) and the other should just closely mirror the API's exact behavior?
    # idk if im super happy about returning requests, either, i kinda want tuples where the primary object u get back is whatever ergonomic thing you expect
    # and then you can dive into that and ask for the request. probably this means writing a class to encapsulate each of the
    # API actions, populating the class in the implementations, and making the top-level api as pretty as possible
    # ideally atproto lib contains meaty close-to-the-api and atprototools is a layer on top that focuses on ergonomics?
    def follow(self, username=None, did_of_person_you_wanna_follow=None):
        """Follow the user with the given username or DID."""

        if username:
            did_of_person_you_wanna_follow = self.resolveHandle(username).json().get("did")

        if not did_of_person_you_wanna_follow:
            # TODO better error in resolveHandle
            raise ValueError("Failed; please pass a username or did of the person you want to follow (maybe the account doesn't exist?)")

        timestamp = datetime.datetime.now(datetime.timezone.utc)
        timestamp = timestamp.isoformat().replace('+00:00', 'Z')

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        data = {
            "collection": "app.bsky.graph.follow",
            "repo": "{}".format(self.DID),
            "record": {
                "subject": did_of_person_you_wanna_follow,
                "createdAt": timestamp,
                "$type": "app.bsky.graph.follow"
            }
        }

        resp = requests.post(
            self.ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
            json=data,
            headers=headers
        )

        return resp
    
    def unfollow(self):
        # TODO lots of code re-use. package everything into a API_ACTION class.
        raise NotImplementedError
    
    def get_profile(self, username):
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        # TODO did / username check, it should just work regardless of which it is

        resp = requests.get(
            self.ATP_HOST + "/xrpc/app.bsky.actor.getProfile?actor={}".format(username),
            headers=headers
        )

        return resp


def register(user, password, invcode, email):
    data = {
        "email": email,
        "handle": user + ".bsky.social",
        "inviteCode": invcode,
        "password": password,
    }

    resp = requests.post(
        # don't use self.ATP_HOST here because you can't instantiate a session if you haven't registered an account yet
        "https://bsky.social/xrpc/com.atproto.server.createAccount",
        json = data,
    )

    return resp
        

if __name__ == "__main__":
    # This code will only be executed if the script is run directly
    # login(os.environ.get("BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
    sess = Session(os.environ.get("BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
    # f = getLatestNBloots('klatz.co',1).content
    # print(f)
    # resp = rebloot("https://staging.bsky.app/profile/klatz.co/post/3jt22a3jx5l2a")
    # resp = getArchive()
    import pdb; pdb.set_trace()



# resp = login()
# post("test post")
