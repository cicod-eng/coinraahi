#!/usr/bin/env python3
"""Submit URLs to Bing IndexNow for coinraahi.com.

Usage:
  python3 indexnow.py https://coinraahi.com/page-1/ https://coinraahi.com/page-2/
"""
import json, sys, urllib.request

HOST = "coinraahi.com"
KEY = "c70bd4b2936b45a48f19d97fffd1bf57"
ENDPOINT = "https://api.indexnow.org/indexnow"


def submit(urls):
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req) as r:
        print(r.status, r.read().decode())


if __name__ == "__main__":
    urls = [u for u in sys.argv[1:] if u.startswith("https://")]
    if not urls:
        print("usage: python3 indexnow.py <url1> <url2> ...", file=sys.stderr)
        sys.exit(1)
    submit(urls)
