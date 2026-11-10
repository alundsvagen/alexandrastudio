#!/usr/bin/env python3
"""Imports the ecosystem research sheet into the fintech database.

  python3 _tools/import_research.py <research.xlsx>
  python3 _tools/score_trending.py --replies ... --readers ...   (new companies can now be scored)
  python3 _tools/build_database.py

Reads the private research export (one row per company: Company, Domain, Vertical, City,
Country, Address, People you know, People who answer, One-liner, Summary, Offering, Serves,
Keywords) and writes _tools/data/company-research.csv with the public company description only.

Left out on purpose:
  People you know / People who answer   relationship data, private
  Address                               not needed; city and country are enough
  most Network rows                     only the agencies and venues named in the guides are kept
  rows the research could not read, or that describe a different company than the domain
"""
import csv, re, sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'data' / 'company-research.csv'
COLS = ['domain', 'name', 'vertical', 'city', 'country', 'one_liner', 'summary', 'offering', 'serves', 'keywords']
COUNTRY = {'Czech Republic': 'Czechia'}
# the research matched these domains to the wrong company
WRONG = {'eqt.com', 'eg.dk', 'konsulat-seychellen.de'}
# right description, wrong or odd name in the sheet
NAME_FIX = {'skjoldet.dk': 'Skjoldet', 'idnow.io': 'IDnow'}
# headquarters the research left blank (checked by hand; country only where the city is uncertain)
LOCATION = {
    'apiax.com': ('Zurich', 'Switzerland'), 'banqsoft.com': ('Oslo', 'Norway'),
    'encompasscorporation.com': ('Glasgow', 'United Kingdom'), 'envira.dk': ('', 'Denmark'),
    'kaizenreporting.com': ('London', 'United Kingdom'), 'kleer.se': ('', 'Sweden'),
    'konsentus.com': ('', 'United Kingdom'), 'marginalen.se': ('Stockholm', 'Sweden'),
    'mastercard.com': ('Purchase', 'United States'), 'opensee.io': ('Paris', 'France'),
    'raisin.bank': ('Berlin', 'Germany'), 'rs2.com': ('', 'Malta'), 'sbab.se': ('Solna', 'Sweden'),
    'shoptet.cz': ('Prague', 'Czechia'), 'skippay.cz': ('', 'Czechia'),
    'vippsmobilepay.com': ('Oslo', 'Norway'), 'virtusa.com': ('', 'United States'),
    'glia.com': ('New York', 'United States'), 'hummingbird.co': ('', 'United States'),
    'idemia.com': ('', 'France'), 'nayaone.com': ('London', 'United Kingdom'), 'nium.com': ('', 'Singapore'),
    'scrive.com': ('Stockholm', 'Sweden'), 'spitch.ai': ('Zurich', 'Switzerland'),
    'trustfull.com': ('Milan', 'Italy'), 'voxsmart.com': ('London', 'United Kingdom'),
    'webid-solutions.com': ('Berlin', 'Germany'), 'wealth-dynamix.com': ('', 'United Kingdom'),
    'profilesw.com': ('', 'Greece'), '2izii.no': ('', 'Norway'), 'fintru.com': ('Belfast', 'United Kingdom'),
}
# Network rows (agencies, venues, investors, other companies we know) stay private, except the
# agencies and venues the guides describe
NETWORK_KEEP = {'heijbelgrowth.com', 'growthhackers.se', 'precis.com', 'topvisible.se', 'hartmanagency.se',
                'storykit.io', 'ahouse.se', 'embassy.house', 'munchenbryggeriet.se', 'convendum.se'}
UNREADABLE = re.compile(r"could not be read|cannot be confirmed|does not describe|no readable content|"
                        r"from what was read|captured page names only", re.I)

def clean(v):
    return re.sub(r'\s+', ' ', str(v or '')).strip()

def main(path):
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
    it = ws.iter_rows(values_only=True)
    head = [clean(h) for h in next(it)]
    out, seen_line, seen_dom, skipped = [], set(), set(), []
    for v in it:
        r = {h: clean(x) for h, x in zip(head, v)}
        dom = r['Domain'].lower().removeprefix('www.')
        text = ' '.join([r['One-liner'], r['Summary']])
        if not dom or not r['One-liner']:
            continue
        if r['Vertical'] == 'Network' and dom not in NETWORK_KEEP:
            continue
        if dom in WRONG or UNREADABLE.search(text):
            skipped.append(r['Company'])
            continue
        if dom in seen_dom or r['One-liner'] in seen_line:   # the same company listed twice
            continue
        seen_dom.add(dom); seen_line.add(r['One-liner'])
        city, country = r['City'], COUNTRY.get(r['Country'], r['Country'])
        if not country and dom in LOCATION:
            city, country = LOCATION[dom]
        out.append({'domain': dom, 'name': NAME_FIX.get(dom, r['Company']), 'vertical': r['Vertical'],
                    'city': city, 'country': country,
                    'one_liner': r['One-liner'], 'summary': r['Summary'], 'offering': r['Offering'],
                    'serves': r['Serves'], 'keywords': r['Keywords']})
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(out)
    print(f'{len(out)} companies written to {OUT.name}; left out (unreadable or wrong company): {", ".join(skipped)}')

if __name__ == '__main__':
    main(sys.argv[1])
