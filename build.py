#!/usr/bin/env python3
"""Static site generator for favorart.github.io.

Inputs
  content/home.<lang>.html  home page body (CV) per language
  i18n/<lang>.yml           UI strings per language (+ URL prefix: "" = root, "/ru", ...)
  templates/*.html          base layout and partials (string.Template, $placeholders)
  assets/site.css           the one stylesheet (Pygments code colours are appended)
  posts/*/index.md          LinkedIn posts and the site's own articles (no original_url): front matter + Markdown
  sources.yml               external articles/courses, fetched from other public repos
  covers/<slug>/            cover options for external content
  projects/<slug>/          projects: project.yml (name, links, date, cover) + <lang>.md (tagline/summary/kind + page text)

Output: _site/  (deployed by .github/workflows/pages.yml)

Usage: python build.py [--out DIR] [--offline]
  --offline  do not fetch external repos (placeholder bodies; for quick local previews)

Design lives only in templates/ and assets/site.css; this file is content logic.
"""
import argparse
import datetime as dt
import glob
import hashlib
import html
import os
import posixpath
import re
import shutil
import string
import time
import urllib.error
import urllib.parse
import urllib.request

import markdown
import yaml
from pygments.formatters import HtmlFormatter

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://favorart.github.io"
LICENSE_URL = "https://github.com/favorart/favorart.github.io/blob/main/LICENSE"
DEFAULT_LANG = "en"
LANG_ORDER = ["en", "es", "ru", "sr", "uz"]  # order in the language switcher
LANGS = {}  # filled in main(): code -> i18n dict
PAPERS = []  # paper items, for the publication links in the CV
HOME_LATEST = 2  # cards per section on the home page
# GoatCounter site code (https://<code>.goatcounter.com): cookie-free visit counter.
# Empty string disables the counter. count.js itself ignores localhost and file:// views.
GOATCOUNTER_CODE = os.environ.get("GOATCOUNTER_CODE", "favorart")
# Web3Forms access key for the contact form (https://web3forms.com, created by e-mail, no account). It is public by
# design: it only tells Web3Forms which inbox to deliver to and does not reveal the address. Empty = form hidden,
# the LinkedIn fallback is shown instead.
CONTACT_FORM_KEY = os.environ.get("CONTACT_FORM_KEY", "")
RASTER = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif")
IMAGE_EXT = RASTER + (".svg",)
# content sections: manifest key -> URL segment
SECTIONS = {"articles": "writing", "courses": "courses"}
ALL_SECTIONS = list(SECTIONS.values()) + ["projects"]  # every list page; projects come from projects/, not sources.yml
NAV_OF = {"writing": "writing", "courses": "teaching", "projects": "projects"}  # side-navigation item of a section

esc = html.escape


def fail(msg):
    raise SystemExit("build error: " + msg)


# ---------------------------------------------------------------- cache busting
# Local CSS / favicon / cover URLs get ?v=<8 hex of sha256 of the file>, so browsers never pair new HTML
# with a stale cached file. The stylesheet's version is set in main() from its generated text.
ASSET_V = {}
TRANSLATIONS = {}  # (section, slug, lang) -> translation, filled in main() by load_translations()


def file_v(path):
    if path not in ASSET_V:
        with open(path, "rb") as f:
            ASSET_V[path] = hashlib.sha256(f.read()).hexdigest()[:8]
    return ASSET_V[path]


def versioned(url, path):
    return "%s?v=%s" % (url, file_v(path)) if path and os.path.isfile(path) else url


def asset_url(name):
    """/assets/<name>?v=..."""
    if name == "site.css":
        return "/assets/site.css?v=" + ASSET_V["site.css"]
    return versioned("/assets/" + name, os.path.join(ROOT, "assets", name))


def cover_file(item, url):
    """Local file behind a cover URL of an item (its post folder or covers/<slug>/)."""
    d = item.get("options_dir") or item.get("folder")
    return os.path.join(d, os.path.basename(url)) if d and url else None


# ---------------------------------------------------------------- templates & strings

_templates = {}


def tpl(_name, **values):
    if _name not in _templates:
        with open(os.path.join(ROOT, "templates", _name + ".html"), encoding="utf-8") as f:
            _templates[_name] = string.Template(f.read())
    try:
        return _templates[_name].substitute(values)
    except KeyError as e:
        fail("templates/%s.html: no value for $%s" % (_name, e.args[0]))


def load_languages():
    langs = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "i18n", "*.yml"))):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        code = data.get("lang") or os.path.splitext(os.path.basename(path))[0]
        data["prefix"] = (data.get("prefix") or "").rstrip("/")
        if code != DEFAULT_LANG and not data["prefix"]:
            fail("i18n/%s.yml: non-default language needs a prefix like /%s" % (code, code))
        data.setdefault("html_lang", code)
        langs[code] = data
    if DEFAULT_LANG not in langs:
        fail("i18n/%s.yml is required" % DEFAULT_LANG)
    order = {c: n for n, c in enumerate(LANG_ORDER)}
    return dict(sorted(langs.items(), key=lambda kv: (order.get(kv[0], 99), kv[0])))


def S(t, key):
    """Escaped UI string."""
    if key not in t:
        fail("i18n/%s.yml: missing key '%s'" % (t.get("lang"), key))
    return esc(str(t[key]))


# ---------------------------------------------------------------- helpers

def as_date(value, where):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        fail("%s: bad date %r (expected YYYY-MM-DD)" % (where, value))


def loc(value, t):
    """A value from sources.yml that may be given per UI language: {en: ..., ru: ...} -> the one for t."""
    if isinstance(value, dict):
        return value.get(t["lang"]) or value.get(DEFAULT_LANG) or next(iter(value.values()), None)
    return value


def localized(value, t):
    """True when value has its own version for t's UI language (then it is in that language, not the item's)."""
    return isinstance(value, dict) and t["lang"] in value


def text_lang(item, field, t):
    return t["html_lang"] if localized(item.get(field), t) else item["lang"]


def date_text(item, t):
    if item.get("paper") and item["paper"].get("conference"):  # conference abstracts: just the year
        return str(item["year"])
    if item.get("paper"):  # journal issue instead of a date: "vol. 23(1)"
        e = item["paper"]
        return esc(str(t.get("paper_issue", "vol. {v}({i})")).replace("{v}", str(e["volume"])).replace("{i}", str(e["issue"])))
    if item.get("date_label"):
        return esc(str(loc(item["date_label"], t)))
    d = item["date"]
    # one unbreakable unit: "14 Nov 2026" never splits across lines
    return esc(str(t.get("date_format", "{d} {m} {y}")).format(d=d.day, m=t["months"][d.month - 1], y=d.year)).replace(" ", NBSP)


def split_front_matter(text, where):
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", text.replace("\r\n", "\n"), re.S)
    if not m:
        fail("%s: missing YAML front matter" % where)
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        fail("%s: front matter must be a mapping" % where)
    return meta, m.group(2)


def gh_slugify(value, separator="-"):
    """GitHub-like heading ids: keep unicode letters, drop punctuation."""
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value).strip().lower()
    value = re.sub(r"[^\w\- ]", "", value, flags=re.U)
    return value.replace(" ", separator)


LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+\S")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


STRIKE_RE = re.compile(r"(?<!~)~~(?=\S)(.+?)(?<=\S)~~(?!~)")


def gfm_fixups(md_text):
    """Bridge GitHub-flavoured Markdown habits that Python-Markdown does not accept:
    lists/tables/fences right after a paragraph (no blank line), 2-space nested lists."""
    out, in_fence, prev = [], False, ""
    for line in md_text.replace("\r\n", "\n").split("\n"):
        if FENCE_RE.match(line):
            if not in_fence and prev.strip() and not LIST_RE.match(prev):
                out.append("")
            in_fence = not in_fence
        elif not in_fence:
            m = LIST_RE.match(line)
            if m:
                indent = len(m.group(1).expandtabs(4))
                if indent and indent % 4:
                    line = " " * (indent * 2) + line.lstrip()
                if prev.strip() and not LIST_RE.match(prev) and not prev.startswith((" ", "\t")):
                    out.append("")
            elif line.startswith("|") and prev.strip() and not prev.startswith("|"):
                out.append("")
            # a hard line break written as a trailing backslash (Pandoc/CommonMark) -> two trailing spaces
            if line.endswith("\\") and not line.endswith("\\\\"):
                line = line[:-1].rstrip() + "  "
            # ~~strikethrough~~ (GFM), outside inline code
            if "~~" in line and "`" not in line:
                line = STRIKE_RE.sub(lambda m: "<del>%s</del>" % m.group(1), line)
        out.append(line)
        prev = line
    return "\n".join(out)


