import requests
import datetime
import os

ATP_HOST = "https://bsky.social"
ATP_AUTH_TOKEN = ""
DID = "" # leave blank
# TODO prob makes sense to have username here too, and then always assume username + did are populated
# two use cases: library calls login() (swap to a class later) and cli user uses a shell variable.
# in either case login() should populate these globals within this file.
# maybe PASSWORD shouldn't hang around, but you have bigger problems if you're relying on python encapsulation for security.

# TODO annotate all requests.get/post with auth header


def login(username, password):
    data = {"identifier": username, "password": password}
    resp = requests.post(
        ATP_HOST + "/xrpc/com.atproto.server.createSession",
        json=data
    )

    global ATP_AUTH_TOKEN
    ATP_AUTH_TOKEN = resp.json().get('accessJwt')
    if ATP_AUTH_TOKEN == None:
        raise ValueError("No access token, is your password wrong?")

    global DID
    DID = resp.json().get("did")

    # TODO
    # global USERNAME

    # global PASSWORD

    return resp

def post_skoot(postcontent, timestamp=None):
    if not timestamp:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
    timestamp = timestamp.isoformat().replace('+00:00', 'Z')

    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}

    data = {
        "collection": "app.bsky.feed.post",
        "$type": "app.bsky.feed.post",
        "repo": "{}".format(DID),
        "record": {
            "$type": "app.bsky.feed.post",
            "createdAt": timestamp,
            "text": postcontent,
        }
    }

    resp = requests.post(
        ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
        json=data,
        headers=headers
    )

    return resp

def get_skoot_by_url(url):
    "https://bsky.social/xrpc/app.bsky.feed.getPostThread?uri=at%3A%2F%2Fdid%3Aplc%3Ascx5mrfxxrqlfzkjcpbt3xfr%2Fapp.bsky.feed.post%2F3jszsrnruws27A"
    "at://did:plc:scx5mrfxxrqlfzkjcpbt3xfr/app.bsky.feed.post/3jszsrnruws27"
    "https://staging.bsky.app/profile/naia.bsky.social/post/3jszsrnruws27"

    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}

    username_of_person_in_link = url.split('/')[-3]
    did_of_person_in_link = resolveHandle(username_of_person_in_link).json().get('did')
    url_identifier = url.split('/')[-1] # the random stuf at the end

    uri = "at://{}/app.bsky.feed.post/{}".format(did_of_person_in_link, url_identifier)

    resp = requests.get(
        ATP_HOST + "/xrpc/app.bsky.feed.getPostThread?uri={}".format(uri),
        headers=headers
    )

    return resp



def reskoot(url):
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

    person_youre_reskooting = resolveHandle(url.split('/')[-3]).json().get('did') # its a DID
    url_identifier = url.split('/')[-1]

    # import pdb; pdb.set_trace()
    skoot_cid = get_skoot_by_url(url).json().get('thread').get('post').get('cid')

    # subject -> uri is the maia one (thing rt'ing, scx)
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    timestamp = timestamp.isoformat().replace('+00:00', 'Z')

    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}

    data = {
        "collection": "app.bsky.feed.repost",
        "repo": "{}".format(DID),
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
        ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
        json=data,
        headers=headers
    )

    # print(data)

    return resp


def delete_skoot(did,rkey):
    data = {"collection":"app.bsky.feed.post","repo":"did:plc:{}".format(did),"rkey":"{}".format(rkey)}
    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
    resp = requests.post(
        ATP_HOST + "/xrpc/com.atproto.repo.deleteRecord",
        json = data,
        headers=headers
    )
    return resp

def resolveHandle(username): # aka getDid
    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
    resp = requests.get(
        ATP_HOST + "/xrpc/com.atproto.identity.resolveHandle?handle={}".format(username),
        headers=headers
    )
    return resp

def get_car_file(did_of_car_to_fetch=None):
    '''
    Get a .car file contain all skoots.
    TODO is there a putRepo?
    TODO save to file
    '''

    if did_of_car_to_fetch == None:
        did_of_car_to_fetch = DID

    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}

    resp = requests.get(
        ATP_HOST + "/xrpc/com.atproto.sync.getRepo?did={}".format(did_of_car_to_fetch),
        headers = headers
    )

    return resp

def get_latest_skoot(accountname):
    return get_latest_n_skoots(accountname, 1)

def get_latest_n_skoots(username, n=5):
    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
    resp = requests.get(
        ATP_HOST + "/xrpc/app.bsky.feed.getAuthorFeed?actor={}&limit={}".format(username, n),
        headers = headers
    )

    return resp

if __name__ == "__main__":
    # This code will only be executed if the script is run directly
    login(os.environ.get("BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
    # f = get_latest_n_skoots('klatz.co',1).content
    # print(f)
    resp = reskoot("https://staging.bsky.app/profile/naia.bsky.social/post/3jszsrnruws27")
    # resp = get_car_file()
    import pdb; pdb.set_trace()



# resp = login()
# post("test post")
