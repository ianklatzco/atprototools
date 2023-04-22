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

    def reskoot(self,url):
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

        person_youre_reskooting = self.resolveHandle(url.split('/')[-3]).json().get('did') # its a DID
        url_identifier = url.split('/')[-1]

        # import pdb; pdb.set_trace()
        skoot_cid = self.get_skoot_by_url(url).json().get('thread').get('post').get('cid')

        # subject -> uri is the maia one (thing rt'ing, scx)
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        timestamp = timestamp.isoformat().replace('+00:00', 'Z')

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        data = {
            "collection": "app.bsky.feed.repost",
            "repo": "{}".format(self.DID),
            "record": {
                "subject": {
                    "uri":"at://{}/app.bsky.feed.post/{}".format(person_youre_reskooting, url_identifier),
                    "cid":"{}".format(skoot_cid) # cid of the skoot to reskoot
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

    def resolveHandle(self,username): # aka getDid
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}
        resp = requests.get(
            self.ATP_HOST + "/xrpc/com.atproto.identity.resolveHandle?handle={}".format(username),
            headers=headers
        )
        return resp
    
    def get_skyline(self,n = 10): # fetches the logged in account's following timeline ("skyline")
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}
        resp = requests.get(
            self.ATP_HOST + "/xrpc/app.bsky.feed.getTimeline?limit={}".format(n),
            headers=headers
        )
        return resp
    
    def get_skoot_by_url(self,url):
        "https://bsky.social/xrpc/app.bsky.feed.getPostThread?uri=at%3A%2F%2Fdid%3Aplc%3Ascx5mrfxxrqlfzkjcpbt3xfr%2Fapp.bsky.feed.post%2F3jszsrnruws27A"
        "at://did:plc:scx5mrfxxrqlfzkjcpbt3xfr/app.bsky.feed.post/3jszsrnruws27"
        "https://staging.bsky.app/profile/naia.bsky.social/post/3jszsrnruws27"

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        username_of_person_in_link = url.split('/')[-3]
        did_of_person_in_link = self.resolveHandle(username_of_person_in_link).json().get('did')
        url_identifier = url.split('/')[-1] # the random stuf at the end

        uri = "at://{}/app.bsky.feed.post/{}".format(did_of_person_in_link, url_identifier)

        resp = requests.get(
            self.ATP_HOST + "/xrpc/app.bsky.feed.getPostThread?uri={}".format(uri),
            headers=headers
        )

        return resp
    
    def uploadBlob(self, blob_path, content_type):
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN, "Content-Type": content_type}
        with open(blob_path, 'rb') as f:
            image_bytes = f.read()
            resp = requests.post(
                self.ATP_HOST + "/xrpc/com.atproto.repo.uploadBlob",
                data=image_bytes,
                headers=headers
            )
        return resp

    def post_skoot(self, postcontent, image_path = None, timestamp=None ):
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

        print(data)
        resp = requests.post(
            self.ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
            json=data,
            headers=headers
        )

        return resp

    def delete_skoot(self, did,rkey):
        data = {"collection":"app.bsky.feed.post","repo":"did:plc:{}".format(did),"rkey":"{}".format(rkey)}
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}
        resp = requests.post(
            self.ATP_HOST + "/xrpc/com.atproto.repo.deleteRecord",
            json = data,
            headers=headers
        )
        return resp

    def get_car_file(self, did_of_car_to_fetch=None):
        '''
        Get a .car file contain all skoots.
        TODO is there a putRepo?
        TODO save to file
        '''

        if did_of_car_to_fetch == None:
            did_of_car_to_fetch = self.DID

        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        resp = requests.get(
            self.ATP_HOST + "/xrpc/com.atproto.sync.getRepo?did={}".format(did_of_car_to_fetch),
            headers = headers
        )

        return resp

    def get_latest_skoot(self, accountname):
        return self.get_latest_n_skoots(accountname, 1)

    def get_latest_n_skoots(self, username, n=5):
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
    
    def getProfile(self, did):
        headers = {"Authorization": "Bearer " + self.ATP_AUTH_TOKEN}

        resp = requests.get(
            self.ATP_HOST + "/xrpc/app.bsky.actor.getProfile?actor={}".format(did),
            headers=headers
        )

        return resp


if __name__ == "__main__":
    # This code will only be executed if the script is run directly
    # login(os.environ.get("BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
    sess = Session(os.environ.get("BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
    # f = get_latest_n_skoots('klatz.co',1).content
    # print(f)
    # resp = reskoot("https://staging.bsky.app/profile/klatz.co/post/3jt22a3jx5l2a")
    # resp = get_car_file()
    import pdb; pdb.set_trace()



# resp = login()
# post("test post")