MERMAID_RE = re.compile(r"^```mermaid[ \t]*\n(.*?)\n```[ \t]*$", re.M | re.S)


def mermaid_blocks(text):
    """```mermaid fences become <pre class="mermaid"> (drawn in the browser by mermaid.js, see templates/base.html)."""
    return MERMAID_RE.sub(lambda m: '\n<pre class="mermaid">%s</pre>\n' % html.escape(m.group(1), quote=False), text)


def render_markdown(text):
    md = markdown.Markdown(
        extensions=["extra", "sane_lists", "codehilite", "toc"],
        extension_configs={
            "codehilite": {"css_class": "codehilite", "guess_lang": False},
            "toc": {"slugify": gh_slugify},
        },
        output_format="html5",
    )
    # pictures in a text load as the reader scrolls to them (a post may carry many heavy GIFs)
    return re.sub(r"<img (?![^>]*\bloading=)", '<img loading="lazy" decoding="async" ', md.convert(mermaid_blocks(gfm_fixups(text))))


def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "site-build"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8")
        except (urllib.error.URLError, OSError) as e:
            last = e
            if isinstance(e, urllib.error.HTTPError) and e.code == 404:
                break
            time.sleep(2 * (i + 1))
    fail("cannot fetch %s: %s" % (url, last))


SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
ATTR_RE = re.compile(r'(\b(?:href|src)\s*=\s*)(["\'])(.*?)\2', re.S)


def rewrite_relative(html_text, entry, page_of):
    """Make relative links/images of external content absolute (pointing at its repo).
    Links to another file that is itself on this site go to that page instead; root-relative links to a page
    of this site (a translation linking to /es/writing/<slug>/) are kept."""
    repo, branch, path = entry["repo"], entry["branch"], entry["path"]
    base_dir = posixpath.dirname(path)
    prefixes = sorted({u["prefix"] for u in LANGS.values() if u["prefix"]}, key=len, reverse=True)
    unprefix = lambda p: next((p[len(x):] for x in prefixes if p.startswith(x + "/")), p)
    pages = {unprefix(p) for p in page_of.values()}
    site_page = lambda p: p.startswith("/") and not p.startswith("//") and unprefix(p) in pages

    def fix(m):
        prefix, quote, url = m.group(1), m.group(2), html.unescape(m.group(3)).strip()
        attr = prefix.strip().split("=")[0].strip().lower()
        if not url or url.startswith(("#", "//")) or SCHEME_RE.match(url):
            return m.group(0)
        parts = urllib.parse.urlsplit(url)
        if site_page(parts.path):  # a page of this site in some language, e.g. /es/writing/<slug>/
            return m.group(0)
        if parts.path.startswith("/"):
            target = parts.path.lstrip("/")
        elif parts.path:
            target = posixpath.normpath(posixpath.join(base_dir, parts.path))
        else:
            target = path
        frag = "#" + parts.fragment if parts.fragment else ""
        query = "?" + parts.query if parts.query else ""
        if attr == "src" or (target.lower().endswith(IMAGE_EXT) and not frag):
            new = "https://raw.githubusercontent.com/%s/%s/%s%s" % (repo, branch, target, query)
        elif (repo, target) in page_of:
            new = page_of[(repo, target)] + frag
        else:
            new = "https://github.com/%s/blob/%s/%s%s%s" % (repo, branch, target, query, frag)
        return "%s%s%s%s" % (prefix, quote, esc(new, quote=True), quote)

    return ATTR_RE.sub(fix, html_text)


TOKEN_RE = re.compile(r"(<[^>]+>)")
BARE_URL_RE = re.compile(r"https?://[^\s<>\"']+")


def short_url(url, limit=42):
    """Readable label for a bare URL: domain + path, trimmed."""
    parts = urllib.parse.urlsplit(url)
    label = (parts.netloc[4:] if parts.netloc.startswith("www.") else parts.netloc) + parts.path.rstrip("/")
    if len(label) > limit:
        label = label[:limit].rsplit("/", 1)[0] + "/…"
    return label


def linkify_bare(html_text):
    """Turn bare URLs in text (not in links/code) into short links."""
    out, skip = [], 0
    for tok in TOKEN_RE.split(html_text):
        if tok.startswith("<"):
            m = re.match(r"<(/?)(a|pre|code)", tok, re.I)
            if m:
                skip += -1 if m.group(1) else 1
            out.append(tok)
        elif skip or "http" not in tok:
            out.append(tok)
        else:
            def link(m):
                url = html.unescape(m.group(0))
                tail = ""
                while url and url[-1] in ".,;:!?)]}":
                    tail, url = url[-1] + tail, url[:-1]
                return '<a href="%s">%s</a>%s' % (esc(url, quote=True), esc(short_url(url)), esc(tail))
            out.append(BARE_URL_RE.sub(link, tok))
    return "".join(out)


# ---------------------------------------------------------------- loading content

def drop_title_line(md, title):
    """A LinkedIn post usually starts with its headline; on the site the headline is the page title, so a first
    paragraph that repeats the title (ignoring case, escapes and punctuation) is not shown twice."""
    norm = lambda x: re.sub(r"[\W_]+", " ", x.replace("\\#", "#")).strip().lower()
    head, sep, rest = md.lstrip("\n").partition("\n\n")
    if norm(head) and norm(head) == norm(str(title)):
        return rest
    return md


def load_posts():
    items = []
    for md_path in sorted(glob.glob(os.path.join(ROOT, "posts", "*", "index.md"))):
        folder = os.path.dirname(md_path)
        name = os.path.basename(folder)
        where = "posts/%s/index.md" % name
        with open(md_path, encoding="utf-8") as f:
            meta, body = split_front_matter(f.read(), where)
        for key in ("title", "date", "summary"):
            if not meta.get(key):
                fail("%s: front matter field '%s' is required" % (where, key))
        # a copied LinkedIn post has source: linkedin + original_url; without them it is the site's own article
        own = not meta.get("original_url")
        if own and meta.get("source") == "linkedin":
            fail("%s: source: linkedin needs original_url" % where)
        slug = str(meta.get("slug") or re.sub(r"^\d{4}-\d{2}(-\d{2})?-", "", name))
        cover = meta.get("cover")
        if cover and not os.path.isfile(os.path.join(folder, cover)):
            fail("%s: cover file '%s' not found next to index.md" % (where, cover))
        card_cover = meta.get("card_cover")  # optional: a different picture for cards (e.g. a portrait photo)
        if card_cover and not os.path.isfile(os.path.join(folder, card_cover)):
            fail("%s: card_cover file '%s' not found next to index.md" % (where, card_cover))
        source_md = body
        body_html = render_markdown(drop_title_line(body, meta["title"]))
        if cover:  # the cover is shown above the title; drop the same picture repeated in the text
            body_html = re.sub(r'<p>\s*<img[^>]*\bsrc="%s"[^>]*>\s*</p>\s*' % re.escape(cover), "", body_html)
        items.append({
            "type": "post", "wtype": "article" if own else "post", "own": own, "section": "writing", "slug": slug,
            "title": str(meta["title"]), "date": as_date(meta["date"], where),
            "date_label": meta.get("date_label"), "lang": meta.get("lang", "ru"),
            "summary": str(meta["summary"]), "kind": meta.get("kind"),
            "original_url": meta.get("original_url"), "tags": meta.get("tags") or [],
            "cover_url": "/writing/%s/%s" % (slug, cover) if cover else None,
            "card_cover_url": "/writing/%s/%s" % (slug, card_cover) if card_cover else None,
            "folder": folder, "options_dir": folder,
            "body_html": mark_link_langs(linkify_bare(body_html)), "subtitle": None, "demo_url": meta.get("demo_url"),
            "list": meta.get("list", True), "home": meta.get("home", True),
            "source_md": source_md, "source_ref": where, "cover_file": cover,
        })
    return items


