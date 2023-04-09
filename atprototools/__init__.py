import requests
import datetime
import os

ATP_HOST = "https://bsky.social"
ATP_AUTH_TOKEN = ""
DID = "" # leave blank

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

def delete_skoot(did,rkey):
    data = {"collection":"app.bsky.feed.post","repo":"did:plc:{}".format(did),"rkey":"{}".format(rkey)}
    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
    resp = requests.post(
        ATP_HOST + "/xrpc/com.atproto.repo.deleteRecord",
        json = data,
        headers=headers
    )
    return resp

def get_latest_skoot(accountname):
    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
    resp = requests.get(
        ATP_HOST + "/xrpc/app.bsky.feed.getAuthorFeed?actor={}&limit=1".format(accountname),
        headers = headers
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
    resp = get_car_file()
    import pdb; pdb.set_trace()



# resp = login()
# post("test post")
