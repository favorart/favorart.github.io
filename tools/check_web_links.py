#!/usr/bin/env python3
"""Request every external link of the built site and report the broken ones.

Usage: python tools/check_web_links.py [_site] [--strict]
Each unique http(s) URL from href/src on every page is requested once (GET, browser-like User-Agent, redirects
followed). Reported: HTTP status >= 400, network errors, and redirects that land on another site (a domain that
expired or a page moved away). Sites behind a login (LinkedIn and the like answer bots with 999/403) are listed
in LOGIN and skipped. Output: one line per problem, "status  url  (pages that link to it)".
Exit code 1 with --strict if anything is reported.
"""
import collections
import concurrent.futures
import html
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTR_RE = re.compile(r'\b(?:href|src)\s*=\s*(["\'])(https?://.*?)\1', re.S)
LOGIN = ("linkedin.com", "lnkd.in", "vk.com", "vk.ru", "facebook.com", "instagram.com", "x.com", "twitter.com")
SKIP = ("favorart.github.io", "fonts.googleapis.com", "fonts.gstatic.com", "gc.zgo.at", "goatcounter.com",
        "cdn.jsdelivr.net", "localhost")
# answer scripts with 403/307 but open in a browser (checked by hand): reported as "bot", not as broken
BOT_WALL = ("stackoverflow.com", "vk.company")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0 Safari/537.36")


def host_of(url):
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def on(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)


def base_domain(host):
    parts = host.split(".")
    return ".".join(parts[-3:] if len(parts) > 2 and len(parts[-2]) <= 3 else parts[-2:])


CDN = ("githubusercontent.com", "amazonaws.com", "github.io", "githubassets.com",  # GitHub file storage
       "youtube.com")  # youtu.be short links


def iri_to_uri(url):
    u = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((u.scheme, u.netloc.encode("idna").decode(), urllib.parse.quote(u.path, safe="/%:@!$&'()*+,;=-._~"),
                                    urllib.parse.quote(u.query, safe="=&%+/:,;@!$'()*-._~"), ""))


def check(url):
    req = urllib.request.Request(iri_to_uri(url), headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.8",
                                               "Accept-Language": "en,ru;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            final = r.geturl()
            if base_domain(host_of(final)) != base_domain(host_of(url)) and not on(host_of(final), CDN):
                return "moved", "-> " + final
            return None, None
    except urllib.error.HTTPError as e:
        if on(host_of(url), BOT_WALL) and e.code in (403, 307, 429):
            return None, None
        return str(e.code), ""
    except Exception as e:  # DNS, TLS, timeout
        return "error", "%s: %s" % (type(e).__name__, e)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    site = os.path.abspath(args[0] if args else os.path.join(ROOT, "_site"))
    where = collections.defaultdict(set)
    for dirpath, _, files in os.walk(site):
        for name in files:
            if name.endswith(".html"):
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                page = "/" + os.path.relpath(dirpath, site).replace(os.sep, "/").strip(".") + "/"
                for _, url in ATTR_RE.findall(text):
                    url = html.unescape(url).split("#")[0]
                    h = host_of(url)
                    if h and not on(h, SKIP) and not on(h, LOGIN):
                        where[url].add(page.replace("//", "/"))
    problems = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for url, (status, note) in zip(where, pool.map(check, list(where))):
            if status:
                problems.append((status, url, note))
    for status, url, note in sorted(problems):
        pages = sorted(where[url])
        print("%s\t%s\t%s\t(%d pages: %s)" % (status, url, note, len(pages), " ".join(pages[:3])))
    print("%d external URLs checked, %d problems" % (len(where), len(problems)), file=sys.stderr)
    sys.exit(1 if strict and problems else 0)


if __name__ == "__main__":
    main()
