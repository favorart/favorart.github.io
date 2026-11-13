#!/usr/bin/env python3
"""Static site generator for favorart.github.io.

Inputs
  content/home.<lang>.html  home page body (CV) per language
  i18n/<lang>.yml           UI strings per language (+ URL prefix: "" = root, "/ru", ...)
  templates/*.html          base layout and partials (string.Template, $placeholders)
  assets/site.css           the one stylesheet (Pygments code colours are appended)
  posts/*/index.md          LinkedIn posts: YAML front matter + Markdown, images next to them
  sources.yml               external articles/courses, fetched from other public repos
  covers/<slug>/            cover options for external content

Output: _site/  (deployed by .github/workflows/pages.yml)

Usage: python build.py [--out DIR] [--offline]
  --offline  do not fetch external repos (placeholder bodies; for quick local previews)

Design lives only in templates/ and assets/site.css; this file is content logic.
"""
import argparse
import datetime as dt
import glob
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
HOME_LATEST = 2  # cards per section on the home page
RASTER = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif")
IMAGE_EXT = RASTER + (".svg",)
# content sections: manifest key -> URL segment
SECTIONS = {"articles": "writing", "courses": "courses"}

esc = html.escape


def fail(msg):
    raise SystemExit("build error: " + msg)


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
        langs[code] = data
    if DEFAULT_LANG not in langs:
        fail("i18n/%s.yml is required" % DEFAULT_LANG)
    return langs


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


def date_text(item, t):
    if item.get("date_label"):
        return esc(str(item["date_label"]))
    d = item["date"]
    return "%d %s %d" % (d.day, t["months"][d.month - 1], d.year)


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
        out.append(line)
        prev = line
    return "\n".join(out)