def load_external(offline):
    path = os.path.join(ROOT, "sources.yml")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f) or {}
    unknown = set(manifest) - set(SECTIONS) - {"papers"}
    if unknown:
        fail("sources.yml: unknown sections %s (known: %s)" % (sorted(unknown), sorted(SECTIONS)))
    entries = [(SECTIONS[key], e) for key in SECTIONS for e in (manifest.get(key) or [])]
    pre_of = lambda code: LANGS[code]["prefix"] if code in LANGS else ""
    # a link to a text that is on this site goes to its page in the text's own language
    page_of = {(e["repo"], e["path"]): "%s/%s/%s/" % (pre_of(e.get("lang", "en")), sec, e["slug"]) for sec, e in entries}
    for sec, e in entries:  # the same text in another language, kept in the repo next to the original
        for code, path in (e.get("translation_files") or {}).items():
            pre = LANGS[code]["prefix"] if code in LANGS else ""
            page_of[(e["repo"], path)] = "%s/%s/%s/" % (pre, sec, e["slug"])
    items = []
    for sec, e in entries:
        where = "sources.yml[%s]" % e.get("slug")
        for key in ("slug", "repo", "branch", "path", "title", "date", "summary"):
            if not e.get(key):
                fail("%s: field '%s' is required" % (where, key))
        cover = e.get("cover")
        if cover and not os.path.isfile(os.path.join(ROOT, cover)):
            fail("%s: cover '%s' not found" % (where, cover))
        item = {
            "type": "external", "wtype": e.get("type", "article"), "section": sec, "slug": e["slug"],
            "title": e["title"], "date": as_date(e["date"], where),
            "date_label": e.get("date_label"), "lang": e.get("lang", "en"),
            "summary": e["summary"], "kind": e.get("kind"),
            "repo": e["repo"], "branch": e["branch"], "path": e["path"],
            "tags": e.get("tags") or [], "demo_url": e.get("demo_url"),
            "cover_url": "/" + cover if cover else None,
            "options_dir": os.path.join(ROOT, os.path.dirname(cover)) if cover else None,
            "list": e.get("list", True), "home": e.get("home", True), "subtitle": None,
            "provided": tuple(e.get("translation_files") or ()),  # the author's own versions in the repo
        }
        if offline:
            item["body_html"] = "<p><em>(offline build: content not fetched)</em></p>"
        else:
            raw = fetch("https://raw.githubusercontent.com/%s/%s/%s" % (e["repo"], e["branch"], e["path"]))
            item["source_md"], item["source_ref"] = raw, "%s@%s:%s" % (e["repo"], e["branch"], e["path"])
            item["page_of"] = page_of
            m = re.match(r"\A\s*#\s+(.+?)\s*#*\s*\n", raw)
            if m:  # the source's own H1 becomes the subtitle; the page H1 is the manifest title
                item["subtitle"], raw = m.group(1).strip(), raw[m.end():]
            item["body_html"] = mark_link_langs(linkify_bare(rewrite_relative(render_markdown(raw), item, page_of)))
            item["author_versions"] = {
                code: fetch("https://raw.githubusercontent.com/%s/%s/%s" % (e["repo"], e["branch"], path))
                for code, path in (e.get("translation_files") or {}).items()}
        items.append(item)
    items += [paper_item(e) for e in manifest.get("papers") or []]
    return items


def load_projects():
    """Projects: projects/<slug>/project.yml (name, links, date, cover, demo) and one <lang>.md per UI language
    (front matter tagline / summary / kind, body = the page text). The title everywhere is `name`, the repo name;
    the tagline is the subtitle on the project page. The text is written per language, so every
    language must have its file."""
    items = []
    for d in sorted(glob.glob(os.path.join(ROOT, "projects", "*", "project.yml"))):
        folder, slug = os.path.dirname(d), os.path.basename(os.path.dirname(d))
        where = os.path.relpath(d, ROOT)
        with open(d, encoding="utf-8") as f:
            e = yaml.safe_load(f) or {}
        for key in ("name", "date", "links"):
            if not e.get(key):
                fail("%s: field '%s' is required" % (where, key))
        cover = e.get("cover")
        if cover and not os.path.isfile(os.path.join(ROOT, cover)):
            fail("%s: cover '%s' not found" % (where, cover))
        item = {"type": "project", "wtype": "project", "section": "projects", "slug": slug, "lang": DEFAULT_LANG,
                "date": as_date(e["date"], where), "date_label": e.get("date_label"), "links": e["links"],
                "demo_url": e.get("demo_url"), "tags": [], "list": e.get("list", True), "subtitle": None,
                "cover_url": "/" + cover if cover else None,
                "options_dir": os.path.join(ROOT, os.path.dirname(cover)) if cover else None,
                "title": str(e["name"]), "tagline": {}, "summary": {}, "kind": {}, "body_md": {}, "body_html": ""}
        for code in LANGS:
            path = os.path.join(folder, "%s.md" % code)
            if not os.path.isfile(path):
                fail("%s is missing (a project page is needed in every language)" % os.path.relpath(path, ROOT))
            with open(path, encoding="utf-8") as f:
                meta, body = split_front_matter(f.read(), os.path.relpath(path, ROOT))
            for key in ("tagline", "summary", "kind"):
                if not meta.get(key):
                    fail("%s: front matter field '%s' is required" % (os.path.relpath(path, ROOT), key))
                item[key][code] = meta[key]
            item["body_md"][code] = body
        items.append(item)
    return items


PAPER_LABELS = {"ru": ("Аннотация", "Ключевые слова"), "en": ("Abstract", "Keywords")}


def paper_item(e):
    """A publication: bibliographic record + abstracts, the PDF stays on the publisher's site. Either a journal
    paper (journal, volume, issue, pages) or a conference abstract (conference, section, collection)."""
    where = "sources.yml[papers/%s]" % e.get("slug")
    thesis = bool(e.get("conference"))
    venue = (("conference", "conference_en", "conference_short", "section", "section_en", "collection") if thesis
             else ("journal", "journal_en", "volume", "issue", "pages"))
    for key in ("slug", "title", "authors", "year", "summary") + venue:
        if not e.get(key):
            fail("%s: field '%s' is required" % (where, key))
    if not (e.get("pdf") or e.get("pdf_copy")):
        fail("%s: give 'pdf' (the original online) or 'pdf_copy' (the copy in papers/), or both" % where)
    if e.get("pdf_copy") and not (e["pdf_copy"].startswith("papers/") and os.path.isfile(os.path.join(ROOT, e["pdf_copy"]))):
        fail("%s: pdf_copy '%s' must be a file in papers/" % (where, e["pdf_copy"]))
    alive = bool(e.get("pdf"))  # the publisher's PDF; the copy in papers/ is always offered next to it
    cover = e.get("cover")
    if cover and not os.path.isfile(os.path.join(ROOT, cover)):
        fail("%s: cover '%s' not found" % (where, cover))
    lang, year = e.get("lang", "ru"), int(e["year"])
    if thesis:  # the collection's own record, as the publisher gives it
        ref = "%s %s // %s." % (esc(e["authors"]), esc(e["title"]), esc(str(e["collection"]).rstrip(".")))
    else:
        ref = "%s %s // %s. — %d. — Т. %s, вып. %s. — С. %s." % (
            esc(e["authors"]), esc(e["title"]), esc(e["journal"]), year, e["volume"], e["issue"], esc(str(e["pages"])))
    body = ['<p class="paper-ref" lang="%s">%s</p>' % (esc(lang), ref)]  # buttons: paper_buttons(), per UI language
    # translated: title, summary and the abstract; a talk whose text is lost has only the summary as body
    src = "# %s\n\n%s\n" % (e["title"], e.get("abstract") or e["summary"])
    if e.get("keywords"):
        src += "\n%s: %s\n" % (PAPER_LABELS[lang][1], e["keywords"])
    title = {lang: str(e["title"])}
    summary = {lang: str(e["summary"])}
    if e.get("title_en"):
        title["en"] = str(e["title_en"])
    if e.get("summary_en"):
        summary["en"] = str(e["summary_en"])
    return {
        "source_md": src, "source_ref": "sources.yml papers/%s" % e["slug"],
        "provided": ("en",) if e.get("abstract_en") else (),  # the journal's own English abstract
        "type": "paper", "wtype": "paper", "section": "writing", "slug": e["slug"], "title": title,
        "date": as_date(e.get("date") or "%d-01-01" % year, where), "date_label": str(year) if thesis else "vol. %s(%s)" % (e["volume"], e["issue"]),
        "lang": lang,
        "summary": summary, "kind": None, "journal_short": e.get("conference_short" if thesis else "journal_short", "Intelligent Systems"), "year": year,
        "original_url": e["pdf"] if alive else ("/" + e["pdf_copy"] if e.get("pdf_copy") else e.get("record_url")),
        "original_alive": alive, "tags": [], "demo_url": None, "list": e.get("list", True),
        "cover_url": "/" + cover if cover else None,
        "options_dir": os.path.join(ROOT, os.path.dirname(cover)) if cover else None,
        "subtitle": None, "paper_head": "\n".join(body), "body_html": "\n".join(body), "paper": e,
        "source_line": ("%s, section “%s”, %d" % (e["conference_en"], e["section_en"], year)) if thesis
        else "%s, vol. %s, no. %s, %d, pp. %s" % (e["journal_en"], e["volume"], e["issue"], year, e["pages"]),
    }


