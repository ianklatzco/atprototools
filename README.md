## atprototools

A couple of functions for making/deleting posts, packaged so you can `pip
install` and go.

Usage:

```bash
pip install atprototools
export BSKY_USERNAME="yourname.bsky.social"
export BSKY_PASSWORD="yourpassword"
```

```python
import atprototools as atpt
import os

USERNAME = os.environ.get("BSKY_USERNAME")
PASSWORD = os.environ.get("PASSWORD")

atpt.login(USERNAME, PASSWORD)
atpt.post_skoot("hello world from atprototools")
latest_skoots = atpt.get_latest_n_skoots('klatz.co',1).content
carfile = atpt.get_car_file().content
```

PEP8 formatted; use autopep8.

### changelog

- 0.0.8: get_skoot_by_url, reskoot
- 0.0.7: getRepo (car files) and get_latest_n_skoots

### Thanks to 

- alice
- [sirodoht](https://github.com/sirodoht)
