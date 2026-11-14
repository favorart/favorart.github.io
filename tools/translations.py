#!/usr/bin/env python3
"""Versioned translation cache for articles and posts (see "Translations" in README.md).

    python tools/translations.py status [--offline]      what is up to date / outdated / missing / unreviewed
    python tools/translations.py source <slug>           print the original (Markdown) and its version hash
    python tools/translations.py new <slug> <lang>       create translations/<slug>/<lang>.md, or re-stamp an
                                                          outdated one for the current version of the original

One file per text and language, updated in place; older versions live only in git history. `source_hash` in
its front matter is build.source_hash() of the original it was made from. When the original changes, the build
keeps showing the reviewed translation with an "original updated" note until it is updated and reviewed again.
"""
import argparse
import re
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def items(offline=False):
    langs = build.load_languages()
    build.LANGS.update(langs)
    all_items = build.load_posts() + build.load_external(offline)
    return [i for i in all_items if build.translatable(i)], langs


def find(slug, offline=False):
    its, langs = items(offline)
    for i in its:
        if i["slug"] == slug:
            return i, langs
    build.fail("no translatable item with slug '%s' (posts and articles in Writing)" % slug)


def state(item, lang):
    path = build.translation_path(item, lang)
    if not os.path.isfile(path):
        return "missing"
    meta = build.read_translation(path)[0]
    if str(meta.get("source_hash")) != build.source_hash(item["source_md"]):
        return "outdated"
    return "ok" if meta.get("reviewed") else "unreviewed"


def cmd_status(args):
    its, langs = items(args.offline)
    codes = list(langs)
    print("%-52s %-4s %s" % ("item", "orig", "  ".join("%-10s" % c for c in codes)))
    totals = {}
    for i in its:
        cells = []
        for c in codes:
            st = "original" if c == i["lang"] else "provided" if c in i.get("provided", ()) else state(i, c)
            totals[st] = totals.get(st, 0) + 1
            cells.append("%-10s" % st)
        print("%-52s %-4s %s" % ((i["section"] + "/" + i["slug"])[:52], i["lang"], "  ".join(cells)))
    print("\n" + ", ".join("%s: %d" % kv for kv in sorted(totals.items())))


def cmd_source(args):
    i, _ = find(args.slug, args.offline)
    print("section: %s\nslug: %s\nsource: %s\nsource_lang: %s\nsource_hash: %s\ntitle: %s\nsummary: %s\n---" % (
        i["section"], i["slug"], i["source_ref"], i["lang"], build.source_hash(i["source_md"]),
        build.loc(i["title"], build.LANGS[build.DEFAULT_LANG]) if isinstance(i["title"], dict) else i["title"],
        build.loc(i["summary"], build.LANGS[build.DEFAULT_LANG]) if isinstance(i["summary"], dict) else i["summary"]))
    print(i["source_md"])


def cmd_new(args):
    i, langs = find(args.slug, args.offline)
    if args.lang not in langs:
        build.fail("unknown language '%s' (have: %s)" % (args.lang, ", ".join(langs)))
    if args.lang == i["lang"] or args.lang in i.get("provided", ()):
        build.fail("'%s' already has %s (original or provided by the source)" % (args.slug, args.lang))
    h, today = build.source_hash(i["source_md"]), dt.date.today().isoformat()
    path = build.translation_path(i, args.lang)
    rel = os.path.relpath(path, build.ROOT)
    if os.path.exists(path):  # outdated: keep the text, stamp the new version, ask for a new review
        with open(path, encoding="utf-8") as f:
            text = f.read()
        text = re.sub(r"(?m)^source_hash:.*$", "source_hash: %s" % h, text, count=1)
        text = re.sub(r"(?m)^translated:.*$", "translated: %s" % today, text, count=1)
        text = re.sub(r"(?m)^reviewed:.*$", "reviewed:            # set after the independent review", text, count=1)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("%s  (re-stamped for the current original: update the text to match it, then review)" % rel)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("---\n"
                "title: \"\"\n"
                "summary: \"\"\n"
                "source: %s\n"
                "source_lang: %s\n"
                "source_hash: %s\n"
                "translated: %s\n"
                "translator: Claude\n"
                "reviewed:            # date of the independent review; the build ignores the file until it is set\n"
                "---\n\n" % (i["source_ref"], i["lang"], h, today))
    print(rel)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip external articles (no network)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    p = sub.add_parser("source"); p.add_argument("slug")
    p = sub.add_parser("new"); p.add_argument("slug"); p.add_argument("lang")
    args = ap.parse_args()
    {"status": cmd_status, "source": cmd_source, "new": cmd_new}[args.cmd](args)


if __name__ == "__main__":
    main()
