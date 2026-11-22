"""What changed on the site this week: a plain-language digest of the Russian pages, by e-mail.

Compares the text of the built pages with last week's snapshot: new pages (title, summary, link),
changed paragraphs (was -> now), removed ones. Written for readers, not developers: no commits, no code.
Short first: one line per new page ("Почитать") and per changed page ("Обновилось": what kind of change, how
much); then a few small edits of the lightly edited pages for the careful reader; a rewritten page only says
"reread it". Changes of markup alone (a formula losing its $ signs) are not changes.
Sent through Web3Forms to the contact form's inbox (see weekly_report.send), ready to forward.

Usage:
  python tools/site_digest.py snapshot SITE_DIR OUT.json         # text of the pages of one build
  python tools/site_digest.py diff OLD.json NEW.json [--send]    # print the digest, or e-mail it
Workflow: .github/workflows/site-digest.yml (Sunday; last week's snapshot is the previous run's artifact).
"""
import argparse
import datetime as dt
import difflib
import glob
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from weekly_report import send  # noqa: E402  (the same Web3Forms channel as the analytics report)

SITE_URL = "https://favorart.github.io"
LANG = "ru"
LISTS = {"", "writing", "projects", "courses"}  # section lists: their changes are the new pages themselves
BLOCKS = {"p", "li", "h1", "h2", "h3", "h4", "blockquote", "td", "th", "dt", "dd", "figcaption", "summary",
          "div", "section", "header", "aside", "figure", "ul", "ol", "table", "tr", "dl"}
SKIP = {"nav", "script", "style", "pre", "svg", "button", "form", "footer", "noscript", "select"}
SKIP_CLASSES = {"views", "kicker", "ctxbar", "steps", "btn", "tr-note"}  # page chrome and the type/date line
INLINE = {"span", "a", "time", "b", "strong", "em", "i"}
NAMES = {"": "Главная", "cv": "Резюме (CV)"}
MONTHS = "января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split()
MAX_PER_PAGE = 10
SWAP_CHARS = 220       # a paragraph this short is shown whole as was -> now
DETAILS_PER_PAGE = 5   # small edits shown per page at the end of the letter
DETAIL_CHARS = 200     # an added/removed paragraph longer than this is only counted
SUMMARY_CHARS = 160    # a new page's summary is cut to this
MAX_CHARS = 40000


