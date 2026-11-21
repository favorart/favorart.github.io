#!/usr/bin/env python3
"""Check that links in the texts of the built site lead to the reader's language.

Usage: python tools/check_link_langs.py [_site] [--wiki] [--strict]
For every Writing page in every language it looks at the links in the text (article.prose) and reports:
  site      a link to a page of this site in another language, while the page exists in the reader's
            language (or, failing that, in English);
  own-repo  a link to a file in the owner's GitHub repo or to a LinkedIn post that is itself a page here;
  wiki      (--wiki, asks the Wikipedia API, cached in tools/.cache/wiki-langlinks.json) a Wikipedia
            article in another language while one exists in the reader's language (or, failing that,
            in English).
Rule: the reader's language first, then the site's own page, then English. Links to other versions of
the same text (the language line at the top: [English](article.md) · [Русский](article.ru.md)) are fine.
Exit code 1 with --strict if anything is reported.
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://favorart.github.io"
LANGS = ["en", "es", "ru", "sr", "uz"]  # en at the root, the others under /<lang>/
CACHE = os.path.join(ROOT, "tools", ".cache", "wiki-langlinks.json")
# links in another language on purpose: url -> why
EXCEPTIONS = {
    "https://en.wikipedia.org/wiki/Penney%27s_game": "only the English article covers Conway's leading numbers",
    "https://en.wikipedia.org/wiki/Julian_calendar": "uz.wikipedia 'Yulian taqvimi' is a one-line stub",
}


class Links(HTMLParser):
    """Collects <a href> inside <article class="prose">."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.links, self.in_a = 0, [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.depth:
            if tag == "article":
                self.depth += 1
            if tag == "a" and a.get("href"):
                self.links.append([a["href"], a.get("hreflang"), ""])
                self.in_a = True
        elif tag == "article" and "prose" in (a.get("class") or "").split():
            self.depth = 1

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_a = False
        if self.depth and tag == "article":
            self.depth -= 1

    def handle_data(self, data):
        if self.depth and self.in_a and len(self.links[-1][2]) < 60:
            self.links[-1][2] += data


def split_lang(path):
    """'/es/writing/x/' -> ('es', '/writing/x/'); '/writing/x/' -> ('en', '/writing/x/')."""
    m = re.match(r"^/(es|ru|sr|uz)(/.*)$", path)
    return (m.group(1), m.group(2)) if m else ("en", path)


def page_exists(site, lang, rest):
    p = os.path.join(site, *(([] if lang == "en" else [lang]) + rest.strip("/").split("/")), "index.html")
    return os.path.isfile(p)


def own_pages():
    """(repo, path) of a source file / post URL -> site path (without a language prefix)."""
    import yaml
    out = {}
    with open(os.path.join(ROOT, "sources.yml"), encoding="utf-8") as f:
        man = yaml.safe_load(f)
    for key, sec in (("articles", "writing"), ("courses", "courses")):
        for e in man.get(key) or []:
            for p in [e["path"]] + list((e.get("translation_files") or {}).values()):
                out[("gh", e["repo"], p)] = "/%s/%s/" % (sec, e["slug"])
    posts = os.path.join(ROOT, "posts")
    for d in os.listdir(posts):
        idx = os.path.join(posts, d, "index.md")
        if os.path.isfile(idx):
            with open(idx, encoding="utf-8") as f:
                m = re.search(r"^original_url:\s*(\S+)", f.read(), re.M)
            if m:
                out[("li", m.group(1).split("?")[0].rstrip("/"))] = "/writing/%s/" % re.sub(r"^\d{4}-\d{2}-", "", d)
    return out


class Wiki:
    def __init__(self):
        try:
            with open(CACHE, encoding="utf-8") as f:
                self.cache = json.load(f)
        except (OSError, ValueError):
            self.cache = {}

    def langlinks(self, lang, title):
        """{lang: title} of the same article in other languages (plus lang itself)."""
        key = "%s:%s" % (lang, title)
        if key not in self.cache:
            q = urllib.parse.urlencode({"action": "query", "prop": "langlinks", "titles": title, "redirects": 1,
                                        "lllimit": "max", "format": "json", "formatversion": 2})
            req = urllib.request.Request("https://%s.wikipedia.org/w/api.php?%s" % (lang, q),
                                         headers={"User-Agent": "site-link-lang-check/1.0"})
            for attempt in range(6):
                try:
                    with urllib.request.urlopen(req, timeout=30) as r:
                        pages = json.load(r)["query"]["pages"]
                    break
                except urllib.error.HTTPError as e:
                    if e.code != 429 or attempt == 5:
                        raise
                    time.sleep(2 ** attempt * 2)
            res = {} if pages[0].get("missing") else {lang: pages[0]["title"]}
            for ll in pages[0].get("langlinks", []):
                res[ll["lang"]] = ll["title"]
            self.cache[key] = res
            time.sleep(0.5)
        return self.cache[key]

    def save(self):
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=0, sort_keys=True)


