"""What changed on the site this week: a plain-language digest of the Russian pages, by e-mail.

Compares the text of the built pages with last week's snapshot: new pages (title, summary, link),
changed paragraphs (was -> now), removed ones. Written for readers, not developers: no commits, no code.
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


def word_changes(a, b):
    """Fragments of a long paragraph that changed, with a few words of context around each."""
    wa, wb = a.split(" "), b.split(" ")
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        left = " ".join(wa[max(0, i1 - 5):i1])
        right = " ".join(wa[i2:i2 + 5])
        was, now = " ".join(wa[i1:i2]), " ".join(wb[j1:j2])
        mid = ("[было: %s] [стало: %s]" % (short(was, 200), short(now, 200)) if was and now
               else "[добавлено: %s]" % short(now, 200) if now else "[убрано: %s]" % short(was, 200))
        out.append("…%s %s %s…" % (left, mid, right))
    return out


def page_changes(old, new):
    """Changes of one page, each a list of lines (shown with a blank line between them)."""
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
            if len(a) <= 220 and len(b) <= 220:
                items.append(["     ❌ было:   " + a, "     ✅ стало:  " + b])
            else:
                items += [["     ✏️ поправлено:  " + w] for w in word_changes(a, b)[:4]]
        items += [["     ➖ убрано:  «%s»" % short(a, 200)] for a in olds]
        items += [["     ➕ добавлено:  «%s»" % short(b)] for b in news]
    d = new["imgs"] - old["imgs"]
    if d:
        items.append(["     🖼 %s картинок: %d" % ("новых" if d > 0 else "убрано", abs(d))])
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


RULE = "━" * 28
SECTIONS = [("writing", "📝 Публикации"), ("projects", "🛠 Проекты"), ("courses", "🎓 Курсы"), ("", "📄 Страницы")]


def section(rel):
    head = rel.split("/")[0]
    return head if head in ("writing", "projects", "courses") else ""


def heading(title):
    return [RULE, title, RULE, ""]


def digest(old, new, end, days=7):
    start = end - dt.timedelta(days=days - 1)
    added = [r for r in new if r not in old]
    removed = [r for r in old if r not in new]
    changed = [(r, page_changes(old[r], new[r])) for r in new if r in old]
    changed = [(r, c) for r, c in changed if c]
    if not (added or removed or changed):
        return None, None
    when = "%s %d" % (period(start, end), end.year)
    out = ["📰  Что нового на сайте favorart.github.io", "      %s" % when, ""]
    if not old:
        out += ["На этой неделе сайт появился! Ниже всё, что на нём есть.", ""]
    if old:
        counts = [plural(len(added), "новая страница", "новые страницы", "новых страниц"),
                  plural(len(changed), "страница с правками", "страницы с правками", "страниц с правками"),
                  plural(len(removed), "страница убрана", "страницы убраны", "страниц убрано")]
        out += ["Коротко: " + ", ".join(c for c in counts if not c.startswith("0 ")) + ".", ""]
    if added:
        out += heading("✨  НОВОЕ")
        for key, name in SECTIONS:
            group = [r for r in added if section(r) == key]
            if not group:
                continue
            out += [name, ""]
            for i, r in enumerate(group, 1):
                out.append("  %d. %s" % (i, new[r]["title"]))
                if new[r]["summary"] and r:
                    out.append("     " + new[r]["summary"])
                out += ["     👉 " + url(r), ""]
    if changed:
        out += heading("✏️  ПРАВКИ НА СТРАНИЦАХ")
        for r, items in changed:
            out += ["📄 " + new[r]["title"], "     👉 " + url(r), ""]
            if len(items) > 3 * MAX_PER_PAGE:  # rewritten as a whole: a list of fragments would not help
                out += ["     🔄 Текст страницы заметно переработан (%s) — её стоит перечитать целиком."
                        % plural(len(items), "правка", "правки", "правок"), ""]
                continue
            for it in items[:MAX_PER_PAGE]:
                out += it + [""]
            if len(items) > MAX_PER_PAGE:
                rest = len(items) - MAX_PER_PAGE
                out += ["     …и ещё %s — страницу стоит перечитать целиком." % plural(rest, "правка", "правки", "правок"), ""]
    if removed:
        out += heading("🗑  УБРАНО С САЙТА") + ["  • " + old[r]["title"] for r in removed] + [""]
    out += [RULE, "Письмо собрано автоматически по русской версии сайта.", "Приятного чтения! 🙂"]
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