def render_markdown(text):
    md = markdown.Markdown(
        extensions=["extra", "sane_lists", "codehilite", "toc"],
        extension_configs={
            "codehilite": {"css_class": "codehilite", "guess_lang": False},
            "toc": {"slugify": gh_slugify},
        },
        output_format="html5",
    )
    return md.convert(gfm_fixups(text))


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
    Links to another file that is itself on this site go to that page instead."""
    repo, branch, path = entry["repo"], entry["branch"], entry["path"]
    base_dir = posixpath.dirname(path)

    def fix(m):
        prefix, quote, url = m.group(1), m.group(2), html.unescape(m.group(3)).strip()
        attr = prefix.strip().split("=")[0].strip().lower()
        if not url or url.startswith(("#", "//")) or SCHEME_RE.match(url):
            return m.group(0)
        parts = urllib.parse.urlsplit(url)
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
    """External content: turn bare URLs in text (not in links/code) into short links."""
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

def load_posts():
    items = []
    for md_path in sorted(glob.glob(os.path.join(ROOT, "posts", "*", "index.md"))):
        folder = os.path.dirname(md_path)
        name = os.path.basename(folder)
        where = "posts/%s/index.md" % name
        with open(md_path, encoding="utf-8") as f:
            meta, body = split_front_matter(f.read(), where)
        for key in ("title", "date", "summary", "original_url"):
            if not meta.get(key):
                fail("%s: front matter field '%s' is required" % (where, key))
        slug = str(meta.get("slug") or re.sub(r"^\d{4}-\d{2}(-\d{2})?-", "", name))
        cover = meta.get("cover")
        if cover and not os.path.isfile(os.path.join(folder, cover)):
            fail("%s: cover file '%s' not found next to index.md" % (where, cover))
        items.append({
            "type": "post", "section": "writing", "slug": slug,
            "title": str(meta["title"]), "date": as_date(meta["date"], where),
            "date_label": meta.get("date_label"), "lang": meta.get("lang", "ru"),
            "summary": str(meta["summary"]), "kind": meta.get("kind"),
            "original_url": meta["original_url"], "tags": meta.get("tags") or [],
            "cover_url": "/writing/%s/%s" % (slug, cover) if cover else None,
            "folder": folder, "options_dir": folder,
            "body_html": render_markdown(body), "subtitle": None, "demo_url": meta.get("demo_url"),
            "list": meta.get("list", True),
        })
    return items


def load_external(offline):
    path = os.path.join(ROOT, "sources.yml")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f) or {}
    unknown = set(manifest) - set(SECTIONS)
    if unknown:
        fail("sources.yml: unknown sections %s (known: %s)" % (sorted(unknown), sorted(SECTIONS)))
    entries = [(SECTIONS[key], e) for key in SECTIONS for e in (manifest.get(key) or [])]
    page_of = {(e["repo"], e["path"]): "/%s/%s/" % (sec, e["slug"]) for sec, e in entries}
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
            "type": "external", "section": sec, "slug": e["slug"],
            "title": str(e["title"]), "date": as_date(e["date"], where),
            "date_label": e.get("date_label"), "lang": e.get("lang", "en"),
            "summary": str(e["summary"]), "kind": e.get("kind"),
            "repo": e["repo"], "branch": e["branch"], "path": e["path"],
            "tags": e.get("tags") or [], "demo_url": e.get("demo_url"),
            "cover_url": "/" + cover if cover else None,
            "options_dir": os.path.join(ROOT, os.path.dirname(cover)) if cover else None,
            "list": e.get("list", True), "subtitle": None,
        }
        if offline:
            item["body_html"] = "<p><em>(offline build: content not fetched)</em></p>"
        else:
            raw = fetch("https://raw.githubusercontent.com/%s/%s/%s" % (e["repo"], e["branch"], e["path"]))
            m = re.match(r"\A\s*#\s+(.+?)\s*#*\s*\n", raw)
            if m:  # the source's own H1 becomes the subtitle; the page H1 is the manifest title
                item["subtitle"], raw = m.group(1).strip(), raw[m.end():]
            item["body_html"] = linkify_bare(rewrite_relative(render_markdown(raw), item, page_of))
        items.append(item)
    return items


# ---------------------------------------------------------------- pages

def page(t, title, body, path, description="", lang=None, og_image=None, og_type="website",
         noindex=False, body_class="", og_title=None, section=""):
    extra = []
    if og_image:
        extra.append('<meta property="og:image" content="%s">' % esc(SITE_URL + og_image))
    if noindex:
        extra.append('<meta name="robots" content="noindex">')
    return tpl("base", lang=esc(lang or t["lang"]), title=esc(title), og_title=esc(og_title or title),
               description=esc(description), og_type=og_type, url=esc(SITE_URL + path),
               head_extra="\n".join(extra), body_class=body_class, prefix=t["prefix"],
               author=S(t, "author"), tagline=S(t, "tagline"), lang_soon=S(t, "lang_soon"), section=section,
               nav_items=tpl("nav", prefix=t["prefix"], **{k: S(t, k) for k in (
                   "nav_home", "nav_writing", "nav_teaching", "nav_about", "nav_contact")}),
               footer_contact=S(t, "footer_contact"),
               footer_copy="".join("<span>%s</span>" % str(line).replace("{mit}", esc(LICENSE_URL))
                                   for line in t["footer_copy"]),
               year=dt.date.today().year, body=body)


def item_url(item, t=None):
    return "/%s/%s/" % (item["section"], item["slug"])


def kind_of(item, t):
    """Label of the item; for a LinkedIn post it links to the original post."""
    label = esc(item["kind"]) if item.get("kind") else S(t, "linkedin_post")
    if item.get("original_url"):
        return '<a class="src" href="%s">%s</a>' % (esc(item["original_url"]), label)
    return label


def card(item, t):
    cover = ""
    if item.get("cover_url"):
        cover = '<img class="cover" src="%s" alt="" loading="lazy" width="1200" height="630">' % esc(item["cover_url"])
    return tpl("card", href=item_url(item), cover=cover, kind=kind_of(item, t), date=date_text(item, t),
               lang=esc(item["lang"]), title=esc(item["title"]), summary=esc(item["summary"]))


def article_page(item, t):
    if item["type"] == "post":
        source_top = '<a href="%s">LinkedIn</a>' % esc(item["original_url"])
        source_bottom = '<p class="origin">%s <a href="%s">LinkedIn →</a></p>' % (
            S(t, "originally_on"), esc(item["original_url"]))
    else:
        repo_url = "https://github.com/" + item["repo"]
        file_url = "%s/blob/%s/%s" % (repo_url, item["branch"], item["path"])
        source_top = '%s: <a href="%s">%s</a>' % (S(t, "source"), esc(repo_url), esc(item["repo"]))
        source_bottom = '<p class="origin">%s: <a href="%s">%s</a> · <a href="%s">%s</a></p>' % (
            S(t, "source"), esc(repo_url), esc(repo_url[len("https://"):]), esc(file_url), esc(item["path"]))
    demo = ""
    if item.get("demo_url"):
        demo = ' · <a class="demo" href="%s">%s</a>' % (esc(item["demo_url"]), S(t, "live_demo"))
    tags = ""
    if item["tags"]:
        tags = '<div class="chips">%s</div>' % "".join(
            '<span class="chip">#%s</span>' % esc(str(x)) for x in item["tags"])
    subtitle = '<p class="subtitle">%s</p>' % esc(item["subtitle"]) if item.get("subtitle") else ""
    back = "back_to_courses" if item["section"] == "courses" else "back_to_writing"
    if item["type"] == "post":
        cta = '<a class="btn sun big" href="%s">%s <span class="arr">→</span></a>' % (
            esc(item["original_url"]), S(t, "comment_on_linkedin"))
    else:
        cta = '<a class="btn sun big" href="%s/#contact">%s <span class="arr">→</span></a>' % (
            t["prefix"], S(t, "send_feedback"))
    hero = ""
    if item.get("cover_url"):
        hero = '<img class="hero-cover" src="%s" alt="" width="1200" height="630">' % esc(item["cover_url"])
    body = tpl("article", hero=hero, kind=kind_of(item, t), date=date_text(item, t), lang=esc(item["lang"]),
               title=esc(item["title"]), subtitle=subtitle, author=S(t, "author"), source_top=source_top,
               demo=demo, content=item["body_html"], tags=tags, cta=cta, source_bottom=source_bottom,
               back_href="%s/%s/" % (t["prefix"], item["section"]), back_text=S(t, back))
    cover = item.get("cover_url") or ""
    return page(t, "%s — %s" % (item["title"], t["author"]), body, item_url(item), description=item["summary"],
                lang=item["lang"], og_image=cover if cover.lower().endswith(RASTER) else None, og_type="article",
                section="teaching" if item["section"] == "courses" else "writing")


def list_page(items, section, t):
    key = "writing" if section == "writing" else "courses"
    cards = "\n".join(card(i, t) for i in items if i["list"] and i["section"] == section)
    body = tpl("list", kicker=S(t, key + "_kicker"), title=S(t, key + "_title"), lead=S(t, key + "_lead"),
               cards=cards)
    return page(t, "%s — %s" % (t[key + "_title"], t["author"]), body, "%s/%s/" % (t["prefix"], section),
                description=t[key + "_description"], section="writing" if section == "writing" else "teaching")


def covers_page(items, t):
    groups, seen = [], set()
    for item in sorted(items, key=lambda i: not i["list"]):  # listed items name the group
        d = item.get("options_dir")
        if not d or d in seen or not item.get("cover_url"):
            continue
        options = sorted(glob.glob(os.path.join(d, "cover-*.svg")))
        if not options:
            continue
        seen.add(d)
        base_url = item["cover_url"].rsplit("/", 1)[0]
        chosen = os.path.basename(item["cover_url"])
        if item["type"] == "post":
            where = "posts/%s/index.md → cover" % os.path.basename(item["folder"])
        else:
            where = "sources.yml → %s → cover" % item["slug"]
        opts = []
        for n, opt in enumerate(options, 1):
            name = os.path.basename(opt)
            sel = name == chosen
            opts.append(tpl("cover_option", selected_class=" selected" if sel else "",
                            src=esc(base_url + "/" + name), label="%s %d" % (S(t, "covers_option"), n),
                            name=esc(name),
                            selected_tag=' <span class="tag">%s</span>' % S(t, "covers_current") if sel else ""))
        groups.append(tpl("cover_group", title=esc(item["title"]), set_in=S(t, "covers_set_in"), where=esc(where),
                          chosen=esc(chosen), options="\n".join(opts)))
    body = tpl("covers", kicker=S(t, "covers_kicker"), title=S(t, "covers_title"), lead=S(t, "covers_lead"),
               groups="\n".join(groups))
    return page(t, "%s — %s" % (t["covers_title"], t["author"]), body, "/writing/covers/", noindex=True,
                section="writing")


def home_page(items, t):
    path = os.path.join(ROOT, "content", "home.%s.html" % t["lang"])
    with open(path, encoding="utf-8") as f:
        content = string.Template(f.read())
    listed = {sec: [i for i in items if i["list"] and i["section"] == sec] for sec in SECTIONS.values()}

    def grid(sec):
        return '<div class="posts">\n%s\n  </div>' % "\n".join(card(i, t) for i in listed[sec][:HOME_LATEST])

    try:
        body = content.substitute(prefix=t["prefix"], writing_cards=grid("writing"), course_cards=grid("courses"),
                                  all_writing=S(t, "all_writing").replace("{n}", str(len(listed["writing"]))),
                                  all_courses=S(t, "all_courses").replace("{n}", str(len(listed["courses"]))))
    except KeyError as e:
        fail("%s: unknown placeholder $%s" % (path, e.args[0]))
    return page(t, t["home_title"], body, t["prefix"] + "/", description=t["home_description"],
                og_title=t["home_og_title"], og_type="profile", body_class="home", section="home")


def cv_page(t):
    path = os.path.join(ROOT, "content", "cv.%s.html" % t["lang"])
    with open(path, encoding="utf-8") as f:
        content = string.Template(f.read())
    try:
        body = content.substitute(prefix=t["prefix"])
    except KeyError as e:
        fail("%s: unknown placeholder $%s" % (path, e.args[0]))
    return page(t, "%s — %s" % (t["cv_title"], t["author"]), body, t["prefix"] + "/cv/",
                description=t["cv_description"], og_type="profile", section="about")


def stylesheet():
    with open(os.path.join(ROOT, "assets", "site.css"), encoding="utf-8") as f:
        css = f.read()
    light = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    dark = HtmlFormatter(style="github-dark").get_style_defs(".codehilite")
    dark = "\n".join("  " + line for line in dark.splitlines())
    return (css + "\n/* ---- code colours: generated by build.py from Pygments ---- */\n%s\n"
            "@media (prefers-color-scheme: dark) {\n%s\n}\n"
            ".prose .codehilite, .prose .codehilite pre { background: var(--code-bg) !important; }\n" % (light, dark))


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
    t0 = langs[DEFAULT_LANG]
    items = load_posts() + load_external(args.offline)
    keys = [(i["section"], i["slug"]) for i in items]
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes or ("writing", "covers") in keys:
        fail("duplicate or reserved slugs: %s" % sorted(dupes | ({("writing", "covers")} & set(keys))))
    items.sort(key=lambda i: (i["date"], i["title"]), reverse=True)

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    open(os.path.join(out, ".nojekyll"), "w").close()
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(out, "assets"))
    write(os.path.join(out, "assets", "site.css"), stylesheet())
    if os.path.isdir(os.path.join(ROOT, "covers")):
        shutil.copytree(os.path.join(ROOT, "covers"), os.path.join(out, "covers"))

    # language-dependent pages: home and indexes (content pages exist once, in their own language)
    for t in langs.values():
        root = os.path.join(out, t["prefix"].lstrip("/"))
        if not os.path.isfile(os.path.join(ROOT, "content", "home.%s.html" % t["lang"])):
            fail("content/home.%s.html is missing for i18n/%s.yml" % (t["lang"], t["lang"]))
        write(os.path.join(root, "index.html"), home_page(items, t))
        if not os.path.isfile(os.path.join(ROOT, "content", "cv.%s.html" % t["lang"])):
            fail("content/cv.%s.html is missing for i18n/%s.yml" % (t["lang"], t["lang"]))
        write(os.path.join(root, "cv", "index.html"), cv_page(t))
        for section in SECTIONS.values():
            write(os.path.join(root, section, "index.html"), list_page(items, section, t))

    for item in items:
        dest = os.path.join(out, item["section"], item["slug"])
        if item["type"] == "post":  # the post's images / attachments go next to its page
            shutil.copytree(item["folder"], dest, ignore=shutil.ignore_patterns("*.md"))
        write(os.path.join(dest, "index.html"), article_page(item, t0))
    write(os.path.join(out, "writing", "covers", "index.html"), covers_page(items, t0))

    counts = {}
    for i in items:
        counts[i["section"]] = counts.get(i["section"], 0) + 1
    print("built: %s, languages: %s -> %s" % (counts, sorted(langs), out))


if __name__ == "__main__":
    main()
