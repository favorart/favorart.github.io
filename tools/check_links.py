#!/usr/bin/env python3
"""Check the built site for broken local links/images and missing in-page anchors.

Usage: python tools/check_links.py [_site] [--external]
  --external  also request absolute URLs into the owner's GitHub repos
              (raw.githubusercontent.com/favorart, github.com/favorart) produced by link rewriting
Exit code 1 if anything is broken.
"""
import html
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ATTR_RE = re.compile(r'\b(href|src)\s*=\s*(["\'])(.*?)\2', re.S)
ID_RE = re.compile(r'\bid\s*=\s*(["\'])(.*?)\1')
OWN = ("https://raw.githubusercontent.com/favorart/", "https://github.com/favorart/")


def target_file(site, page, url_path):
    if url_path.startswith("/"):
        p = os.path.join(site, url_path.lstrip("/"))
    else:
        p = os.path.join(os.path.dirname(page), url_path)
    p = os.path.normpath(urllib.parse.unquote(p))
    if url_path.endswith("/") or os.path.isdir(p):
        p = os.path.join(p, "index.html")
    return p


def head_ok(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "site-link-check"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status < 400
        except urllib.error.HTTPError as e:
            if method == "GET":
                return e.code < 400
        except OSError:
            if method == "GET":
                return False
    return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    external = "--external" in sys.argv
    site = os.path.abspath(args[0] if args else "_site")
    pages = [os.path.join(d, f) for d, _, fs in os.walk(site) for f in fs if f.endswith(".html")]
    ids = {}
    for p in pages:
        with open(p, encoding="utf-8") as f:
            ids[os.path.normpath(p)] = {html.unescape(m.group(2)) for m in ID_RE.finditer(f.read())}
    errors, checked, ext_urls = [], 0, set()
    for p in pages:
        with open(p, encoding="utf-8") as f:
            text = f.read()
        rel = os.path.relpath(p, site)
        for m in ATTR_RE.finditer(text):
            url = html.unescape(m.group(3)).strip()
            if url.startswith(OWN):
                ext_urls.add((rel, url))
                continue
            if not url or url.startswith("//") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url):
                continue
            checked += 1
            parts = urllib.parse.urlsplit(url)
            target = target_file(site, p, parts.path) if parts.path else os.path.normpath(p)
            if not os.path.isfile(target):
                errors.append("%s: missing %s" % (rel, url))
            elif parts.fragment and target.endswith(".html"):
                if urllib.parse.unquote(parts.fragment) not in ids.get(target, set()):
                    errors.append("%s: missing anchor %s" % (rel, url))
    if external:
        for rel, url in sorted(ext_urls):
            if not head_ok(url.split("#")[0]):
                errors.append("%s: external %s" % (rel, url))
    print("pages: %d, local links checked: %d, own-repo links%s: %d" % (
        len(pages), checked, " checked" if external else " (not checked)", len(ext_urls)))
    for e in errors:
        print("BROKEN", e)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