# ---------------------------------------------------------------- translations
# One file per text and language, updated in place (older versions live only in git history):
#   translations/<slug>/<lang>.md   front matter `source_hash` = source_hash() of the original it was made from
# If the hash matches the current original the translation is up to date; otherwise the page still shows it,
# with a note that the original has changed since. Only reviewed translations (`reviewed: <date>`) are used.
# tools/translations.py lists what is missing or outdated and creates / re-stamps the files.

TRANSLATABLE_TYPES = ("post", "external", "paper")


def source_hash(text):
    """Version of an original text: sha256 of its normalized Markdown, first 8 hex digits."""
    norm = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().split("\n"))
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:8]


def translatable(item):
    return item["type"] in TRANSLATABLE_TYPES and item["section"] == "writing" and item["list"] and "source_md" in item


def translation_path(item, lang):
    return os.path.join(ROOT, "translations", item["slug"], "%s.md" % lang)  # short: Windows paths max 260 chars


def read_translation(path):
    with open(path, encoding="utf-8") as f:
        meta, body = split_front_matter(f.read(), os.path.relpath(path, ROOT))
    for key in ("title", "summary", "source_hash", "translated"):
        if meta.get("reviewed") and not meta.get(key):
            fail("%s: front matter field '%s' is required" % (os.path.relpath(path, ROOT), key))
    return meta, body


def load_translations(items, langs):
    """Pick, for every translatable item and UI language, the translation to show."""
    report = {"fresh": 0, "stale": 0, "missing": 0}
    for item in items:
        if not translatable(item):
            continue
        cur = source_hash(item["source_md"])
        item["source_version"] = cur
        for code, md in (item.get("author_versions") or {}).items():  # the author's own version: always current
            if code in langs:
                TRANSLATIONS[(item["section"], item["slug"], code)] = {
                    "meta": {"title": loc(item["title"], langs[code]), "summary": loc(item["summary"], langs[code])},
                    "body": md, "fresh": True, "by_author": True}
        for code in langs:
            if code == item["lang"] or code in item.get("provided", ()):
                continue
            best, path = None, translation_path(item, code)
            if os.path.isfile(path):
                meta, body = read_translation(path)
                if meta.get("reviewed"):  # not reviewed yet: never published
                    best = {"meta": meta, "body": body, "fresh": str(meta["source_hash"]) == cur}
            if best:
                TRANSLATIONS[(item["section"], item["slug"], code)] = best
                report["fresh" if best["fresh"] else "stale"] += 1
            else:
                report["missing"] += 1
    return report


def pdf_link(item):
    """The PDF to open: the publisher's, or the copy kept in papers/ when it was never online (None if neither)."""
    e = item["paper"]
    if item["original_alive"]:
        return e["pdf"]
    return "/" + e["pdf_copy"] if e.get("pdf_copy") else None


def paper_buttons(item, t):
    """Two buttons: the publisher's PDF and the copy kept on this site (just the copy if it was never online),
    then the bibliographic record in ISTINA (MSU)."""
    e, lang = item["paper"], item["lang"]
    out = []
    pdf = pdf_link(item)
    if pdf:
        out.append('<a class="btn sun big" href="%s" hreflang="%s">PDF <span class="arr">→</span></a>' % (
            esc(pdf), esc(lang)))
    if item["original_alive"] and e.get("pdf_copy"):
        out.append('<a class="btn big calm" href="/%s" hreflang="%s">%s</a>' % (esc(e["pdf_copy"]), esc(lang), S(t, "paper_copy")))
    note = '<p class="tr-note">%s</p>' % S(t, "paper_offline") if not e.get("pdf") else ""
    record = ('<p class="paper-record"><a href="%s" hreflang="ru">%s</a></p>' % (esc(e["record_url"]), S(t, "paper_record"))
              if e.get("record_url") else "")
    return note + ('<p class="paper-pdf">%s</p>' % " ".join(out) if out else "") + record


def cv_paper_links(t):
    """$plinks_<slug> in the CV: the page, the PDF, the copy on this site, the ISTINA record."""
    out = {}
    for item in PAPERS:
        links = ['<a href="%s">%s →</a>' % (item_url(item, t), S(t, "paper_page"))]
        if pdf_link(item):
            links.append('<a href="%s" hreflang="%s">PDF →</a>' % (esc(pdf_link(item)), esc(item["lang"])))
        if item["original_alive"] and item["paper"].get("pdf_copy"):
            links.append('<a href="/%s" hreflang="%s">%s →</a>' % (esc(item["paper"]["pdf_copy"]), esc(item["lang"]), S(t, "paper_copy")))
        if item["paper"].get("record_url"):
            links.append('<a href="%s" hreflang="ru">%s →</a>' % (esc(item["paper"]["record_url"]), S(t, "paper_istina")))
        out["plinks_" + item["slug"].replace("-", "_")] = " · ".join(links)
    return out


def paper_body(item, t, tr):
    """Record + PDF, then the abstract in the page's language only (the original, a reviewed translation, or the
    journal's English abstract); the original title stays as the subtitle on other-language pages."""
    e, lang = item["paper"], item["lang"]
    lab = lambda tt, k: esc(str(tt.get("paper_" + k) or PAPER_LABELS.get(tt["lang"], PAPER_LABELS["en"])[k == "keywords"]))
    out = [item["paper_head"], paper_buttons(item, t)]

    def block(tt, hl, title, abstract, keywords):
        a = ['<h2 lang="%s">%s</h2>' % (hl, lab(tt, "abstract"))]
        if title:
            a.append('<p lang="%s"><em>%s</em></p>' % (hl, esc(title)))
        a.append('<p lang="%s">%s</p>' % (hl, esc(abstract)))
        if keywords:
            a.append('<p lang="%s"><strong>%s:</strong> %s</p>' % (hl, lab(tt, "keywords"), esc(keywords)))
        return a

    if not e.get("abstract"):  # the text is lost: the record and what is left (the programme page)
        return "\n".join(out + ['<p class="tr-note">%s</p>' % S(t, "paper_no_text")])
    # one abstract per page, in the page's language; the original only when there is no translation
    src_t = LANGS.get(lang, t)
    if t["lang"] == lang:
        out += block(t, src_t["html_lang"], None, e["abstract"], e.get("keywords"))
    elif tr:
        out.append(tr_note(item, tr, t))
        out += block(t, t["html_lang"], None, tr["body"].strip(), tr["meta"].get("keywords"))
    elif t["lang"] == "en" and e.get("abstract_en"):
        out += block(t, "en", None, e["abstract_en"], e.get("keywords_en"))
    else:
        out += block(src_t, src_t["html_lang"], None, e["abstract"], e.get("keywords"))
    return "\n".join(out)


RU_HOSTS = ("habr.com", "vk.com", "vk.ru", "ru.wikipedia.org", "coderszone.info", "intsysjournal.ru", "confhub.ru", "lomonosov.msu.ru", "conf.msu.ru", "istina.msu.ru")
EN_HOSTS = ("en.wikipedia.org", "stackoverflow.com", "docs.python.org", "reddit.com", "blog.cloudflare.com",
            "travisdowns.github.io", "lemire.me", "tutorialspoint.com", "effbot.org", "tcl.tk", "zetcode.com",
            "readthedocs.io", "nmt.edu", "cppreference.com", "isocpp.org", "medium.com", "nvidia.com", "pytorch.org")
A_HREF_RE = re.compile(r'<a\b([^>]*?)\bhref="(https?://[^"]+)"([^>]*)>')


def mark_link_langs(html_text):
    """Links to sites known to be in Russian / English get hreflang="ru" / "en": the page shows a small badge
    unless it is in that language. Explicit marks ({: hreflang=xx } in Markdown) win."""
    def sub(m):
        attrs = m.group(1) + m.group(3)
        if "hreflang=" in attrs:
            return m.group(0)
        host = urllib.parse.urlsplit(html.unescape(m.group(2))).hostname or ""
        on = lambda hosts: any(host == h or host.endswith("." + h) for h in hosts)
        code = "ru" if host.endswith((".ru", ".su")) or on(RU_HOSTS) else "en" if on(EN_HOSTS) else None
        if not code:
            return m.group(0)
        return '<a%s href="%s" hreflang="%s"%s>' % (m.group(1), m.group(2), code, m.group(3))
    return A_HREF_RE.sub(sub, html_text)


def tr_of(item, t):
    return TRANSLATIONS.get((item["section"], item["slug"], t["lang"]))


