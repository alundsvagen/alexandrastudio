#!/usr/bin/env python3
"""Scores the Fintech Award Points in the fintech database.

  python3 _tools/score_trending.py --replies <replies.xlsx> --readers <substack-export.csv> [--today YYYY-MM-DD]
  python3 _tools/build_database.py

Reads two private exports. Keep them out of the repo:
  replies.xlsx   companies that replied to or emailed us
                 (Company, Website, Category, Emails from them, Last contact)
  readers.csv    the Substack subscriber export (Email, Type, Activity = 0-5 stars)

Writes _tools/data/trending.csv with company name, domain and points only, and
_tools/data/newsletter-stats.json with whole-list totals (subscribers, work-email share,
open rates, star mix). No email addresses, people, or per-company counts leave this script.

Fintech Award Points. Every scored company starts at 105, then:
  +60   based outside Stockholm
  +150  replied to us in the past month
  +80   emailed us back at least 4 times
  for each newsletter reader at the company: 5 stars +100, 4 stars +80, 3 stars +50,
  2 stars +30, 1 star +5
Only rows marked Fintech in the replies sheet count. A reader counts when their work email
domain matches a company in the database; personal addresses (Gmail and so on) are skipped.
"""
import argparse, collections, csv, datetime, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_database import load, domain, outside_stockholm, TRENDING, ALIASES  # noqa: E402

BASE, OUTSIDE, RECENT, REPLIES_4 = 105, 60, 150, 80
STARS = {5: 100, 4: 80, 3: 50, 2: 30, 1: 5}

FREE_MAIL = {'gmail', 'googlemail', 'hotmail', 'outlook', 'live', 'msn', 'yahoo', 'icloud', 'me', 'mac',
             'protonmail', 'proton', 'aol', 'gmx', 'web', 'telia', 'bredband', 'comhem', 'bahnhof', 'mail'}
NOT_A_COMPANY = {'google.com', 'linkedin.com', 'facebook.com', 'instagram.com', 'alexandrastudio.se'}
def norm_name(s):
    s = re.sub(r'\(.*?\)', ' ', s.lower())
    s = re.sub(r'\b(ab|gmbh|ltd|limited|as|a/s|oy|oü|sa|bv|inc|plc|group)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', '', s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--replies', required=True)
    ap.add_argument('--readers', required=True)
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    a = ap.parse_args()
    today = datetime.date.fromisoformat(a.today)
    month_ago = today - datetime.timedelta(days=30)

    rows = load()
    by_domain, by_name = {}, {}
    for r in rows:
        if r['domain'] and r['domain'] not in NOT_A_COMPANY:
            by_domain.setdefault(r['domain'], r)
        by_name.setdefault(norm_name(r['name']), r)

    def company(dom='', name=''):
        dom = ALIASES.get(dom, dom)
        if dom and dom in by_domain:
            return by_domain[dom]
        return by_name.get(norm_name(name)) if name else None

    # 1. replies sheet
    import openpyxl
    ws = openpyxl.load_workbook(a.replies, read_only=True, data_only=True).active
    it = ws.iter_rows(values_only=True)
    head = [str(h).strip() for h in next(it)]
    col = {h: i for i, h in enumerate(head)}
    emails = collections.Counter()
    last = {}
    missing = []
    for v in it:
        if not v or str(v[col['Category']] or '').strip() != 'Fintech':
            continue
        name = str(v[col['Company']] or '').strip()
        site = str(v[col['Website']] or '').strip().lower()
        host = site.split('//', 1)[-1].split('/', 1)[0]
        r = company(domain(host[4:] if host.startswith('www.') else host), name)
        if not r:
            missing.append(name)
            continue
        key = id(r)
        emails[key] += int(v[col['Emails from them']] or 0)
        when = v[col['Last contact']]
        d = when.date() if isinstance(when, datetime.datetime) else datetime.date.fromisoformat(str(when)[:10]) if when else None
        if d and (key not in last or d > last[key]):
            last[key] = d

    # 2. newsletter readers
    readers = collections.Counter()
    tot = collections.Counter(); stars_mix = collections.Counter(); orgs = set()
    with open(a.readers, newline='', encoding='utf-8-sig') as f:
        for s in csv.DictReader(f):
            if s.get('Type') == 'Author':
                continue
            dom = domain(s['Email'].strip().lower().rsplit('@', 1)[-1])
            tot['subs'] += 1
            tot['open6'] += int(s.get('Emails opened (6mo)') or 0) > 0
            tot['open30'] += int(s.get('Emails opened (30d)') or 0) > 0
            stars_mix[int(s.get('Activity') or 0)] += 1
            if dom and dom.split('.')[0] not in FREE_MAIL:
                tot['work'] += 1; orgs.add(dom)
            if not dom or dom.split('.')[0] in FREE_MAIL or dom in NOT_A_COMPANY:
                continue
            stars = int(s.get('Activity') or 0)
            r = company(dom)
            if r and stars in STARS:
                readers[id(r)] += STARS[stars]

    pct = lambda k: round(tot[k] * 100 / tot['subs']) if tot['subs'] else 0
    stats = {'date': a.today, 'subscribers': tot['subs'], 'work_email_pct': pct('work'), 'organisations': len(orgs),
             'opened_6mo_pct': pct('open6'), 'opened_30d_pct': pct('open30'),
             'stars': {str(k): stars_mix[k] for k in range(5, -1, -1)}}
    (TRENDING.parent / 'newsletter-stats.json').write_text(json.dumps(stats, indent=1), encoding='utf-8')

    # 3. points
    out = []
    for r in rows:
        key = id(r)
        if key not in emails and key not in last and not readers[key]:
            continue
        p = BASE
        p += OUTSIDE if outside_stockholm(r) is True else 0
        p += RECENT if last.get(key) and last[key] >= month_ago else 0
        p += REPLIES_4 if emails[key] >= 4 else 0
        p += readers[key]
        out.append((r['name'], r['domain'], p))
    out.sort(key=lambda t: (-t[2], t[0].lower()))

    with open(TRENDING, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['name', 'domain', 'points'])
        w.writerows(out)
    print(f'{len(out)} companies with Fintech Award Points written to {TRENDING.relative_to(TRENDING.parents[2])}')
    if missing:
        print('Not in the database, so not scored: ' + ', '.join(sorted(set(missing))))

if __name__ == '__main__':
    main()
