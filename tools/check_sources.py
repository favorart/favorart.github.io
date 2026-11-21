#!/usr/bin/env python3
"""Are the publishers' PDFs of the papers still online?

Checks every `pdf:` of `papers:` in sources.yml and keeps the result in papers/source-status.yml:
    <slug>: {url: ..., fails: <failed checks in a row>, since: <date the current state began>}
build.py switches a paper's links to its saved text (papers/<slug>.md) once `fails` reaches
SOURCE_GONE_AFTER, and back as soon as the PDF answers again. Run weekly by .github/workflows/source-check.yml;
the file only changes when a state changes, so a quiet week makes no commit.

Usage: python tools/check_sources.py [--dry-run]
"""
import datetime as dt
import os
import sys
import time
import urllib.error
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, "papers", "source-status.yml")
UA = "Mozilla/5.0 (compatible; favorart.github.io source check)"


def alive(url, tries=3):
    """The URL answers 200 with a PDF (by type or by its first bytes)."""
    why = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                head = r.read(1024)
                ctype = r.headers.get("Content-Type", "")
                if r.status == 200 and ("pdf" in ctype.lower() or head.startswith(b"%PDF")):
                    return True, "ok"
                why = "HTTP %s, %s" % (r.status, ctype or "no type")
        except urllib.error.HTTPError as e:
            why = "HTTP %s" % e.code
            if e.code in (404, 410):
                break
        except (urllib.error.URLError, OSError) as e:
            why = str(getattr(e, "reason", e))
        time.sleep(3 * (i + 1))
    return False, why


def main():
    dry = "--dry-run" in sys.argv
    with open(os.path.join(ROOT, "sources.yml"), encoding="utf-8") as f:
        papers = (yaml.safe_load(f) or {}).get("papers") or []
    status = {}
    if os.path.isfile(STATUS):
        with open(STATUS, encoding="utf-8") as f:
            status = yaml.safe_load(f) or {}
    today = dt.date.today().isoformat()
    new = {}
    for e in papers:
        if not e.get("pdf"):
            continue
        ok, why = alive(e["pdf"])
        old = status.get(e["slug"]) or {}
        fails = 0 if ok else (int(old.get("fails", 0)) + 1 if old.get("url") == e["pdf"] else 1)
        same = old.get("url") == e["pdf"] and (old.get("fails", 0) == 0) == (fails == 0)
        new[e["slug"]] = {"url": e["pdf"], "fails": fails, "since": old.get("since", today) if same else today}
        print("%-40s %s%s" % (e["slug"], "ok" if ok else "FAIL (%s)" % why, "" if ok else ", %d in a row" % fails))
    if new == status:
        print("no changes")
        return
    if dry:
        print("changed (dry run, not written)")
        return
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    with open(STATUS, "w", encoding="utf-8", newline="\n") as f:
        f.write("# written by tools/check_sources.py: is the publisher's PDF of each paper online?\n")
        yaml.safe_dump(new, f, allow_unicode=True, sort_keys=True)
    print("written:", os.path.relpath(STATUS, ROOT))


if __name__ == "__main__":
    main()