def tr_body_html(item, tr):
    body = drop_title_line(tr["body"], tr["meta"]["title"]) if item["type"] == "post" else tr["body"]
    body_html = render_markdown(body)
    if item["type"] == "post" and item.get("cover_file"):
        body_html = re.sub(r'<p>\s*<img[^>]*\bsrc="%s"[^>]*>\s*</p>\s*' % re.escape(item["cover_file"]), "", body_html)
    if item["type"] == "external":
        body_html = rewrite_relative(body_html, item, item["page_of"])
    return mark_link_langs(linkify_bare(body_html))  # bare URLs in any text become short clickable links


def tr_note(item, tr, t):
    if tr.get("by_author"):
        return ""
    return _tr_note(item, tr, t)


def _tr_note(item, tr, t):
    """'Translated … Original: <language>' above a translated text, plus a warning when it is out of date."""
    src = LANGS.get(item["lang"])
    link = ('<a href="%s%s" hreflang="%s" lang="%s">%s</a>' % (
        src["prefix"], item_url(item), esc(src["html_lang"]), esc(src["html_lang"]), esc(str(src["name"])))
        if src else "")
    note = '<p class="tr-note">%s %s</p>' % (esc(str(t.get("translation_note", "Translation. Original:"))), link)
    if not tr["fresh"]:
        note += '<p class="tr-note stale">%s</p>' % esc(str(t.get(
            "translation_stale", "The original has been updated since this translation.")))
    return note


# ---------------------------------------------------------------- pages

def lang_nav(t, rel, only_default=False):
    """Language switcher: the same page in every language (rel = path without the language prefix)."""
    links = []
    for code, u in LANGS.items():
        target = rel if not only_default or code == DEFAULT_LANG else "/writing/"
        cur = ' aria-current="true"' if code == t["lang"] else ""
        links.append('<a href="%s%s" hreflang="%s" lang="%s" title="%s"%s>%s</a>' % (
            u["prefix"], target, esc(u["html_lang"]), esc(u["html_lang"]), esc(str(u["name"])), cur, code.upper()))
    return "".join(links)


def lang_menu(t, rel, only_default=False):
    """Phones: the language switcher folded into one 40x40 button that opens a list of full language names."""
    items = []
    for code, u in LANGS.items():
        target = rel if not only_default or code == DEFAULT_LANG else "/writing/"
        cur = ' aria-current="true"' if code == t["lang"] else ""
        items.append('<a href="%s%s" hreflang="%s" lang="%s"%s><b>%s</b> %s</a>' % (
            u["prefix"], target, esc(u["html_lang"]), esc(u["html_lang"]), cur, code.upper(), esc(str(u["name"]))))
    return ('<details class="langdd"><summary aria-label="%s">%s</summary><div class="glass">%s</div></details>'
            % (esc(str(t.get("aria_language", "Language"))), t["lang"].upper(), "".join(items)))


# ---- typography: no short word (preposition, conjunction, article) or number left hanging at a line end ----
SHORT_WORDS = {
    "ru": "в во на к ко с со у о об обо от до по за из изо и а но не ни для без при над под про как что или да же ли бы то это я мы ты он она их его её ещё уже".split(),
    "en": "a an the of to in on at by for and or but is as if it I my we no nor via".split(),
    "es": "a y e o u de el la los las lo un una del al en con por que se no su sus mi ni sin".split(),
    "sr": "i u na sa s za od do po o a ali da ne ni iz k ka bez pri uz kao".split(),
    "uz": "va bu u ham har bir yoki bilan".split(),
}
_SHORT_ALL = sorted({w for ws in SHORT_WORDS.values() for w in ws}, key=len, reverse=True)
_SHORT_RE = re.compile(r"(?<![\w\-.\u02bb\u02bc'\u2019])(%s|\d{1,4}|\u2116|\u00a7)[ \t\n]+(?=[^\s<])"
                       % "|".join(map(re.escape, _SHORT_ALL)), re.IGNORECASE)
_DASH_RE = re.compile(r"(?<=\S)[ \t\n]+(?=\u2014)")  # "word —": the dash never starts a line
_SKIP_RE = re.compile(r"<(pre|code|script|style|textarea|svg|kbd|samp|title)\b.*?</\1>|<[^>]*>", re.S | re.I)
NBSP = "\u00a0"


