## atprototools

Easy-to-use and ergonomic library for interacting with bluesky, packaged so you can `pip
install atprototools` and go.

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
session.post_skoot("hello world from atprototools")
# session.post_skoot("here's an image!", "path/to/your/image")
latest_skoots = session.get_latest_n_skoots('klatz.co',1).content
carfile = session.get_car_file().content
```

PEP8 formatted; use autopep8.

### Running tests

```
# clone repo
cd atprototools
python -m unittest
```

### changelog

- 0.0.12: Set your own ATP_HOST! get_skyline. Thanks Shreyan.
- 0.0.11: images! in post_skoot.
- 0.0.10: follow, getProfile
- 0.0.9: move everything into a session class
- 0.0.8: get_skoot_by_url, reskoot
- 0.0.7: getRepo (car files) and get_latest_n_skoots

### Thanks to 

- alice
- [sirodoht](https://github.com/sirodoht)
