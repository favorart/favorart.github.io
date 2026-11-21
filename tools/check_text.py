#!/usr/bin/env python3
"""Check the text of the built pages for markup that did not turn into what the reader should see.

Usage: python tools/check_text.py [_site]
Looks at the text inside <main>, outside code, scripts and styles, of every page in every language:
  tex          a formula left as TeX source ($...$, $$, \\hspace{...}, \\to): it should be <code class="math">
  placeholder  an internal placeholder of the build (MATHPH…X, REFLBL…R) leaked into the page
  cite         a citation [N] / {N} that is not a link while the page has a reference list with that item,
               or a reference list item [N] / {N} without an anchor
  markdown     Markdown that was not converted: **bold**, [text](url), ![img](...), {: attr }, escaped \\_ \\*
Exit code 1 if anything is found.
"""
import glob
import os
import re
import sys
from html.parser import HTMLParser

SKIP = {"pre", "code", "script", "style", "svg", "textarea", "kbd", "samp"}
VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "col", "area", "base", "embed", "track"}
CHECKS = [
    ("tex", re.compile(r"\$\$|(?<![\w$])\$[^$\s][^$\n]{0,80}?[\\^_{}][^$\n]{0,80}?\$|\\(?:hspace|frac|to|sum|cdot|le|ge|"
                       r"times|alpha|beta|infty|sqrt|mathrm|text)\b")),
    ("placeholder", re.compile(r"MATHPH\d+X|REFLBL\d+R")),
    ("markdown", re.compile(r"\*\*\S[^*]{0,80}\*\*|!?\[[^\]\n]{1,80}\]\((?:https?:|/|\.)[^)\s]*\)|\{:\s*[^}]*\}"
                            r"|\\[_*`#]")),
]
CITE_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]|\{(\d+)\}")
REF_LABEL_RE = re.compile(r"^\s*([\[{])(\d+)[\]}]")


class Text(HTMLParser):
    """Text runs inside <main> outside code, with whether each sits in a link, and the reference list items."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main = self.skip = self.link = 0
        self.runs = []  # (text, in a link or the label of a list item)
        self.ids = set()
        self.items = []  # [id or None, text] of every <li> and <p> in main (a footnote may be a paragraph)
        self.li = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "main":
            self.main = 1
        if not self.main or tag in VOID:
            return
        if tag in SKIP or self.skip:
            self.skip += 1
            return
        if tag == "a":
            self.link += 1
        if tag in ("li", "p"):
            self.items.append([a.get("id"), ""])
            self.li.append(self.items[-1])

    def handle_endtag(self, tag):
        if not self.main or tag in VOID:
            return
        if self.skip:
            self.skip -= 1
            return
        if tag == "main":
            self.main = 0
        if tag == "a" and self.link:
            self.link -= 1
        if tag in ("li", "p") and self.li:
            self.li.pop()

    def handle_data(self, data):
        if self.main and not self.skip:
            first = bool(self.li) and not self.li[-1][1].strip()  # an item's opening text holds its own label
            self.runs.append((data, self.link or first))
            if self.li:
                self.li[-1][1] += data


def check(path):
    p = Text()
    p.feed(open(path, encoding="utf-8").read())
    found = []
    text = "".join(t for t, _ in p.runs)
    for name, rx in CHECKS:
        for m in rx.finditer(text):
            found.append((name, text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")))
    refs = {}
    for item_id, item_text in p.items:
        m = REF_LABEL_RE.match(item_text)
        if m:
            kind = "ref" if m.group(1) == "[" else "src"
            refs[(kind, m.group(2))] = item_id
            if item_id != "%s-%s" % (kind, m.group(2)):
                found.append(("cite", "reference item without anchor: " + item_text.strip()[:60]))
    if not refs:  # numbered list turned into ref-N by the build (build.numbered_refs)
        refs = {("ref", i[4:]): i for i in p.ids if re.fullmatch(r"ref-\d+", i)}
    if not refs:
        bare = [m.group(0) for t, in_link in p.runs if not in_link for m in re.finditer(r"\[\d+(?:,\s*\d+)*\]", t)]
        if bare:
            found.append(("cite", "citations %s but no reference list to link them to" % " ".join(sorted(set(bare)))))
    if refs:
        for t, in_link in p.runs:
            if in_link:
                continue
            for m in CITE_RE.finditer(t):
                nums = [("ref", n) for n in re.findall(r"\d+", m.group(1))] if m.group(1) else [("src", m.group(2))]
                if all(k in refs for k in nums):
                    found.append(("cite", "not a link: " + t[max(0, m.start() - 30):m.end() + 10].strip()))
    return found


def main():
    site = sys.argv[1] if len(sys.argv) > 1 else "_site"
    total = 0
    for f in sorted(glob.glob(os.path.join(site, "**", "*.html"), recursive=True)):
        found = check(f)
        if found:
            print("== " + os.path.relpath(f, site).replace("\\", "/"))
            for name, ctx in found:
                print("   %-11s %s" % (name, ctx))
            total += len(found)
    print("check_text: %d problem(s)" % total)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