class Page(HTMLParser):
    """Text blocks inside <main>, without navigation, code, forms and the cards of other pages."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = self.summary = ""
        self.blocks, self.imgs = [], []
        self.in_main = self.in_title = 0
        self.skip = []  # stack of open skipped tags
        self.stack = []  # text of the open blocks: nested blocks split the outer one into pieces

    def handle_starttag(self, t, a):
        a = dict(a)
        if t == "title":
            self.in_title = 1
        if t == "meta" and a.get("name") == "description":
            self.summary = a.get("content", "")
        if t == "main":
            self.in_main = 1
        if not self.in_main:
            return
        if self.skip:
            if t == self.skip[-1][0]:
                self.skip.append((t, 0))
            return
        cls = a.get("class") or ""
        if (t in SKIP or (t == "article" and "card" in cls) or SKIP_CLASSES & set(cls.split())
                or a.get("aria-hidden") == "true"):
            self.skip.append((t, 0))
            return
        if t == "img":
            self.imgs.append(a.get("src", ""))
        if (t == "br" or t in INLINE) and self.stack:
            self.stack[-1] += " "
        if t in BLOCKS:
            if self.stack:
                self.blocks.append(self.stack[-1])  # text before a nested block (li > p, div > p)
                self.stack[-1] = ""
            self.stack.append("")

    def handle_startendtag(self, t, a):
        self.handle_starttag(t, a)
        if self.skip and self.skip[-1][0] == t and t not in ("img", "br", "meta"):
            self.skip.pop()

    def handle_endtag(self, t):
        if t == "title":
            self.in_title = 0
        if not self.in_main:
            return
        if self.skip:
            if t == self.skip[-1][0]:
                self.skip.pop()
            return
        if t == "main":
            self.in_main = 0
        if t in BLOCKS and self.stack:
            self.blocks.append(self.stack.pop())

    def handle_data(self, d):
        if self.in_title:
            self.title += d
        if self.in_main and not self.skip and self.stack:
            self.stack[-1] += d


def clean(s):
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r" ([,.;:!?»)])", r"", s).replace("« ", "«").replace("( ", "(")


def snapshot(site):
    pages = {}
    root = os.path.join(site, LANG)
    for f in sorted(glob.glob(os.path.join(root, "**", "index.html"), recursive=True)):
        rel = os.path.relpath(os.path.dirname(f), root).replace("\\", "/")
        rel = "" if rel == "." else rel
        if rel in LISTS or rel.startswith("covers"):
            continue
        p = Page()
        p.feed(open(f, encoding="utf-8").read())
        blocks, seen = [], set()
        for b in map(clean, p.blocks):
            if re.search(r"\w", b) and b not in seen:
                blocks.append(b)
                seen.add(b)
        title = clean(p.title).rsplit(" — ", 1)[0] if " — " in p.title else clean(p.title)
        pages[rel] = {"title": NAMES.get(rel, title), "summary": clean(p.summary),
                      "blocks": blocks, "imgs": len(p.imgs)}
    return pages


def url(rel):
    return "%s/%s/%s" % (SITE_URL, LANG, rel + "/" if rel else "")


def short(s, n=400):
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def same_text(a, b):
    return re.sub(r"[\s$]", "", a) == re.sub(r"[\s$]", "", b)


def page_changes(old, new):
    """Changes of one page as (kind, was, now): swap (a short paragraph edited: was -> now), fix (a long
    paragraph edited: only counted), add, remove, img (now = how many pictures more, negative if fewer)."""
    items = []
    ob, nb = old["blocks"], new["blocks"]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ob, nb, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        olds, news = ob[i1:i2], nb[j1:j2]
        while olds and news:  # pair similar paragraphs as edits, the rest are additions/removals
            a, b = olds[0], news[0]
            if difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() < 0.5:
                break
            olds.pop(0), news.pop(0)
            if same_text(a, b):  # only markup changed (a formula lost its $ signs, spacing): nothing to read
                continue
            items.append(("swap" if len(a) <= SWAP_CHARS and len(b) <= SWAP_CHARS else "fix", a, b))
        items += [("remove", a, "") for a in olds]
        items += [("add", "", b) for b in news]
    d = new["imgs"] - old["imgs"]
    if d:
        items.append(("img", "", d))
    return items


def date_ru(d):
    return "%d %s" % (d.day, MONTHS[d.month - 1])


def period(start, end):
    if start.month == end.month:
        return "%d–%s" % (start.day, date_ru(end))
    return "%s – %s" % (date_ru(start), date_ru(end))


def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return "%d %s" % (n, one)
    return "%d %s" % (n, few if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else many)


RULE = "─" * 30
NEW_WORDS = {"writing": ("новая публикация", "новые публикации", "новых публикаций"),
             "projects": ("новый проект", "новых проекта", "новых проектов"),
             "courses": ("новый курс", "новых курса", "новых курсов"),
             "": ("новая страница", "новые страницы", "новых страниц")}


def section(rel):
    head = rel.split("/")[0]
    return head if head in NEW_WORDS else ""


def rewritten(items):
    """Changed so much that a list of edits would not help: the reader should reread the page."""
    big = sum(1 for k, _, _ in items if k in ("add", "remove", "fix"))
    return len(items) > 3 * MAX_PER_PAGE or big >= 6


def what_changed(items):
    """One plain line about a page's changes: what kind, how many."""
    if rewritten(items):
        return "текст заметно переписан, стоит перечитать"
    n = {k: sum(1 for kk, _, _ in items if kk == k) for k in ("swap", "fix", "add", "remove", "img")}
    parts = []
    if n["swap"] + n["fix"]:
        parts.append("поправлено " + plural(n["swap"] + n["fix"], "место", "места", "мест"))
    if n["add"]:
        parts.append(agreed(n["add"], "добавлен", "добавлено"))
    if n["remove"]:
        parts.append(agreed(n["remove"], "убран", "убрано"))
    imgs = sum(v for k, _, v in items if k == "img")
    if imgs:
        parts.append(("новые картинки: %d" if imgs > 0 else "убрано картинок: %d") % abs(imgs))
    return ", ".join(parts)


def agreed(n, one, many):
    """'добавлен 1 абзац', 'добавлено 3 абзаца'."""
    return "%s %s" % (one if n % 10 == 1 and n % 100 != 11 else many, plural(n, "абзац", "абзаца", "абзацев"))


def names(titles, limit=3):
    if len(titles) <= limit:
        return ", ".join(titles[:-1]) + (" и " if len(titles) > 1 else "") + titles[-1]
    return ", ".join(titles[:limit]) + " и ещё %d" % (len(titles) - limit)