def main():
    args = sys.argv[1:]
    use_wiki, strict = "--wiki" in args, "--strict" in args
    args = [a for a in args if not a.startswith("--")]
    site = os.path.abspath(args[0] if args else os.path.join(ROOT, "_site"))
    own, wiki = own_pages(), (Wiki() if use_wiki else None)
    problems = []
    for lang in LANGS:
        base = os.path.join(site, *([] if lang == "en" else [lang]), "writing")
        if not os.path.isdir(base):
            continue
        for slug in sorted(os.listdir(base)):
            page = os.path.join(base, slug, "index.html")
            if not os.path.isfile(page):
                continue
            with open(page, encoding="utf-8") as f:
                p = Links()
                p.feed(f.read())
            where = "%s/writing/%s/" % ("" if lang == "en" else "/" + lang, slug)
            for href, hreflang, text in p.links:
                url = html.unescape(href)
                if url in EXCEPTIONS:
                    continue
                text = " ".join(text.split())[:50]
                u = urllib.parse.urlsplit(url)
                path = u.path
                if u.netloc in ("favorart.github.io", ""):
                    if not path.startswith("/") or not re.match(r"^(/(es|ru|sr|uz))?/(writing|courses|projects)/[^/]+/$", path):
                        continue
                    tl, rest = split_lang(path)
                    if rest == "/writing/%s/" % slug:
                        continue  # another version of this very text
                    if tl != lang:
                        if page_exists(site, lang, rest):
                            problems.append((where, "site", text, url, "есть на языке страницы: %s" % (
                                rest if lang == "en" else "/" + lang + rest)))
                        elif tl != "en" and page_exists(site, "en", rest):
                            problems.append((where, "site", text, url, "нет на языке страницы, есть английская: " + rest))
                    continue
                m = re.match(r"^/favorart/([^/]+)/blob/[^/]+/(.+)$", path) if u.netloc == "github.com" else None
                if m and ("gh", "favorart/" + m.group(1), m.group(2)) in own:
                    rest = own[("gh", "favorart/" + m.group(1), m.group(2))]
                    problems.append((where, "own-repo", text, url, "есть страница на сайте: %s" % (
                        rest if lang == "en" else "/" + lang + rest)))
                    continue
                if u.netloc.endswith("linkedin.com"):
                    key = ("li", (u.scheme + "://" + u.netloc + path).rstrip("/"))
                    if key in own:
                        problems.append((where, "own-repo", text, url, "пост есть на сайте: " + own[key]))
                    continue
                m = re.match(r"^([a-z-]+)(?:\.m)?\.wikipedia\.org$", u.netloc)
                if wiki and m and path.startswith("/wiki/"):
                    wl, title = m.group(1), urllib.parse.unquote(path[len("/wiki/"):]).replace("_", " ")
                    if wl == lang:
                        continue
                    try:
                        ll = wiki.langlinks(wl, title)
                    except Exception as e:  # network trouble: report, don't stop
                        problems.append((where, "wiki", text, url, "не удалось проверить: %s" % e))
                        continue
                    if lang in ll:
                        problems.append((where, "wiki", text, url, "есть на языке страницы: https://%s.wikipedia.org/wiki/%s"
                                         % (lang, urllib.parse.quote(ll[lang].replace(" ", "_")))))
                    elif wl != "en" and "en" in ll:
                        problems.append((where, "wiki", text, url, "нет на языке страницы, есть английская: "
                                         "https://en.wikipedia.org/wiki/%s" % urllib.parse.quote(ll["en"].replace(" ", "_"))))
    if wiki:
        wiki.save()
    for where, kind, text, url, why in problems:
        print("%s\t%s\t%s\t%s\t%s" % (where, kind, text, url, why))
    print("%d links to fix" % len(problems), file=sys.stderr)
    sys.exit(1 if strict and problems else 0)


if __name__ == "__main__":
    main()
