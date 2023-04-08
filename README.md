## atprototools

A couple of functions for making/deleting posts, packaged so you can `pip
install` and go.

Usage:

```bash
pip install atprototools
export BSKY_USERAME="yourname.bsky.social"
export PASSWORD="yourpassword"
```

```python
import atprototools as atpt
import os

USERNAME = os.environ.get("BSKY_USERNAME")
PASSWORD = os.environ.get("PASSWORD")

atpt.login(USERNAME, PASSWORD)
atpt.post_skoot("hello world from atprototools")
```

PEP8 formatted; use autopep8.
