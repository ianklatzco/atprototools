## atprototools

Easy-to-use and ergonomic library for interacting with bluesky, <br>
packaged so you can `pip install atprototools` and go.

Usage:

```bash
pip install atprototools
export BSKY_USERNAME="yourname.bsky.social"
export BSKY_PASSWORD="yourpassword"
```

```python
from atprototools import Session
import os

USERNAME = os.environ.get("BSKY_USERNAME")
PASSWORD = os.environ.get("BSKY_PASSWORD")

session = Session(USERNAME, PASSWORD)

# make a text post
resp = session.post_bloot("hello world from atprototools")

# post an image
# session.post_bloot("here's an image!", "path/to/your/image")

# get bloots/posts
latest_bloot = session.get_latest_n_bloots('klatz.co',1).content

# get archive
# carfile = session.get_car_file().content

# reply to a post
#   Get first post details for replying to, you can also reply to other posts
#   from getting bloots other ways
# Using "hello world" bloot from above:
first_post = resp.json()
# Create reply_ref:
# - root is the highest up original post
# - parent is the comment you want to reply to directly
# if you want to reply to root make both the same
reply_ref = {"root": first_post, "parent": first_post}
session.post_bloot("this is the reply", reply_to=reply_ref)
# TODO write a test for replies
```


PEP8 formatted; use autopep8.

### Running tests

```
# clone repo
cd atprototools
python -m unittest
```

### changelog

- 0.0.16: replies! added to post_bloot, thanks to Jxck-S
- 0.0.15: get_bloot_by_url switched to getPosts instead of getPostThread
- 0.0.14: refactoring for cbase talk
- 0.0.13: register(), thanks Chief!
- 0.0.12: Set your own ATP_HOST! get_skyline. Thanks Shreyan.
- 0.0.11: images! in post_bloot.
- 0.0.10: follow, getProfile
- 0.0.9: move everything into a session class
- 0.0.8: get_bloot_by_url, rebloot
- 0.0.7: getRepo (car files) and get_latest_n_bloots

### Thanks to 

- alice
- [sirodoht](https://github.com/sirodoht)