def details(items):
    """The small edits of a page, for the reader who wants to notice them: was -> now, added, removed."""
    out, shown = [], 0
    for kind, was, now in items:
        if shown == DETAILS_PER_PAGE:
            break
        if kind == "swap":
            out += ["   было:   " + was, "   стало:  " + now, ""]
        elif kind == "add" and len(now) <= DETAIL_CHARS:
            out += ["   + добавлено: «%s»" % now, ""]
        elif kind == "remove" and len(was) <= DETAIL_CHARS:
            out += ["   − убрано: «%s»" % was, ""]
        else:
            continue
        shown += 1
    rest = sum(1 for k, _, _ in items if k != "img") - shown
    if rest > 0 and out:
        out += ["   …и ещё %s — на странице" % plural(rest, "правка", "правки", "правок"), ""]
    return out


def digest(old, new, end, days=7):
    start = end - dt.timedelta(days=days - 1)
    added = [r for r in new if r not in old]
    removed = [r for r in old if r not in new]
    changed = [(r, page_changes(old[r], new[r])) for r in new if r in old]
    changed = sorted([(r, c) for r, c in changed if c], key=lambda rc: -len(rc[1]))
    if not (added or removed or changed):
        return None, None
    when = "%s %d" % (period(start, end), end.year)
    out = ["Что нового на сайте · %s" % when, ""]
    if not old:
        out += ["На этой неделе сайт появился! Ниже всё, что на нём есть.", ""]
    else:
        lead = []
        for key in NEW_WORDS:
            n = sum(1 for r in added if section(r) == key)
            if n:
                lead.append(plural(n, *NEW_WORDS[key]))
        if changed:
            lead.append("обновлено: " + names([new[r]["title"] for r, _ in changed]))
        if removed:
            lead.append("убрано " + plural(len(removed), "страница", "страницы", "страниц"))
        out += ["За неделю: " + "; ".join(lead) + ".", ""]
    if added:
        out += [RULE, "📖 ПОЧИТАТЬ", ""]
        for r in sorted(added, key=lambda r: list(NEW_WORDS).index(section(r))):
            out.append("• " + new[r]["title"])
            if new[r]["summary"] and r:
                out.append("  " + short(new[r]["summary"], SUMMARY_CHARS))
            out += ["  " + url(r), ""]
    if changed:
        out += [RULE, "✏️ ОБНОВИЛОСЬ", ""]
        for r, items in changed:
            out += ["• %s — %s" % (new[r]["title"], what_changed(items)), "  " + url(r), ""]
    if removed:
        out += [RULE, "🗑 УБРАНО", ""] + ["• " + old[r]["title"] for r in removed] + [""]
    small = [(r, details(items)) for r, items in changed if not rewritten(items)]
    small = [(r, d) for r, d in small if d]
    if small:
        out += [RULE, "🔍 МЕЛКИЕ ПРАВКИ — для внимательного чтения", ""]
        for r, d in small:
            out += [new[r]["title"] + ":", ""] + d
    out += [RULE, "Письмо собрано автоматически по русской версии сайта. Приятного чтения! 🙂"]
    text = "\n".join(out)
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS].rsplit("\n", 1)[0] + "\n\n…письмо обрезано: правок за неделю очень много."
    subject = "что нового на сайте, %s" % when
    return subject, text


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("site")
    s.add_argument("out")
    d = sub.add_parser("diff")
    d.add_argument("old")
    d.add_argument("new")
    d.add_argument("--end", help="last day of the period, YYYY-MM-DD, default today (UTC)")
    d.add_argument("--days", type=int, default=7, help="length of the period in days")
    d.add_argument("--send", action="store_true", help="e-mail the digest instead of printing it")
    a = ap.parse_args()
    if a.cmd == "snapshot":
        pages = snapshot(a.site) if os.path.isdir(a.site) else {}
        if not pages:
            print("site_digest: warning: no %s pages in %s" % (LANG, a.site))
        json.dump(pages, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print("snapshot: %d pages" % len(pages))
        return
    old, new = (json.load(open(f, encoding="utf-8")) for f in (a.old, a.new))
    end = dt.date.fromisoformat(a.end) if a.end else dt.datetime.now(dt.timezone.utc).date()
    subject, text = digest(old, new, end, a.days)
    if not subject:
        print("no changes this week: nothing sent")
    elif a.send:
        send(subject, text, name="Что нового на сайте")
    else:
        print(subject + "\n\n" + text)


if __name__ == "__main__":
    main()
