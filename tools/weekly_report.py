#!/usr/bin/env python3
"""Weekly analytics report from the GoatCounter API, as plain text (in Russian, for the author).

    GOATCOUNTER_API_TOKEN=... python tools/weekly_report.py [--end 2026-11-16]           # print it
    GOATCOUNTER_API_TOKEN=... CONTACT_FORM_KEY=... python tools/weekly_report.py --send  # e-mail it
    CONTACT_FORM_KEY=... python tools/weekly_report.py --test-send                       # delivery check only

The week is the last full Monday-Sunday (UTC) before --end (default: today), compared with the week before.
The report is e-mailed through Web3Forms with the contact form's key (CONTACT_FORM_KEY), so it lands in the
same inbox as messages from the site and nothing is published (the repo and its Actions logs are public, so the
workflow does not print the report). GOATCOUNTER_API_TOKEN is a GoatCounter API key with only "Read statistics"
for this site; both live in GitHub secrets, never in the repo. Used by .github/workflows/weekly-report.yml.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

READ_EVENTS = ("read-50", "read-90", "time-1m", "time-3m")


def fail(msg):
    sys.exit("weekly_report: " + msg)


class API:
    def __init__(self, site, token):
        self.base = "https://%s.goatcounter.com/api/v0/" % site
        self.token = token

    def get(self, path, **params):
        url = self.base + path + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + self.token,
                                                   "Content-Type": "application/json"})
        for attempt in range(5):
            time.sleep(0.3)  # the API allows 4 requests per second
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 4:
                    time.sleep(2)
                    continue
                fail("%s -> HTTP %d: %s" % (url, e.code, e.read()[:300].decode("utf-8", "replace")))


def week(end):
    """[start, end) of the last full Monday-Sunday week before the day `end`."""
    monday = end - dt.timedelta(days=end.weekday())
    return monday - dt.timedelta(days=7), monday


def rng(start, end):
    return {"start": start.strftime("%Y-%m-%dT00:00:00Z"), "end": end.strftime("%Y-%m-%dT00:00:00Z")}


def hits(api, r):
    out, exclude = [], []
    while True:
        params = dict(r, limit=100)
        if exclude:
            params["exclude_paths"] = ",".join(exclude)
        d = api.get("stats/hits", **params)
        out += d.get("hits") or []
        if not d.get("more"):
            return out
        exclude = [str(h["path_id"]) for h in out]


def stats(api, page, r, limit=10):
    return api.get("stats/" + page, limit=limit, **r).get("stats") or []


def delta(now, before):
    if not before:
        return "(новое)" if now else ""
    d = now - before
    return "(%+d)" % d if d else "(=)"


def lines(rows):
    """Rows as "  <number>  <text>": the number first, so it reads in a proportional e-mail font too."""
    if not rows:
        return ["  нет данных"]
    w = max(len(str(r[0])) for r in rows)
    return ["  %s  %s" % (str(r[0]).rjust(w), "  ".join(str(c) for c in r[1:] if c != "")) for r in rows]


def report(api, site, today):
    start, end = week(today)
    cur, prev = rng(start, end), rng(start - dt.timedelta(days=7), start)

    tot, tot_prev = api.get("stats/total", **cur), api.get("stats/total", **prev)
    h, h_prev = hits(api, cur), hits(api, prev)
    prev_count = {(x["path"], x["event"]): x["count"] for x in h_prev}
    pages = [x for x in h if not x["event"]]
    events = [x for x in h if x["event"]]

    def ev(prefix, before=False):
        if before:
            return sum(c for (p, e), c in prev_count.items() if e and p.startswith(prefix))
        return sum(x["count"] for x in events if x["path"].startswith(prefix))

    def was(now, before):
        return "(было %d)" % before if before != now else "(=)"

    last_day = end - dt.timedelta(days=1)
    period = "%s – %s" % (start.strftime("%d.%m"), last_day.strftime("%d.%m.%Y"))
    out = ["Статистика favorart.github.io за неделю %s (UTC); в скобках — изменение к прошлой неделе." % period,
           "Дашборд: https://%s.goatcounter.com" % site, ""]

    visitors = tot.get("total", 0) - tot.get("total_events", 0)
    visitors_prev = tot_prev.get("total", 0) - tot_prev.get("total_events", 0)
    out.append("КОРОТКО")
    out += lines([[visitors, "посетителей", was(visitors, visitors_prev)]] +
                 [[ev(p), name, was(ev(p), ev(p, True))] for p, name in (
                     ("form/contact-sent", "сообщений через форму"),
                     ("click/contact", "кликов «Связаться»"),
                     ("out/", "переходов наружу (LinkedIn, GitHub…)"),
                     ("download/", "скачиваний"))])

    out += ["", "СТРАНИЦЫ (визиты)"]
    out += lines([[x["count"], x["path"], delta(x["count"], prev_count.get((x["path"], False), 0))]
                  for x in sorted(pages, key=lambda x: -x["count"])[:15]])

    reading = {}
    for x in events:
        for name in READ_EVENTS:
            if x["path"].startswith(name + "/"):
                reading.setdefault("/" + x["path"][len(name) + 1:], {})[name] = x["count"]
    visits = {x["path"]: x["count"] for x in pages}
    out += ["", "ДОЧИТЫВАНИЕ (визиты / прокрутили до 50% / до 90% / вкладка открыта ≥1 мин / ≥3 мин)"]
    out += lines([["%s / %s / %s / %s / %s" % (visits.get(p, "?"), *[r.get(n, 0) for n in READ_EVENTS]), p]
                  for p, r in sorted(reading.items(), key=lambda kv: -visits.get(kv[0], 0))[:15]])

    clicks = [x for x in events if not any(x["path"].startswith(n + "/") for n in READ_EVENTS)]
    out += ["", "КЛИКИ"]
    out += lines([[x["count"], x["path"], delta(x["count"], prev_count.get((x["path"], True), 0)),
                   "— " + x["title"] if x.get("title") and x["title"] != x["path"] else ""]
                  for x in sorted(clicks, key=lambda x: -x["count"])[:20]])

    for title, page in (("СТРАНЫ И РЕГИОНЫ", "locations"), ("ИСТОЧНИКИ", "toprefs"),
                        ("КАМПАНИИ (utm_campaign)", "campaigns"), ("ЯЗЫКИ БРАУЗЕРА", "languages"),
                        ("ЭКРАНЫ", "sizes")):
        s, s_prev = stats(api, page, cur), stats(api, page, prev, limit=100)
        before = {x["name"]: x["count"] for x in s_prev}
        out += ["", title]
        out += lines([[x["count"], x["name"] or "(нет данных)", delta(x["count"], before.get(x["name"], 0))]
                      for x in s])

    out += ["", "«(нет данных)» в источниках — переходы без реферера (приложение LinkedIn, lnkd.in).",
            "Ссылки в постах ставь с ?ref=linkedin&utm_campaign=<пост>."]
    return "статистика за неделю %s" % period, "\n".join(out)


def send(subject, text):
    """E-mail through Web3Forms with the contact form's key (the same inbox as the site's messages)."""
    key = os.environ.get("CONTACT_FORM_KEY", "")
    if not key:
        fail("CONTACT_FORM_KEY is not set")
    data = json.dumps({"access_key": key, "subject": "favorart.github.io: " + subject,
                       "from_name": "favorart.github.io", "name": "Weekly report (GoatCounter)",
                       "message": text}).encode()
    req = urllib.request.Request("https://api.web3forms.com/submit", data=data, headers={
        "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "site-weekly-report"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        fail("Web3Forms -> HTTP %d: %s" % (e.code, e.read()[:300].decode("utf-8", "replace")))
    if not res.get("success"):
        fail("Web3Forms: %s" % res.get("message", res))
    print("sent:", res.get("message", "ok"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=os.environ.get("GOATCOUNTER_CODE", "favorart"))
    ap.add_argument("--end", help="YYYY-MM-DD, default today (UTC)")
    ap.add_argument("--send", action="store_true", help="e-mail the report instead of printing it")
    ap.add_argument("--test-send", action="store_true", help="only check that an e-mail gets through")
    a = ap.parse_args()
    if a.test_send:
        send("weekly report (test)", "Проверка доставки еженедельного отчёта GoatCounter. Статистики здесь нет.")
        return
    token = os.environ.get("GOATCOUNTER_API_TOKEN", "")
    if not token:
        fail("GOATCOUNTER_API_TOKEN is not set")
    today = dt.date.fromisoformat(a.end) if a.end else dt.datetime.now(dt.timezone.utc).date()
    subject, text = report(API(a.site, token), a.site, today)
    if a.send:
        send(subject, text)  # not printed: Actions logs of a public repo are public
    else:
        print(subject + "\n\n" + text)


if __name__ == "__main__":
    main()