def typo_nbsp(page_html):
    """Bind short words and numbers to the next word, and a dash to the previous one, with U+00A0 — in text only,
    never inside tags, attributes, code, scripts or styles. Same rule in every language (lists merged): a
    non-breaking space after a short word of another language costs nothing."""
    out, pos = [], 0
    for m in _SKIP_RE.finditer(page_html):
        out.append(_fix_text(page_html[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_fix_text(page_html[pos:]))
    return "".join(out)


def _fix_text(text):
    if not text.strip():
        return text
    return _DASH_RE.sub(NBSP, _SHORT_RE.sub(lambda m: m.group(1) + NBSP, text))


def page(t, title, body, path, description="", lang=None, og_image=None, og_type="website",
         noindex=False, body_class="", og_title=None, section="", canonical=None, only_default=False, crumbs=None):
    rel = path[len(t["prefix"]):] if t["prefix"] and path.startswith(t["prefix"] + "/") else path
    extra = []
    if not noindex and not only_default and canonical is None:
        for code, u in LANGS.items():
            extra.append('<link rel="alternate" hreflang="%s" href="%s">' % (
                esc(u["html_lang"]), esc(SITE_URL + u["prefix"] + rel)))
        extra.append('<link rel="alternate" hreflang="x-default" href="%s">' % esc(SITE_URL + rel))
    if og_image:
        extra.append('<meta property="og:image" content="%s">' % esc(SITE_URL + og_image))
    if noindex:
        extra.append('<meta name="robots" content="noindex">')
    if GOATCOUNTER_CODE:
        # an item page in any UI language counts as one page: /ru/writing/<slug>/ -> /writing/<slug>/
        prefixes = "|".join(re.escape(u["prefix"].strip("/")) for u in LANGS.values() if u["prefix"])
        if prefixes:
            extra.append("<script>window.goatcounter = { path: function (p) { return p.replace("
                         "/^\\/(?:%s)(\\/(?:writing|courses|projects)\\/[^\\/]+\\/)$/, '$1'); } };</script>" % prefixes)
        extra.append('<script data-goatcounter="https://%s.goatcounter.com/count" async '
                     'src="https://gc.zgo.at/count.js"></script>' % esc(GOATCOUNTER_CODE))
    return typo_nbsp(tpl("base", lang=esc(lang or t["html_lang"]), title=esc(title), og_title=esc(og_title or title),
               description=esc(description), og_type=og_type, url=esc(SITE_URL + path),
               aria_language=esc(str(t.get("aria_language", "Language"))),
               aria_sections=esc(str(t.get("aria_sections", "Sections"))),
               canonical=esc(SITE_URL + (canonical or path)), lang_nav=lang_nav(t, rel, only_default),
               og_locale=esc(str(t.get("og_locale", "en_US"))),
               head_extra="\n".join(extra), body_class=body_class, prefix=t["prefix"],
               css_url=asset_url("site.css"), favicon_url=asset_url("favicon.svg"),
               author=S(t, "author"), role_title=S(t, "role_title"), role_skills=S(t, "role_skills"), lang_soon=S(t, "lang_soon"), section=section,
               theme_label=S(t, "theme_label"), theme_auto=S(t, "theme_auto"), theme_light=S(t, "theme_light"),
               theme_dark=S(t, "theme_dark"),
               nav_items=tpl("nav", prefix=t["prefix"], **{k: S(t, k) for k in (
                   "nav_home", "nav_writing", "nav_projects", "nav_teaching", "nav_about", "nav_contact")}),
               footer_contact=S(t, "footer_contact"),
               footer_copy="".join("<span>%s</span>" % str(line).replace("{mit}", esc(LICENSE_URL))
                                   for line in t["footer_copy"]),
               gc_counter=("https://%s.goatcounter.com/counter/" % GOATCOUNTER_CODE) if GOATCOUNTER_CODE else "",
               lang_menu=lang_menu(t, rel, only_default), crumbs=breadcrumbs(t, crumbs),
               year=dt.date.today().year, body=body))


SECTION_PAGE = {"writing": ("/writing/", "nav_writing"), "projects": ("/projects/", "nav_projects"),
                "courses": ("/courses/", "nav_teaching"), "cv": ("/cv/", "nav_about")}


def card_title(item, t):
    """Title of an item as its card shows it in t's language (a reviewed translation's title when there is one)."""
    tr = tr_of(item, t)
    return str(tr["meta"]["title"] if tr else loc(item["title"], t))


def breadcrumbs(t, crumbs):
    """Section bar above the title of every inner page: 'Home › Section › Page' and, on an item page, ← → to the
    neighbouring items of the section (list order). crumbs = (section, current title or None[, item]);
    the last crumb is the current page and is not a link. The side navigation itself always leads to the home page."""
    if not crumbs:
        return ""
    section, current = crumbs[:2]
    item = crumbs[2] if len(crumbs) > 2 else None
    href, key = SECTION_PAGE[section]
    parts = ['<a href="%s/">%s</a>' % (t["prefix"], S(t, "nav_home"))]
    if current:
        parts.append('<a href="%s%s">%s</a>' % (t["prefix"], href, S(t, key)))
        parts.append('<span aria-current="page">%s</span>' % esc(current))
    else:
        parts.append('<span aria-current="page">%s</span>' % S(t, key))
    trail = ('<nav class="crumbs" aria-label="%s"><ol>%s</ol></nav>'
             % (S(t, "aria_breadcrumbs"), "".join("<li>%s</li>" % p for p in parts)))
    steps = ""
    if item is not None:
        links = []
        for rel, arrow in (("prev", "←"), ("next", "→")):
            nb = item.get("nb_" + rel)
            if nb:
                name = esc(card_title(nb, t))
                links.append('<a rel="%s" href="%s" title="%s" aria-label="%s">%s</a>' % (rel, item_url(nb, t), name, name, arrow))
            else:
                links.append('<span aria-hidden="true">%s</span>' % arrow)
        steps = '<span class="steps">%s</span>' % "".join(links)
    return '<div class="ctxbar">%s%s</div>' % (trail, steps)


def item_url(item, t=None):
    """URL of an item's page; with t, the page in that UI language (/ru/writing/<slug>/)."""
    return "%s/%s/%s/" % (t["prefix"] if t else "", item["section"], item["slug"])


def kind_of(item, t):
    """Label of the item: kind, else 'LinkedIn post' for a copied post, 'Article' for the site's own one."""
    if item.get("paper") and item["paper"].get("conference"):  # "Talk abstract · Lomonosov", the year follows
        label = "%s · %s" % (S(t, "type_thesis"), esc(str(loc(item["journal_short"], t))))
    elif item.get("paper"):
        label = "%s · %s · %d" % (S(t, "type_paper"), esc(str(loc(item["journal_short"], t))), item["year"])
    elif item.get("kind"):
        label = esc(str(loc(item["kind"], t)))
    elif item.get("own"):
        label = S(t, "type_article")
    else:
        label = S(t, "linkedin_post")
    return label  # plain text: a link with a language badge here read as "no translation"


def page_cover(item):
    """Cover above the article title: an SVG cover's text-free variant (cover-N-plain.svg) when it exists."""
    url = item.get("cover_url")
    if url and url.endswith(".svg") and item.get("options_dir"):
        plain = os.path.basename(url)[:-4] + "-plain.svg"
        if os.path.isfile(os.path.join(item["options_dir"], plain)):
            return url.rsplit("/", 1)[0] + "/" + plain
    return url


def dark_twin(item, url):
    """Dark-theme twin of an SVG cover: cover-N-dark[-plain].svg if it exists, otherwise the "night" style
    (cover-2[-plain].svg) for the other generated styles. Photos have no twin."""
    if not url or not url.endswith(".svg") or not item.get("options_dir"):
        return None
    name = os.path.basename(url)
    m = re.match(r"cover-(\d+)(-plain)?\.svg$", name)
    if not m:
        return None
    plain = m.group(2) or ""
    for cand in ("cover-%s-dark%s.svg" % (m.group(1), plain), "cover-2%s.svg" % plain):
        if cand != name and os.path.isfile(os.path.join(item["options_dir"], cand)):
            return url.rsplit("/", 1)[0] + "/" + cand
    return None


def lang_cover(item, url, t):
    """cover-N.svg -> cover-N.<lang>.svg when that language version exists (titles in the page's language)."""
    if not url or not t or not url.endswith(".svg") or not item.get("options_dir"):
        return url
    alt = os.path.basename(url)[:-4] + ".%s.svg" % t["lang"]
    if os.path.isfile(os.path.join(item["options_dir"], alt)):
        return url.rsplit("/", 1)[0] + "/" + alt
    return url


def cover_imgs(item, url, cls, lazy=True, t=None):
    """<img> for the cover, plus its dark twin (CSS shows one of them by theme); in t's language if available."""
    lz = ' loading="lazy"' if lazy else ""
    dark = dark_twin(item, url)
    url, dark = lang_cover(item, url, t), lang_cover(item, dark, t)
    html_ = '<img class="%s cover-light%s" src="%s" alt="" width="1200" height="630"%s>' % (
        cls, " has-dark" if dark else "", esc(versioned(url, cover_file(item, url))), lz)
    if dark:
        html_ += '<img class="%s cover-dark" src="%s" alt="" width="1200" height="630" loading="lazy">' % (
            cls, esc(versioned(dark, cover_file(item, dark))))
    return html_


def type_chip(item, t):
    """The one type tag of a Writing item: Post / Article / Paper (courses have none)."""
    if item["section"] != "writing":
        return ""
    thesis = item.get("paper") and item["paper"].get("conference")
    return '<span class="chip type">%s</span>' % S(t, "type_thesis" if thesis else "type_" + item["wtype"])


EYE_SVG = ('<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path fill="none" stroke="currentColor" '
           'stroke-width="2" d="M1.5 12S5.5 5 12 5s10.5 7 10.5 7-4 7-10.5 7S1.5 12 1.5 12z"/>'
           '<circle cx="12" cy="12" r="3" fill="currentColor"/></svg>')


def views_tag(item, t):
    """Placeholder filled by base.html JS from GoatCounter's public counter; stays hidden on failure."""
    if not GOATCOUNTER_CODE:
        return ""
    return ('<span class="views" data-views="%s" title="%s" hidden> · %s <b></b></span>'
            % (esc(item_url(item)), S(t, "views"), EYE_SVG))


TEASERS = {}  # content/teasers.yml: slug -> {lang: teaser}, filled in main()


def load_teasers():
    path = os.path.join(ROOT, "content", "teasers.yml")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    for slug, by_lang in data.items():
        for lang, text in (by_lang or {}).items():
            if len(str(text)) > 140:
                fail("content/teasers.yml: %s/%s is %d characters, the limit is 140 (3 lines of a card)"
                     % (slug, lang, len(str(text))))
    return data


def card(item, t):
    cover, src = "", item.get("card_cover_url") or item.get("cover_url")
    if src:
        cover = cover_imgs(item, src, "cover", t=t)
    badge = ""
    if item.get("demo_url"):
        badge = '<a class="badge" href="%s">%s</a>' % (esc(item["demo_url"]), S(t, "badge_demo"))
    # a teaser in the page's language (short hook, breaks off with "…") replaces the summary on the card
    teaser = str((TEASERS.get(item["slug"]) or {}).get(t["lang"]) or "")
    return tpl("card", href=item_url(item, t), cover=cover, badge=badge, type_chip=type_chip(item, t),
               wtype=esc(item.get("wtype", "")) if item["section"] == "writing" else "", kind=kind_of(item, t), date=date_text(item, t),
               views=views_tag(item, t),
               lang=esc(t["html_lang"] if tr_of(item, t) else text_lang(item, "title", t)),
               title=esc(str(tr_of(item, t)["meta"]["title"] if tr_of(item, t) else loc(item["title"], t))),
               summary_lang=esc(t["html_lang"] if teaser or tr_of(item, t) else text_lang(item, "summary", t)),
               summary=esc(teaser or str(tr_of(item, t)["meta"]["summary"] if tr_of(item, t) else loc(item["summary"], t))))


def article_page(item, t):
    if item.get("own"):  # the site's own article: no original elsewhere
        source_top = ""
    elif item["type"] == "post":
        source_top = '<a href="%s">LinkedIn</a>' % esc(item["original_url"])
    elif item["type"] == "paper":
        e, own = item["paper"], t["lang"] == item["lang"]
        if e.get("conference"):
            line = str(t["thesis_source"]).format(c=e["conference"] if own else e["conference_en"],
                                                  s=e["section"] if own else e["section_en"], y=item["year"])
        else:
            line = str(t.get("paper_source", "{j}, vol. {v}, no. {i}, {y}, pp. {p}")).format(
                j=e["journal"] if own and e.get("journal") else e["journal_en"],
                v=e["volume"], i=e["issue"], y=item["year"], p=e["pages"])
        source_top = ('<a href="%s">%s</a>' % (esc(e["pdf"]), esc(line))) if item["original_alive"] else esc(line)
    elif item["type"] == "project":
        source_top = '%s: %s' % (S(t, "source"), " · ".join('<a href="%s">%s</a>' % (
            esc(link["url"]), esc(str(loc(link["label"], t)))) for link in item["links"]))
    else:
        repo_url = "https://github.com/" + item["repo"]
        file_url = "%s/blob/%s/%s" % (repo_url, item["branch"], item["path"])
        source_top = '%s: <a href="%s">%s</a> · <a href="%s" hreflang="%s">%s</a>' % (
            S(t, "source"), esc(repo_url), esc(item["repo"]), esc(file_url), esc(item["lang"]),
            esc(posixpath.basename(item["path"])))
    demo = ""
    if item.get("demo_url"):
        demo = ' · <a class="demo" href="%s">%s</a>' % (esc(item["demo_url"]), S(t, "live_demo"))
    subtitle = '<p class="subtitle">%s</p>' % esc(item["subtitle"]) if item.get("subtitle") else ""
    back = {"courses": "back_to_courses", "projects": "back_to_projects"}.get(item["section"], "back_to_writing")
    if item["type"] == "post" and not item.get("own"):
        cta = '<a class="btn sun big" href="%s">%s <span class="arr">→</span></a>' % (
            esc(item["original_url"]), S(t, "comment_on_linkedin"))
    else:
        cta = '<a class="btn sun big" href="%s/#contact">%s <span class="arr">→</span></a>' % (
            t["prefix"], S(t, "send_feedback"))
    hero = ""
    if page_cover(item):
        hero = cover_imgs(item, page_cover(item), "hero-cover", lazy=False)
    tr = tr_of(item, t)
    title, title_lang = str(loc(item["title"], t)), text_lang(item, "title", t)
    summary, text_lang_, content, canonical = str(loc(item["summary"], t)), item["lang"], item["body_html"], item_url(item)
    if item["type"] == "paper":
        if tr:
            title, title_lang, summary = str(tr["meta"]["title"]), t["html_lang"], str(tr["meta"]["summary"])
        orig = item["paper"]["title"] if t["lang"] != item["lang"] else None  # original title, in its language
        orig_lang = item["lang"]
        subtitle = '<p class="subtitle" lang="%s">%s</p>' % (esc(orig_lang), esc(orig)) if orig else ""
        content, text_lang_, canonical = paper_body(item, t, tr), t["html_lang"], None
    elif item["type"] == "project":  # written in every language: the page is in t's language
        text_lang_, canonical = t["html_lang"], None
        subtitle = '<p class="subtitle" lang="%s">%s</p>' % (esc(t["html_lang"]), esc(str(item["tagline"][t["lang"]])))
        content = mark_link_langs(linkify_bare(render_markdown(item["body_md"][t["lang"]])))
    elif item["section"] == "courses" and t["lang"] != item["lang"] and t.get("course_lang_note"):
        content = '<p class="tr-note">%s</p>' % S(t, "course_lang_note") + content  # courses are not translated
    elif tr:  # a reviewed translation of the text into this UI language
        title, title_lang, summary = str(tr["meta"]["title"]), t["html_lang"], str(tr["meta"]["summary"])
        text_lang_, canonical = t["html_lang"], None
        subtitle, body_md = "", tr["body"]
        m = re.match(r"\A\s*#\s+(.+?)\s*#*\s*\n", body_md)
        if m and item["type"] == "external":  # the text's own H1 is the subtitle, as on the original's page
            subtitle = '<p class="subtitle">%s</p>' % esc(m.group(1).strip())
            body_md = body_md[m.end():]
        content = tr_note(item, tr, t) + tr_body_html(item, dict(tr, body=body_md))
    kind = kind_of(item, t)
    if item["section"] == "writing":  # the type chip already says it ("Note" chip + "NOTE" label read as a stutter)
        chip = S(t, "type_" + item["wtype"])
        if kind == chip:
            kind = ""
        elif kind.startswith(chip + " · "):
            kind = kind[len(chip) + 3:]
    if subtitle and re.sub(r"<[^>]+>|\W", "", html.unescape(subtitle)).lower() == re.sub(r"\W", "", title).lower():
        subtitle = ""  # the text's own H1 equal to the title would print the same line twice
    body = tpl("article", hero=hero, kind=kind, sep='<span class="sep"> · </span>' if kind else "", date=date_text(item, t), views=views_tag(item, t), lang=esc(text_lang_),
               title=esc(title), title_lang=esc(title_lang),
               subtitle=subtitle, author=S(t, "author"), source_top=" · " + source_top if source_top else "",
               demo=demo, content=content, cta=cta, type_chip=type_chip(item, t),
               back_href="%s/%s/" % (t["prefix"], item["section"]), back_text=S(t, back))
    cover = item.get("cover_url") or ""
    return page(t, "%s — %s" % (title, t["author"]), body, item_url(item, t),
                description=summary,
                canonical=canonical, og_image=cover if cover.lower().endswith(RASTER) else None, og_type="article",
                section=NAV_OF[item["section"]], crumbs=(item["section"], title, item))


def list_page(items, section, t):
    key = section
    cards = "\n".join(card(i, t) for i in items if i["list"] and i["section"] == section)
    filters = ""
    if section == "writing":
        listed = [i for i in items if i["list"] and i["section"] == section]
        counts = {w: sum(1 for i in listed if i["wtype"] == w) for w in ("post", "article", "paper")}
        filters = '<nav class="filters" aria-label="%s" hidden>%s</nav>' % (S(t, "filter_label"), "".join(
            '<a id="%s" href="#%s" data-filter="%s">%s <span class="n">%d</span></a>' % (h, h, f, S(t, "filter_" + h), n)
            for h, f, n in (("all", "", len(listed)), ("posts", "post", counts["post"]),
                            ("articles", "article", counts["article"]), ("papers", "paper", counts["paper"]))))
    body = tpl("list", kicker=S(t, key + "_kicker"), title=S(t, key + "_title"), lead=S(t, key + "_lead"),
               cards=cards, filters=filters)
    return page(t, "%s — %s" % (t[key + "_title"], t["author"]), body, "%s/%s/" % (t["prefix"], section),
                description=t[key + "_description"], section=NAV_OF[section], crumbs=(section, None))


def covers_page(items, t):
    groups, seen = [], set()
    for item in sorted(items, key=lambda i: not i["list"]):  # listed items name the group
        d = item.get("options_dir")
        if not d or d in seen or not item.get("cover_url"):
            continue
        options = sorted(o for o in glob.glob(os.path.join(d, "cover-*.svg")) if re.search(r"cover-\d+\.svg$", o))
        if not options:
            continue
        seen.add(d)
        card_url = item.get("card_cover_url") or item["cover_url"]
        base_url = card_url.rsplit("/", 1)[0]
        chosen = os.path.basename(card_url)
        if item["type"] == "project":
            where = "projects/%s/project.yml → cover" % item["slug"]
        elif item["type"] == "post":
            where = "posts/%s/index.md → %s" % (os.path.basename(item["folder"]),
                                                 "card_cover" if item.get("card_cover_url") else "cover")
        else:
            where = "sources.yml → %s → cover" % item["slug"]
        opts = []
        for n, opt in enumerate(options, 1):
            name = os.path.basename(opt)
            sel = name == chosen
            plain = name[:-4] + "-plain.svg"
            plain_html = ""
            if os.path.isfile(os.path.join(d, plain)):
                plain_html = '<img src="%s" alt="%s" width="1200" height="630" loading="lazy">' % (
                    esc(versioned(base_url + "/" + plain, os.path.join(d, plain))), S(t, "covers_plain"))
            opts.append(tpl("cover_option", selected_class=" selected" if sel else "", plain=plain_html,
                            src=esc(versioned(base_url + "/" + name, opt)), label="%s %d" % (S(t, "covers_option"), n),
                            name=esc(name),
                            selected_tag=' <span class="tag">%s</span>' % S(t, "covers_current") if sel else ""))
        groups.append(tpl("cover_group", title=esc(str(loc(item["title"], t))), set_in=S(t, "covers_set_in"), where=esc(where),
                          chosen=esc(chosen), options="\n".join(opts)))
    # demo of the cover effect on a few real covers (hover, or "Play all")
    with_cover = [i for i in items if i["list"] and (i.get("card_cover_url") or i.get("cover_url"))]
    demos = "\n".join('<div class="fx-tile">%s</div>' % card(i, t) for i in with_cover[:3])
    body = tpl("covers", kicker=S(t, "covers_kicker"), title=S(t, "covers_title"), lead=S(t, "covers_lead"),
               groups="\n".join(groups), mask_title=S(t, "covers_mask_title"), mask_hint=S(t, "covers_mask_hint"),
               mask_demos=demos, play_all=S(t, "covers_play_all"), stop_all=S(t, "covers_stop_all"))
    return page(t, "%s — %s" % (t["covers_title"], t["author"]), body, "/writing/covers/", noindex=True,
                section="writing", only_default=True)


def plural_form(lang, n):
    """CLDR plural category of a whole number n: one / few / many / other."""
    if lang in ("ru", "uk", "be", "sr", "hr", "bs"):
        if n % 10 == 1 and n % 100 != 11:
            return "one"
        if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            return "few"
        return "many" if lang in ("ru", "uk", "be") else "other"
    return "one" if n == 1 else "other"


def all_label(t, key, n):
    """'All {n} courses', or the '<key>_two' wording ('Both courses') when there are exactly two.
    The string may also be a dict of plural forms {one, few, many, other}."""
    if n == 2 and t.get(key + "_two"):
        return S(t, key + "_two")
    if key not in t:
        fail("i18n/%s.yml: missing key '%s'" % (t.get("lang"), key))
    text = t[key]
    if isinstance(text, dict):
        text = text.get(plural_form(t["lang"], n)) or text.get("other")
        if not text:
            fail("i18n/%s.yml: %s has no '%s'/'other' form" % (t["lang"], key, plural_form(t["lang"], n)))
    return esc(str(text)).replace("{n}", str(n))


def fun_roles(t):
    """'Also: <role>' line of the hero; templates/base.html rotates the roles (all shown inline without JS)."""
    roles = [esc(str(r)) for r in t.get("fun_roles") or []]
    if not roles:
        return ""
    spans = "".join('<span class="role">%s</span>' % r for r in roles)
    return ('<p class="also">%s <span class="roles" aria-hidden="true">%s</span>'
            '<span class="sr-only">%s</span></p>' % (S(t, "also"), spans, ", ".join(roles)))


def home_page(items, t):
    path = os.path.join(ROOT, "content", "home.%s.html" % t["lang"])
    with open(path, encoding="utf-8") as f:
        content = string.Template(f.read())
    listed = {sec: [i for i in items if i["list"] and i["section"] == sec] for sec in ALL_SECTIONS}

    def grid(sec):
        on_home = [i for i in listed[sec] if i.get("home", True)]
        return '<div class="posts">\n%s\n  </div>' % "\n".join(card(i, t) for i in on_home[:HOME_LATEST])

    try:
        body = content.substitute(cv_paper_links(t), prefix=t["prefix"], open_to=S(t, "open_to"), open_also=S(t, "open_also"), writing_cards=grid("writing"), course_cards=grid("courses"),
                                  contact_key=esc(CONTACT_FORM_KEY), lang_code=t["lang"],
                                  project_cards=grid("projects"),
                                  all_projects=all_label(t, "all_projects", len(listed["projects"])),
                                  role_title=S(t, "role_title"), role_skills=S(t, "role_skills"), fun_roles=fun_roles(t),
                                  all_writing=all_label(t, "all_writing", len(listed["writing"])),
                                  all_courses=all_label(t, "all_courses", len(listed["courses"])))
    except KeyError as e:
        fail("%s: unknown placeholder $%s" % (path, e.args[0]))
    return page(t, t["home_title"], body, t["prefix"] + "/", description=t["home_description"],
                og_title=t["home_og_title"], og_type="profile", body_class="home", section="home")


def cv_page(t):
    path = os.path.join(ROOT, "content", "cv.%s.html" % t["lang"])
    with open(path, encoding="utf-8") as f:
        content = string.Template(f.read())
    try:
        body = content.substitute(cv_paper_links(t), prefix=t["prefix"], open_to=S(t, "open_to"), open_also=S(t, "open_also"), role_title=S(t, "role_title"), role_skills=S(t, "role_skills"))
    except KeyError as e:
        fail("%s: unknown placeholder $%s" % (path, e.args[0]))
    return page(t, "%s — %s" % (t["cv_title"], t["author"]), body, t["prefix"] + "/cv/",
                description=t["cv_description"], og_type="profile", section="about", crumbs=("cv", None))


def stylesheet():
    with open(os.path.join(ROOT, "assets", "site.css"), encoding="utf-8") as f:
        css = f.read()
    light = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    dark_os = HtmlFormatter(style="github-dark").get_style_defs(':root:not([data-theme="light"]) .codehilite')
    dark_os = "\n".join("  " + line for line in dark_os.splitlines())
    dark_forced = HtmlFormatter(style="github-dark").get_style_defs(':root[data-theme="dark"] .codehilite')
    return (css + "\n/* ---- code colours: generated by build.py from Pygments ---- */\n%s\n"
            "@media (prefers-color-scheme: dark) {\n%s\n}\n%s\n"
            ".prose .codehilite, .prose .codehilite pre { background: var(--code-bg) !important; }\n"
            % (light, dark_os, dark_forced))


# ---------------------------------------------------------------- main

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "_site"))
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    out = os.path.abspath(args.out)

    langs = load_languages()
    LANGS.update(langs)
    t0 = langs[DEFAULT_LANG]
    items = load_posts() + load_external(args.offline) + load_projects()
    PAPERS.extend(i for i in items if i["type"] == "paper")
    keys = [(i["section"], i["slug"]) for i in items]
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes or ("writing", "covers") in keys:
        fail("duplicate or reserved slugs: %s" % sorted(dupes | ({("writing", "covers")} & set(keys))))
    items.sort(key=lambda i: (i["date"], str(loc(i["title"], t0))), reverse=True)
    tr_report = load_translations(items, langs)
    TEASERS.update(load_teasers())

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    open(os.path.join(out, ".nojekyll"), "w").close()
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(out, "assets"))
    css = stylesheet()
    ASSET_V["site.css"] = hashlib.sha256(css.encode("utf-8")).hexdigest()[:8]
    write(os.path.join(out, "assets", "site.css"), css)
    if os.path.isdir(os.path.join(ROOT, "covers")):
        shutil.copytree(os.path.join(ROOT, "covers"), os.path.join(out, "covers"))
    for item in PAPERS:  # PDF copies of the publications: /papers/<slug>.pdf
        if item["paper"].get("pdf_copy"):
            os.makedirs(os.path.join(out, "papers"), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, item["paper"]["pdf_copy"]), os.path.join(out, item["paper"]["pdf_copy"]))

    # language-dependent pages: home and indexes (content pages exist once, in their own language)
    for t in langs.values():
        root = os.path.join(out, t["prefix"].lstrip("/"))
        if not os.path.isfile(os.path.join(ROOT, "content", "home.%s.html" % t["lang"])):
            fail("content/home.%s.html is missing for i18n/%s.yml" % (t["lang"], t["lang"]))
        write(os.path.join(root, "index.html"), home_page(items, t))
        if not os.path.isfile(os.path.join(ROOT, "content", "cv.%s.html" % t["lang"])):
            fail("content/cv.%s.html is missing for i18n/%s.yml" % (t["lang"], t["lang"]))
        write(os.path.join(root, "cv", "index.html"), cv_page(t))
        for section in ALL_SECTIONS:
            write(os.path.join(root, section, "index.html"), list_page(items, section, t))

    # neighbours in the section's list (newest first) for the ← → of the section bar
    for sec in ALL_SECTIONS:
        listed = [i for i in items if i["list"] and i["section"] == sec]
        for k, i in enumerate(listed):
            i["nb_prev"] = listed[k - 1] if k > 0 else None
            i["nb_next"] = listed[k + 1] if k + 1 < len(listed) else None

    # item pages: the text stays in its own language, the page around it exists in every UI language
    for item in items:
        for t in langs.values():
            dest = os.path.join(out, t["prefix"].lstrip("/"), item["section"], item["slug"])
            if item["type"] == "post":  # the post's images / attachments go next to its page
                shutil.copytree(item["folder"], dest, ignore=shutil.ignore_patterns("*.md"))
            write(os.path.join(dest, "index.html"), article_page(item, t))
    write(os.path.join(out, "writing", "covers", "index.html"), covers_page(items, t0))

    counts = {}
    for i in items:
        counts[i["section"]] = counts.get(i["section"], 0) + 1
    print("built: %s, languages: %s -> %s" % (counts, sorted(langs), out))
    print("translations: %(fresh)d up to date, %(stale)d outdated, %(missing)d missing "
          "(details: python tools/translations.py status)" % tr_report)


if __name__ == "__main__":
    main()
