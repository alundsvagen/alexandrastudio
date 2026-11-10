#!/usr/bin/env python3
"""Builds the fintech database:

  trending.html                       the Trending page (filterable table, 10 rows, bottom 5 blurred)
  data/fintechs.json                  the data the table filters (no emails)
  fintech-companies/<slug>.html       one page per country, sector, the Nordics and Stockholm,
                                      each listing every company so search engines can index them

Run from the repo root:   python3 _tools/build_database.py
Source lists: _tools/data/fintech-companies.csv (EU FinTech Map, cleaned; emails removed)
              _tools/data/network-companies.csv (companies from our own network, added by hand)
Fintech Award Points: _tools/data/trending.csv, written by _tools/score_trending.py.
Company research:    _tools/data/company-research.csv, written by _tools/import_research.py.
"""
import csv, collections, json, re, statistics
from site_chrome import ROOT, SITE, E, head, header, tail

DATA = ROOT / '_tools' / 'data' / 'fintech-companies.csv'
NETWORK = ROOT / '_tools' / 'data' / 'network-companies.csv'
TRENDING = ROOT / '_tools' / 'data' / 'trending.csv'
RESEARCH = ROOT / '_tools' / 'data' / 'company-research.csv'
# same company, another domain (used to match research rows and newsletter readers)
ALIASES = {'seb.se': 'sebx.io', 'sebgroup.com': 'sebx.io', 'nordea.dk': 'nordea.com', 'nordea.se': 'nordea.com',
           'danskebank.com': 'danskebank.dk', 'handelsbanken.com': 'handelsbanken.se', 'svea.se': 'svea.com',
           'tieto.com': 'tietoevry.com', '11fsholdings.com': '11fs.com', 'findity.com': 'findity.se',
           'britepayments.com': 'britepaymentgroup.com', 'sitoo.com': 'sitoo.se', 'flatpay.dk': 'flatpay.com',
           'trustly.com': 'trustly.net', 'tryg.dk': 'tryg.com', 'northmill.se': 'northmill.com',
           'payex.com': 'payex.se', 'silverflow.com': 'silverflow.co', 'basikon.io': 'basikon.com',
           '2izii.com': '2izii.no'}
# the source put a street address where these cities should be
CITY_FIX = {'Klarna': 'Stockholm', 'Insurely': 'Stockholm', 'Fimento': 'Stockholm',
            'Wise Europe': 'Brussels', 'Mifundo': 'Tallinn', 'Scalable': 'Munich'}
# Stockholm and the municipalities around it count as Stockholm for the trending points
STOCKHOLM_AREA = {'Stockholm', 'Solna', 'Sundbyberg', 'Nacka', 'Danderyd', 'Täby', 'Lidingö', 'Huddinge',
                  'Segeltorp', 'Bromma', 'Kista', 'Sollentuna', 'Järfälla'}
NO_HUB = {'United Kingdom', 'United States'}  # outside the EU source: too few rows for a page of their own
UPDATED = 'November 2026'
SUBSCRIBERS = 1600
ICP_URL = '/icp-list.html'
CONTACT_URL = 'https://calendly.com/alexandra-alexandrastudio/30min'
ADD_FORM = '/add-your-company.html'        # page to be built
REMOVE_FORM = '/remove-your-company.html'  # page to be built
SOURCE_NAME = 'EU FinTech Map, EU Digital Finance Platform (European Commission)'
SOURCE_URL = 'https://digital-finance-platform.ec.europa.eu/observatory/eu-fintech-map'

SECTORS = ['Payments', 'Banking', 'Lending', 'Wealth Management', 'Insurance', 'Crypto and DeFi',
           'Regtech', 'Financial Management', 'Real Estate', 'Spend Management']
SECTOR_SHORT = {'Wealth Management': 'Wealth', 'Crypto and DeFi': 'Crypto & DeFi',
                'Financial Management': 'Finance software', 'Spend Management': 'Spend'}
SECTOR_SLUG = {'Payments': 'payments', 'Banking': 'banking', 'Lending': 'lending',
               'Wealth Management': 'wealth-management', 'Insurance': 'insurtech',
               'Crypto and DeFi': 'crypto-defi', 'Regtech': 'regtech',
               'Financial Management': 'financial-management', 'Real Estate': 'proptech-real-estate'}
SECTOR_NOUN = {'Payments': 'payments', 'Banking': 'banking and neobank', 'Lending': 'lending',
               'Wealth Management': 'wealth management and wealthtech', 'Insurance': 'insurtech',
               'Crypto and DeFi': 'crypto and DeFi', 'Regtech': 'regtech',
               'Financial Management': 'financial management software', 'Real Estate': 'proptech and real-estate finance'}
DEMONYM = {'Germany': 'German', 'France': 'French', 'Netherlands': 'Dutch', 'Spain': 'Spanish', 'Sweden': 'Swedish',
           'Italy': 'Italian', 'Poland': 'Polish', 'Ireland': 'Irish', 'Denmark': 'Danish', 'Belgium': 'Belgian',
           'Estonia': 'Estonian', 'Austria': 'Austrian', 'Lithuania': 'Lithuanian', 'Finland': 'Finnish',
           'Czechia': 'Czech', 'Cyprus': 'Cypriot', 'Luxembourg': 'Luxembourg', 'Portugal': 'Portuguese',
           'Romania': 'Romanian', 'Malta': 'Maltese', 'Latvia': 'Latvian', 'Hungary': 'Hungarian',
           'Bulgaria': 'Bulgarian', 'Slovakia': 'Slovak', 'Greece': 'Greek', 'Croatia': 'Croatian',
           'Slovenia': 'Slovenian', 'Norway': 'Norwegian', 'Switzerland': 'Swiss', 'Iceland': 'Icelandic'}
NORDICS = ['Sweden', 'Denmark', 'Finland', 'Norway']

POSTS = [  # Stockholm Growth & Fintech, most recent first
    dict(title='The Fintech German Market: Why so into crypto?', date='2026-11-08', label='8 Nov 2026',
         url='https://stockholmgrowthfintech.substack.com/p/the-fintech-german-market-why-so',
         img='$s_!PwwV!,w_480,h_300,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F03216349-82b2-4412-8bc5-e76ad81eb2dc_1496x914.png',
         dek="Hello from Germany. We're spending a month meeting fintechs in Berlin, Hamburg and Frankfurt."),
    dict(title='Opportunities in Regulation: The Swedish Regulation Cheat Sheet', date='2026-10-25', label='25 Oct 2026',
         url='https://stockholmgrowthfintech.substack.com/p/opportunities-in-regulation-the-swedish',
         img='$s_!jWmh!,w_480,h_300,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa3079e6a-66ca-498d-8452-2643475e8575_794x1000.png',
         dek='Swedish fintech regulations 101, written in simple language to make the dry stuff digestible.'),
    dict(title='Trend Setting Emotional Fintech Ad Campaigns', date='2026-10-18', label='18 Oct 2026',
         url='https://stockholmgrowthfintech.substack.com/p/trend-setting-emotional-fintech-ad',
         img='$s_!L-5z!,w_480,h_300,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9073c742-8c4f-4fd6-8a13-9fe18790df79_2030x1126.png',
         dek='Three beautiful fintech campaigns for different audiences, and why they work.'),
]

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def domain(host):
    """example.com from www.app.example.com; keeps two-part country suffixes like example.co.uk."""
    p = host.lower().split('.')
    if len(p) >= 3 and p[-2] in ('co', 'com', 'org') and len(p[-1]) == 2:
        return '.'.join(p[-3:])
    return '.'.join(p[-2:]) if host else ''

def outside_stockholm(r):
    """True/False, or None when we only know the company is somewhere in Sweden."""
    if r['country'] != 'Sweden':
        return True
    if not r['city']:
        return None
    return r['city'] not in STOCKHOLM_AREA

def load_trending():
    if not TRENDING.exists():
        return {}
    return {(t['name'], t['domain']): int(t['points']) for t in csv.DictReader(open(TRENDING, encoding='utf-8'))}

def load_research():
    if not RESEARCH.exists():
        return []
    return list(csv.DictReader(open(RESEARCH, encoding='utf-8')))

# Sector from what a company says it does (used when the source list has no sector)
SECTOR_RULES = [
    ('Payments', r'payment|checkout|acquir|card issu|issuer processing|\bpsp\b|remittance|payout|point of sale|\bpos\b|wallet|money transfer|cross-border'),
    ('Banking', r'core banking|neobank|digital bank|banking-as-a-service|\bbaas\b|banking platform|banking software|mobile banking|open banking|\bbank\b'),
    ('Lending', r'lending|\bloans?\b|credit|factoring|financing|buy now|\bbnpl\b|mortgage|deferred payment'),
    ('Wealth Management', r'wealth|investment|invest\b|asset manag|portfolio|pension|brokerage|trading'),
    ('Insurance', r'insur'),
    ('Crypto and DeFi', r'crypto|blockchain|stablecoin|digital asset|tokeni|web3|defi\b'),
    ('Regtech', r'\bkyc\b|\bkyb\b|\baml\b|compliance|fraud|identity|regtech|sanction|e-?signature|\beid\b|verification|surveillance|regulatory'),
    ('Financial Management', r'accounting|fp&a|invoic|\berp\b|bookkeeping|reconciliation|\bcfo\b|budget|forecast|financial planning|treasury|billing|reporting'),
    ('Real Estate', r'real estate|property|proptech'),
    ('Spend Management', r'expense|spend management|corporate card'),
]
def infer_sectors(p):
    text = ' '.join([p['keywords'], p['offering'], p['one_liner']]).lower()
    hits = [(len(re.findall(rx, text)), s) for s, rx in SECTOR_RULES]
    return [s for n, s in sorted(hits, key=lambda t: -t[0]) if n][:3]

def slugify(s):
    s = s.lower().replace('&', ' and ').replace('ó', 'o').replace('ö', 'o').replace('ä', 'a').replace('å', 'a').replace('ø', 'o').replace('æ', 'ae').replace('é', 'e').replace('ü', 'u')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def split_list(s):
    return [x.strip() for x in re.split(r';\s*', s or '') if x.strip()]

def load():
    rows = list(csv.DictReader(open(DATA, encoding='utf-8'))) + list(csv.DictReader(open(NETWORK, encoding='utf-8')))
    # companies researched by the Alexandra Studio team: enrich the matching row, or add the company
    by_dom = {}
    for r in rows:
        w = r['website'].strip().lower()
        h = w.split('//', 1)[-1].split('/', 1)[0]
        d = domain(h[4:] if h.startswith('www.') else h)
        if d:
            by_dom.setdefault(d, r)
    for p in load_research():
        if p['vertical'] not in ('Fintech', 'Hackathons'):
            continue
        d = ALIASES.get(domain(p['domain']), domain(p['domain']))
        r = by_dom.get(d)
        if r is None:
            if not p['country']:
                continue
            r = {'name': p['name'], 'slug': slugify(p['name']), 'sectors': '|'.join(infer_sectors(p)),
                 'country': p['country'], 'city': p['city'], 'founded': '', 'website': 'https://' + p['domain'],
                 'description': '', 'source_url': ''}
            rows.append(r); by_dom[d] = r
        elif not r['city'] and p['city'] and p['country'] == r['country']:
            r['city'] = p['city']
        if not r['sectors']:
            r['sectors'] = '|'.join(infer_sectors(p))
        # two research rows for one company (nordea.com and nordea.dk): keep the main domain's
        if r.get('profile') is None or domain(p['domain']) == d and domain(r['profile']['domain']) != d:
            r['profile'] = p
    pts = load_trending()
    for r in rows:
        r['tags'] = [t for t in r['sectors'].split('|') if t] if r['sectors'] else []
        r['year'] = int(r['founded']) if r['founded'] else 0
        w = r['website'].strip()
        r['url'] = w if w.startswith('http') else ('https://' + w if w else '')
        h = r['url'].split('//', 1)[-1].split('/', 1)[0].lower() if r['url'] else ''
        r['host'] = h[4:] if h.startswith('www.') else h
        r['domain'] = domain(r['host'])
        # the source sometimes puts a street address where the city should be
        c = re.sub(r'^\d[\d\s-]*', '', r['city']).strip()
        r['city'] = '' if (re.search(r'\d', c) or re.search(r'(str\.|straat|strasse|straße|street|road|calle|via |rue |avenue|ul\.)', c, re.I)) else c
        if not r['city'] and r['name'] in CITY_FIX:
            r['city'] = CITY_FIX[r['name']]
        r['pts'] = pts.get((r['name'], r['domain']), 0)
        r.setdefault('profile', None)
    # default order: companies with Fintech Award Points first (most points first), then complete
    # records (sector + city + website), newest first, then A-Z
    rows.sort(key=lambda r: (-r['pts'], -(bool(r['tags']) and bool(r['city']) and bool(r['url'])), -r['year'], r['name'].lower()))
    # profile page URLs, unique
    used = set()
    for r in rows:
        if r['profile']:
            s = slugify(r['name']) or slugify(r['domain'])
            if s in used:
                s = slugify(r['name'] + ' ' + r['country'])
            used.add(s)
            r['purl'] = f'/fintech-company/{s}.html'
        else:
            r['purl'] = ''
    return rows

ROWS = load()
TOTAL = len(ROWS)
COUNTRIES = [c for c, _ in collections.Counter(r['country'] for r in ROWS).most_common()]
TOP_PTS = ROWS[0]['pts'] if ROWS and ROWS[0]['pts'] else 0
N_TRENDING = sum(1 for r in ROWS if r['pts'])
RANKED = [r for r in ROWS if r['pts']]
RANK = {id(r): i + 1 for i, r in enumerate(RANKED)}  # ties share the order they sort in
PROFILED = [r for r in ROWS if r['profile']]

def fmt(n): return f'{n:,}'
def sector_label(r): return ', '.join(SECTOR_SHORT.get(t, t) for t in r['tags']) or 'Other fintech'
def place(r): return f"{r['city']}, {r['country']}" if r['city'] else r['country']

# --------------------------------------------------------------------------
# Shared bits
# --------------------------------------------------------------------------
AWARDS_URL = '/fintech-awards.html'

def trend_html(r):
    """Green Fintech Award Points badge (+ the #1 label) next to a company name."""
    if not r['pts']:
        return ''
    top = '<span class="db-top">#1 Fintech Award</span>' if r['pts'] == TOP_PTS else ''
    return f'<span class="db-trend"><span class="db-pts" title="Fintech Award Points">+{fmt(r["pts"])}</span>{top}</span>'

def trend_legend(n=None):
    n = N_TRENDING if n is None else n
    if not n:
        return ''
    who = 'the company' if n == 1 else f'the {fmt(n)} companies'
    return ('<p class="db-legend"><span class="db-pts" aria-hidden="true">+</span> '
            f'<span><a href="{AWARDS_URL}">Fintech Award Points</a>: {who} most active with Nordic fintech buyers, '
            'partners and our readers right now, highest first.</span></p>')

def row_html(r, blur=0):
    # blur 1-5: visible but increasingly blurred; 6: in the page (for search engines) but not shown.
    # Every gated row carries .db-locked, which the paywall structured data points at.
    if blur == 6:
        hidden = ' class="db-locked db-hide" aria-hidden="true"'
    elif blur:
        hidden = f' class="db-locked is-blur b{blur}" aria-hidden="true"'
    else:
        hidden = ''
    name = E(r['name'])
    if r['purl'] and not blur:
        name_html = f'<a href="{r["purl"]}">{name}</a>'
    elif r['url'] and not blur:
        name_html = f'<a href="{E(r["url"])}" target="_blank" rel="nofollow noopener">{name}</a>'
    else:
        name_html = name
    host = f'<span class="db-host">{E(r["host"])}</span>' if r['host'] else ''
    return (f'<tr{hidden}><td class="db-name"><span class="db-co">{name_html}</span>{trend_html(r)}{host}</td>'
            f'<td class="db-sec">{E(sector_label(r))}</td><td class="db-loc">{E(place(r))}</td>'
            f'<td class="db-year">{r["year"] or "–"}</td></tr>')

def table_head():
    return ('<thead><tr><th scope="col">Company</th><th scope="col">Sector</th>'
            '<th scope="col">Location</th><th scope="col">Founded</th></tr></thead>')

def crumbs(items):
    parts = []
    for i, (name, href) in enumerate(items):
        parts.append(f'<a href="{href}">{E(name)}</a>' if href else f'<span>{E(name)}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + '<span aria-hidden="true">/</span>'.join(parts) + '</nav>'

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + (h or '')} for i, (n, h) in enumerate(items)]}

# --------------------------------------------------------------------------
# Hubs (indexable pages)
# --------------------------------------------------------------------------
HUBS = []  # (slug, kind, label, rows)
for c in COUNTRIES:
    rs = [r for r in ROWS if r['country'] == c]
    if len(rs) >= 10 and c not in NO_HUB:
        HUBS.append(dict(slug=c.lower().replace(' ', '-'), kind='country', key=c, rows=rs))
HUBS.append(dict(slug='nordics', kind='region', key='Nordics', rows=[r for r in ROWS if r['country'] in NORDICS]))
HUBS.append(dict(slug='stockholm', kind='city', key='Stockholm',
                 rows=[r for r in ROWS if r['country'] == 'Sweden' and r['city'] == 'Stockholm']))
for s, slug in SECTOR_SLUG.items():
    rs = [r for r in ROWS if s in r['tags']]
    HUBS.append(dict(slug=slug, kind='sector', key=s, rows=rs))
HUB_BY = {(h['kind'], h['key']): h for h in HUBS}

def hub_url(h): return f'/fintech-companies/{h["slug"]}.html'

def hub_title(h):
    n = fmt(len(h['rows']))
    if h['kind'] == 'country':
        return f'Fintech Companies in {h["key"]}: {n} {DEMONYM[h["key"]]} Fintechs (2026)', f'Fintech companies in {h["key"]}'
    if h['kind'] == 'region':
        return f'Nordic Fintech Companies: {n} Fintechs in Sweden, Denmark, Finland and Norway', 'Nordic fintech companies'
    if h['kind'] == 'city':
        return f'Fintech Companies in Stockholm: {n} Stockholm Fintechs (2026)', 'Fintech companies in Stockholm'
    noun = SECTOR_NOUN[h['key']]
    cap = noun[0].upper() + noun[1:]
    return f'{cap} Fintech Companies in Europe: {n} Companies (2026)', f'{cap} fintech companies in Europe'

def top(counter, k=3):
    return [(a, b) for a, b in counter.most_common() if a][:k]

def join_list(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]

def hub_lead(h):
    rs = h['rows']; n = len(rs)
    years = [r['year'] for r in rs if r['year']]
    med = int(statistics.median(years)) if years else None
    sectors = collections.Counter(t for r in rs for t in r['tags'])
    cities = collections.Counter(r['city'] for r in rs)
    countries = collections.Counter(r['country'] for r in rs)
    since = sum(1 for y in years if y >= 2020)
    bits = []
    if h['kind'] in ('country', 'city', 'region'):
        where = {'country': h['key'], 'city': 'Stockholm', 'region': 'the Nordics'}[h['kind']]
        bits.append(f'Our database lists {fmt(n)} fintech companies in {where}.')
        if h['kind'] == 'region':
            bits.append('By country: ' + join_list(f'{c} ({fmt(k)})' for c, k in top(countries, 4)) + '.')
        elif h['kind'] == 'country' and len(top(cities)) > 0:
            bits.append('The biggest hubs are ' + join_list(f'{c} ({k})' for c, k in top(cities)) + '.')
        if sectors:
            bits.append('The largest categories are ' + join_list(f'{SECTOR_SHORT.get(s, s).lower()} ({k})' for s, k in top(sectors)) + '.')
    else:
        bits.append(f'Our database lists {fmt(n)} European fintech companies working in {SECTOR_NOUN[h["key"]]}.')
        bits.append('Most are based in ' + join_list(f'{c} ({k})' for c, k in top(countries, 4)) + '.')
        if top(cities):
            bits.append('Leading cities: ' + join_list(f'{c} ({k})' for c, k in top(cities)) + '.')
    if med:
        bits.append(f'The median company was founded in {med}, and {since} were founded in 2020 or later.')
    return ' '.join(bits), med, sectors, cities, countries

def related_links(h):
    links = []
    if h['kind'] in ('country', 'city', 'region'):
        sectors = collections.Counter(t for r in h['rows'] for t in r['tags'])
        for s, k in sectors.most_common():
            if ('sector', s) in HUB_BY:
                links.append((f'{SECTOR_SHORT.get(s, s)} fintechs in Europe', hub_url(HUB_BY[('sector', s)])))
    if h['kind'] == 'sector':
        for c, k in collections.Counter(r['country'] for r in h['rows']).most_common(8):
            if ('country', c) in HUB_BY:
                links.append((f'Fintech companies in {c}', hub_url(HUB_BY[('country', c)])))
    if h['key'] != 'Nordics': links.append(('Nordic fintech companies', '/fintech-companies/nordics.html'))
    if h['key'] != 'Stockholm': links.append(('Fintech companies in Stockholm', '/fintech-companies/stockholm.html'))
    links.append(('Search all fintechs', '/trending.html'))
    return links[:10]

def build_hub(h):
    title, h1 = hub_title(h)
    lead, med, sectors, cities, countries = hub_lead(h)
    rs = h['rows']; n = len(rs)
    path = hub_url(h)
    desc = (lead[:150].rsplit(' ', 1)[0] + '…') if len(lead) > 155 else lead
    trail = [('Alexandra Studio', '/'), ('Fintech database', '/trending.html'), (h1, path)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": SITE + path, "url": SITE + path, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"}, "inLanguage": "en",
         "dateModified": "2026-11-10",
         "isAccessibleForFree": False,
         "hasPart": {"@type": "WebPageElement", "isAccessibleForFree": False, "cssSelector": ".db-locked"},
         "citation": {"@type": "Dataset", "name": "EU FinTech Map", "url": SOURCE_URL},
         "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [
             {"@type": "ListItem", "position": i + 1,
              "item": {"@type": "Organization", "name": r['name'], **({"url": r['url']} if r['url'] else {}),
                       **({"foundingDate": str(r['year'])} if r['year'] else {}),
                       "address": {"@type": "PostalAddress", "addressCountry": r['country'],
                                   **({"addressLocality": r['city']} if r['city'] else {})}}}
             for i, r in enumerate(rs[:5])]}},
        crumbs_ld(trail)]}

    stat3 = (f'<div class="db-stat"><b>{fmt(n)}</b><span>fintechs listed</span></div>')
    if h['kind'] == 'sector':
        c1, k1 = top(countries, 1)[0]
        stat3 += f'<div class="db-stat"><b>{k1}</b><span>in {E(c1)}, the most of any country</span></div>'
    elif h['kind'] == 'region':
        c1, k1 = top(countries, 1)[0]
        stat3 += f'<div class="db-stat"><b>{k1}</b><span>in {E(c1)}</span></div>'
    elif top(cities, 1):
        c1, k1 = top(cities, 1)[0]
        stat3 += f'<div class="db-stat"><b>{k1}</b><span>in {E(c1)}</span></div>'
    if med:
        stat3 += f'<div class="db-stat"><b>{med}</b><span>median founding year</span></div>'

    chips = ''
    if sectors and h['kind'] != 'sector':
        chips = '<ul class="db-chips">' + ''.join(
            f'<li><a href="{hub_url(HUB_BY[("sector", s)])}">{E(SECTOR_SHORT.get(s, s))} <span>{k}</span></a></li>'
            if ('sector', s) in HUB_BY else f'<li><span class="db-chip-static">{E(SECTOR_SHORT.get(s, s))} <span>{k}</span></span></li>'
            for s, k in sectors.most_common()) + '</ul>'
    elif h['kind'] == 'sector':
        chips = '<ul class="db-chips">' + ''.join(
            f'<li><a href="{hub_url(HUB_BY[("country", c)])}">{E(c)} <span>{k}</span></a></li>'
            for c, k in countries.most_common() if ('country', c) in HUB_BY) + '</ul>'

    rows_html = '\n'.join('          ' + row_html(r, blur=(0 if i < 5 else min(i - 4, 5) if i < 11 else 6)) for i, r in enumerate(rs))
    noun = {'country': f"{DEMONYM.get(h['key'], h['key'])} fintechs", 'region': 'Nordic fintechs',
            'city': 'Stockholm fintechs'}.get(h['kind'], f"{SECTOR_SHORT.get(h['key'], h['key']).lower()} fintechs")
    gate = (f'''<div class="db-gate"><p><b>{fmt(n - 5)}</b> more {E(noun)} in the database.</p>
            <a class="btn btn-sky" href="{ICP_URL}">Download a list of 100 of your ICP</a></div>''' if n > 5 else '')
    rel = ''.join(f'<li><a href="{u}">{E(t)}</a></li>' for t, u in related_links(h))
    nordic_cta = ''
    if h['key'] in ('Sweden', 'Nordics', 'Stockholm', 'Denmark', 'Finland'):
        nordic_cta = ('<a class="btn btn-line" href="/insider-events.html">Meet them at Insider Events</a>')

    page = head(f'{title} | Alexandra Studio', desc, path, ld, css=('/events.css', '/database.css')) + header('/trending.html') + f'''
<main id="main" class="db-hub">
  <div class="wrap">
    {crumbs(trail[1:])}
    <h1 class="ep-title">{E(h1)}</h1>
    <p class="ep-dek">{E(lead)}</p>
    <div class="db-stats">{stat3}</div>
    {chips}

    <div class="db-cta">
      <p><b>Selling to these companies?</b> Get a list of 100 that match your ideal customer profile, with the people to talk to.</p>
      <div class="db-cta-actions">
        <a class="btn btn-sky" href="{ICP_URL}">Download a list of 100 of your ICP</a>
        {nordic_cta}
      </div>
    </div>

    <section class="db-list" aria-labelledby="list-title">
      <div class="db-list-head">
        <h2 class="sec-title" id="list-title">{fmt(n)} companies in the database</h2>
        <a class="db-list-link" href="/trending.html">Search and filter the database</a>
      </div>
      {trend_legend(sum(1 for r in rs if r['pts']))}
      <div class="db-table-wrap">
        <table class="db-table">
          {table_head()}
          <tbody>
{rows_html}
          </tbody>
        </table>
        {gate}
      </div>
      <p class="db-source">Source: <a href="{SOURCE_URL}" target="_blank" rel="noopener">{E(SOURCE_NAME)}</a>, plus companies from our own network, compiled and cleaned by Alexandra Studio. Updated {UPDATED}. Is your company missing or listed wrong? <a href="{ADD_FORM}">Add your company</a> or <a href="{REMOVE_FORM}">remove it</a>.</p>
    </section>

    <section class="db-related" aria-labelledby="rel-title">
      <h2 class="sec-title" id="rel-title">Keep exploring</h2>
      <ul class="db-chips">{rel}</ul>
    </section>
  </div>
</main>
''' + tail(('/database.js',))
    out = ROOT / path.lstrip('/')
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')

# --------------------------------------------------------------------------
# Trending page
# --------------------------------------------------------------------------
def build_json():
    countries = COUNTRIES
    data = {"updated": UPDATED, "total": TOTAL, "sectors": SECTORS, "countries": countries,
            "nordics": NORDICS,
            "hubs": {**{h['key']: hub_url(h) for h in HUBS if h['kind'] in ('country', 'region')}},
            "top": TOP_PTS,
            # [name, sectorBitmask, countryIndex, city, year, url, fintechAwardPoints, profilePath]
            # companies with Fintech Award Points first
            "rows": [[r['name'], sum(1 << SECTORS.index(t) for t in r['tags']), countries.index(r['country']),
                      r['city'], r['year'], r['url'], r['pts'], r['purl']] for r in ROWS]}
    (ROOT / 'data').mkdir(exist_ok=True)
    (ROOT / 'data' / 'fintechs.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

def build_trending():
    path = '/trending.html'
    title = f'Fintech Database: {fmt(TOTAL)} European Fintech Companies | Alexandra Studio'
    desc = (f'Search {fmt(TOTAL)} European fintech companies by sector and country: payments, banking, lending, wealth, '
            f'insurtech, crypto and regtech, with {fmt(len(HUB_BY[("region","Nordics")]["rows"]))} in the Nordics.')
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": SITE + path, "url": SITE + path, "name": "Fintech database", "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"}, "inLanguage": "en",
         "isAccessibleForFree": False,
         "hasPart": [{"@type": "WebPageElement", "isAccessibleForFree": False, "cssSelector": ".db-locked"}]
                    + [{"@type": "WebPage", "name": hub_title(h)[1], "url": SITE + hub_url(h)} for h in HUBS]},
        {"@type": "Dataset", "name": "Alexandra Studio fintech database", "description": desc, "url": SITE + path,
         "creator": {"@id": f"{SITE}/#organization"}, "isBasedOn": SOURCE_URL, "dateModified": "2026-11-10",
         "spatialCoverage": "Europe", "variableMeasured": ["Company", "Sector", "Country", "City", "Founding year", "Fintech Award Points"]},
        crumbs_ld([('Alexandra Studio', '/'), ('Fintech database', path)])]}

    first = ROWS[:10]
    rows_html = '\n'.join('            ' + row_html(r, blur=(i - 4 if i >= 5 else 0)) for i, r in enumerate(first))
    sec_btns = '\n'.join(
        f'            <button type="button" class="db-chip" data-sector="{i}" aria-pressed="false">{E(SECTOR_SHORT.get(s, s))}</button>'
        for i, s in enumerate(SECTORS[:9]))
    opts = '\n'.join(f'              <option value="{E(c)}">{E(c)}</option>' for c in COUNTRIES)
    posts = '\n'.join(f'''          <li>
            <a class="post" href="{p["url"]}" target="_blank" rel="noopener">
              <img src="https://substackcdn.com/image/fetch/{p["img"]}" alt="" width="240" height="150" loading="lazy" decoding="async" />
              <div>
                <p class="post-meta">Stockholm Growth &amp; Fintech · <time datetime="{p["date"]}">{p["label"]}</time></p>
                <h3>{E(p["title"])}</h3>
                <p class="post-dek">{E(p["dek"])}</p>
              </div>
            </a>
          </li>''' for p in POSTS)

    def chip_links(hubs):
        return ''.join(f'<li><a href="{hub_url(h)}">{E(h["key"] if h["kind"] != "sector" else SECTOR_SHORT.get(h["key"], h["key"]))} <span>{fmt(len(h["rows"]))}</span></a></li>' for h in hubs)
    country_hubs = [h for h in HUBS if h['kind'] == 'country']
    sector_hubs = [h for h in HUBS if h['kind'] == 'sector']
    nordic = HUB_BY[('region', 'Nordics')]; sthlm = HUB_BY[('city', 'Stockholm')]

    page = head(title, desc, path, ld, css=('/database.css',), preconnect=('https://substackcdn.com',)) + header('/trending.html') + f'''
<main id="main" class="db-page">

  <section class="db-hero" aria-labelledby="db-title">
    <div class="wrap">
      <h1 class="hero-title" id="db-title">Trending</h1>
    </div>
  </section>

  <section class="db-main" aria-label="Fintech database">
    <div class="wrap db-grid">
      <div class="db-left">
        <p class="db-intro">A searchable database of <b>{fmt(TOTAL)} European fintech companies</b> across {len(COUNTRIES)} countries: payments, banking, lending, wealth, insurtech, crypto and regtech, with {fmt(len(nordic["rows"]))} in the Nordics and {fmt(len(sthlm["rows"]))} in Stockholm alone. Filter by sector and country, or search by name.</p>

        <div class="db-filters" role="search">
          <label class="db-search"><span class="sr-only">Search fintech companies</span>
            <input type="search" id="dbSearch" placeholder="Search {fmt(TOTAL)} fintechs" autocomplete="off" />
          </label>
          <label class="db-select"><span class="sr-only">Country</span>
            <select id="dbCountry">
              <option value="">All of Europe</option>
              <option value="Nordics">Nordics</option>
{opts}
            </select>
          </label>
          <div class="db-chiprow" role="group" aria-label="Filter by sector">
            <button type="button" class="db-chip" data-sector="" aria-pressed="true">All sectors</button>
{sec_btns}
          </div>
        </div>

        <div class="db-board" aria-live="polite">
          <p class="db-count" id="dbCount">Showing 10 of {fmt(TOTAL)} fintechs, {'highest Fintech Award Points first' if N_TRENDING else 'newest first'}</p>
          {trend_legend()}
          <div class="db-table-wrap">
            <table class="db-table db-gated">
              {table_head()}
              <tbody id="dbRows">
{rows_html}
              </tbody>
            </table>
            <div class="db-gate" id="dbGate">
              <p><b id="dbMore">{fmt(TOTAL - 10)}</b> more fintechs in the database.</p>
              <a class="btn btn-sky" href="{ICP_URL}">Download a list of 100 of your ICP</a>
            </div>
          </div>
          <p class="db-source">Source: <a href="{SOURCE_URL}" target="_blank" rel="noopener">{E(SOURCE_NAME)}</a>, plus companies from our own network, compiled and cleaned by Alexandra Studio. Updated {UPDATED}.</p>
        </div>
      </div>

      <aside class="db-right" aria-label="Database size">
        <div class="db-box odo-scope"><p class="db-box-num"><span class="sr-only">{fmt(TOTAL)}</span><span class="odo" data-to="{TOTAL}" aria-hidden="true">{TOTAL}</span></p></div>
        <p class="db-box-label">Fintechs in our database.</p>
        <ul class="db-actions">
          <li><a class="btn btn-sky" href="{ADD_FORM}">Add your Company</a></li>
          <li><a class="btn btn-sky" href="{REMOVE_FORM}">Remove your Company</a></li>
        </ul>
      </aside>
    </div>
  </section>

  <section class="db-lower" aria-label="Newsletter and work with us">
    <div class="wrap db-lower-grid">
      <div>
        <h2 class="sec-title">Recently Hosted on our Podcast</h2>
        <ul class="posts db-posts">
{posts}
        </ul>
      </div>
      <div class="db-lower-right">
        <div class="db-sub">
          <div class="db-box db-box-wide odo-scope"><p class="db-box-num"><span class="sr-only">+{fmt(SUBSCRIBERS)}</span><span aria-hidden="true">+</span><span class="odo" data-to="{SUBSCRIBERS}" aria-hidden="true">{SUBSCRIBERS}</span></p></div>
          <p class="db-sub-label">Subscribers in Nordic Banks &amp; Fintechs.</p>
        </div>
        <a class="db-apply" href="{CONTACT_URL}" target="_blank" rel="noopener"><span>Apply to work with us.</span></a>
      </div>
    </div>
  </section>

  <section class="db-browse" aria-labelledby="browse-title">
    <div class="wrap">
      <h2 class="sec-title" id="browse-title">Browse the database</h2>
      <div class="db-browse-grid">
        <div>
          <h3>Nordics</h3>
          <ul class="db-chips">{chip_links([nordic, sthlm] + [HUB_BY[("country", c)] for c in NORDICS if ("country", c) in HUB_BY])}</ul>
          <h3>By sector</h3>
          <ul class="db-chips">{chip_links(sector_hubs)}</ul>
        </div>
        <div>
          <h3>By country</h3>
          <ul class="db-chips">{chip_links(country_hubs)}</ul>
        </div>
      </div>
    </div>
  </section>

</main>
''' + tail(('/database.js',))
    (ROOT / 'trending.html').write_text(page, encoding='utf-8')

# --------------------------------------------------------------------------
# Company profiles: one page per researched company
# --------------------------------------------------------------------------
PROFILE_CSS = ('/events.css', '/database.css', '/guides.css')
DATE_ISO = '2026-11-10'
DATE_LABEL = '10 November 2026'

def sector_links(r):
    out = []
    for t in r['tags']:
        h = HUB_BY.get(('sector', t))
        lab = E(SECTOR_SHORT.get(t, t))
        out.append(f'<a href="{hub_url(h)}">{lab}</a>' if h else lab)
    return ', '.join(out) or 'Other fintech'

def points_line(r):
    return f'+{fmt(r["pts"])}, #{RANK[id(r)]} of {fmt(N_TRENDING)}'

def similar(r, k=6):
    pool = [x for x in PROFILED if x is not r and set(x['tags']) & set(r['tags'])]
    pool.sort(key=lambda x: (x['country'] != r['country'], -x['pts'], x['name'].lower()))
    return pool[:k]

def card_li(x, show_pts=True):
    p = x['profile']
    pts = f'<span class="db-pts">+{fmt(x["pts"])}</span>' if (show_pts and x['pts']) else ''
    return (f'<li><h3><a href="{x["purl"]}">{E(x["name"])}</a>{pts}</h3>'
            f'<span class="gd-card-meta">{E(sector_label(x))} · {E(place(x))}</span>'
            f'<p>{E(p["one_liner"])}</p></li>')

def org_ld(r, at=None):
    p = r['profile'] or {}
    d = {"@type": "Organization", "name": r['name']}
    if at: d["@id"] = at
    if r['url']: d["url"] = r['url']
    if p.get('one_liner'): d["description"] = p['one_liner']
    d["address"] = {"@type": "PostalAddress", "addressCountry": r['country'], **({"addressLocality": r['city']} if r['city'] else {})}
    if r['year']: d["foundingDate"] = str(r['year'])
    kws = split_list(p.get('keywords', ''))
    if kws: d["knowsAbout"] = kws[:10]
    return d

def build_profile(r):
    p = r['profile']
    name = r['name']
    path = r['purl']
    first = SECTOR_SHORT.get(r['tags'][0], r['tags'][0]) if r['tags'] else 'Fintech'
    title = f'{name}: {first} company in {r["country"]} | Fintech Company Profile'
    desc = p['one_liner'] if len(p['one_liner']) <= 158 else p['one_liner'][:154].rsplit(' ', 1)[0] + '…'
    hub = HUB_BY.get(('country', r['country']))
    trail = [('Alexandra Studio', '/'), ('Fintech database', '/trending.html')]
    trail += [(hub_title(hub)[1], hub_url(hub))] if hub else []
    trail += [('Company profiles', '/fintech-company/'), (name, path)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": SITE + path, "url": SITE + path, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"},
         "about": {"@id": SITE + path + '#org'}, "dateModified": DATE_ISO, "inLanguage": "en"},
        org_ld(r, SITE + path + '#org'),
        crumbs_ld(trail)]}

    facts = []
    if r['url']:
        facts.append(('Website', f'<a href="{E(r["url"])}" target="_blank" rel="nofollow noopener">{E(r["host"])}</a>'))
    facts.append(('Headquarters', E(place(r))))
    if r['year']:
        facts.append(('Founded', str(r['year'])))
    facts.append(('Sector', sector_links(r)))
    if r['pts']:
        facts.append(('Fintech Award Points', f'<a href="{AWARDS_URL}">{points_line(r)}</a>'))
    facts_html = '\n'.join(f'            <div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in facts)

    def ul(items, cls=''):
        c = f' class="{cls}"' if cls else ''
        return f'<ul{c}>' + ''.join(f'<li>{E(x)}</li>' for x in items) + '</ul>'
    offering, serves, kws = split_list(p['offering']), split_list(p['serves']), split_list(p['keywords'])
    body = [f'<h2>About {E(name)}</h2>', f'<p>{E(p["summary"])}</p>']
    if offering:
        body += [f'<h2>What {E(name)} offers</h2>', ul(offering)]
    if serves:
        body += [f'<h2>Who {E(name)} serves</h2>', ul(serves)]
    if kws:
        body += ['<h2>Topics</h2>', ul(kws, 'pf-tags')]
    sims = similar(r)
    if sims:
        body += ['<h2>Similar fintech companies</h2>', '<ul class="gd-cards">' + ''.join(card_li(x) for x in sims) + '</ul>']
    rel = []
    if hub: rel.append((hub_title(hub)[1], hub_url(hub)))
    for t in r['tags']:
        h = HUB_BY.get(('sector', t))
        if h: rel.append((f'{SECTOR_SHORT.get(t, t)} fintechs in Europe', hub_url(h)))
    if r['country'] in NORDICS: rel.append(('Nordic fintech companies', '/fintech-companies/nordics.html'))
    rel += [('Fintech Awards 2026', AWARDS_URL), ('All company profiles', '/fintech-company/')]
    body += ['<h2>More in the database</h2>',
             '<ul class="db-chips">' + ''.join(f'<li><a href="{u}">{E(t)}</a></li>' for t, u in rel) + '</ul>']

    if r['pts']:
        top = '<span class="db-top">#1 Fintech Award</span>' if r['pts'] == TOP_PTS else ''
        card = (f'<div class="pf-points"><b>+{fmt(r["pts"])}</b>'
                f'<span>Fintech Award Points · #{RANK[id(r)]} of {fmt(N_TRENDING)} scored companies</span>{top}</div>'
                f'<p class="pf-aside-copy">Points go to the companies most active with Nordic fintech buyers, partners and '
                f'Stockholm Growth &amp; Fintech readers right now. <a href="{AWARDS_URL}#how">How points work</a>.</p>')
    else:
        card = (f'<p class="pf-aside-copy">{E(name)} has no Fintech Award Points yet. Points go to the companies most '
                f'active with Nordic fintech buyers, partners and our readers. <a href="{AWARDS_URL}#earn">How to earn them</a>.</p>')
    kicker = f'{E(sector_label(r))} · {E(place(r))}'
    page = head(title, desc, path, ld, css=PROFILE_CSS) + header('/trending.html') + f"""
<main id="main" class="ep pf">
  <div class="wrap">
    {crumbs(trail[1:])}
    <div class="ep-grid">
      <article class="ep-article">
        <p class="ep-kicker"><span class="dot"></span>{kicker}</p>
        <h1 class="ep-title">{E(name)}</h1>
        <p class="ep-dek">{E(p['one_liner'])}</p>
        <dl class="ep-facts">
{facts_html}
        </dl>
        <div class="ep-body">
          {''.join(body)}
        </div>
        <p class="db-source">Profile researched by Alexandra Studio from public information about {E(name)}, updated {DATE_LABEL}. Something wrong or missing? <a href="{ADD_FORM}">Update your company</a> or <a href="{REMOVE_FORM}">remove it</a>.</p>
      </article>
      <aside class="ep-aside" aria-label="Fintech Award Points">
        <div class="ep-card">
          {card}
          <a class="btn btn-sky" href="{AWARDS_URL}">See the Fintech Awards 2026</a>
          <a class="btn btn-line" href="/insider-events.html">Meet Nordic fintechs at Insider Events</a>
          <p class="ep-note"><a href="/trending.html">Search {fmt(TOTAL)} fintechs in the database</a></p>
        </div>
      </aside>
    </div>
  </div>
</main>
""" + tail()
    out = ROOT / path.lstrip('/')
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')

def build_profile_index():
    path = '/fintech-company/'
    n = len(PROFILED)
    title = f'Fintech Company Profiles: {n} Nordic and European Fintechs, Banks and Payments Companies'
    desc = (f'{n} company profiles researched by Alexandra Studio: what each fintech does, what it offers, who it serves '
            'and its Fintech Award Points.')
    trail = [('Alexandra Studio', '/'), ('Fintech database', '/trending.html'), ('Company profiles', path)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": SITE + path, "url": SITE + path, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"},
         "dateModified": DATE_ISO, "inLanguage": "en", "numberOfItems": n},
        crumbs_ld(trail)]}
    groups = collections.defaultdict(list)
    for r in sorted(PROFILED, key=lambda r: r['name'].lower()):
        k = r['name'][0].upper()
        groups[k if k.isalpha() else '0–9'].append(r)
    blocks = ''.join(
        f'<section><h2>{E(k)}</h2><ul>' + ''.join(
            f'<li><a href="{r["purl"]}">{E(r["name"])}</a>{E(sector_label(r))} · {E(place(r))}</li>' for r in rs)
        + '</ul></section>' for k, rs in sorted(groups.items(), key=lambda t: (t[0] == '0–9', t[0])))
    page = head(title, desc, path, ld, css=PROFILE_CSS) + header('/trending.html') + f"""
<main id="main" class="ep db-hub">
  <div class="wrap">
    {crumbs(trail[1:])}
    <h1 class="ep-title">Fintech company profiles</h1>
    <p class="ep-dek">{n} fintechs, banks and payments companies, researched by the Alexandra Studio team: what each one does, what it offers, who it sells to, and its <a href="{AWARDS_URL}">Fintech Award Points</a>. The full list of {fmt(TOTAL)} European fintechs is in the <a href="/trending.html">fintech database</a>.</p>
    <div class="pf-index">{blocks}</div>
  </div>
</main>
""" + tail(('/database.js',))
    out = ROOT / 'fintech-company' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')

# --------------------------------------------------------------------------
# Fintech Awards 2026: the Fintech Award Points leaderboard
# --------------------------------------------------------------------------
AWARD_CATS = [('Banking', 'Banking'), ('Payments', 'Payments'), ('Regtech', 'Regtech, KYC and fraud'),
              ('Lending', 'Lending and credit'), ('Wealth Management', 'Wealth and investing'),
              ('Financial Management', 'Finance software'), ('Crypto and DeFi', 'Crypto and digital assets'),
              ('Insurance', 'Insurtech')]
OTHER_NORDICS = {'Denmark', 'Finland', 'Norway', 'Iceland'}

def name_link(r):
    return f'<a href="{r["purl"]}">{E(r["name"])}</a>' if r['purl'] else E(r['name'])

def award_categories():
    cats = []
    for t, label in AWARD_CATS:
        rs = [r for r in RANKED if t in r['tags']]
        if rs: cats.append((label, rs))
    regions = [('Stockholm fintech', [r for r in RANKED if outside_stockholm(r) is False]),
               ('Nordics outside Sweden', [r for r in RANKED if r['country'] in OTHER_NORDICS]),
               ('Outside the Nordics', [r for r in RANKED if r['country'] not in OTHER_NORDICS | {'Sweden'}]),
               ('API and hackathon partner', [r for r in RANKED if r['profile'] and r['profile']['vertical'] == 'Hackathons'])]
    return cats + [(a, b) for a, b in regions if b]

def build_awards():
    path = AWARDS_URL
    n = N_TRENDING
    countries = collections.Counter(r['country'] for r in RANKED)
    nordic = sum(1 for r in RANKED if r['country'] in NORDICS + ['Iceland'])
    top25 = RANKED[:25]
    abroad25 = sum(1 for r in top25 if r['country'] != 'Sweden')
    sec25 = collections.Counter(t for r in top25 for t in r['tags'])
    lead_sec, lead_k = sec25.most_common(1)[0] if sec25 else ('', 0)
    banks10 = [r for r in RANKED[:10] if 'Banking' in r['tags']]
    title = 'Fintech Awards 2026: The Fintech Award Points Leaderboard | Alexandra Studio'
    desc = (f'Fintech Awards 2026: the {n} Nordic and European fintechs, banks and payments companies most active with '
            f'fintech buyers, partners and readers, ranked by Fintech Award Points. {RANKED[0]["name"]} is #1.')
    trail = [('Alexandra Studio', '/'), ('Fintech database', '/trending.html'), ('Fintech Awards 2026', path)]

    faqs = [
        ('What are the Fintech Awards?',
         f'The Fintech Awards are Alexandra Studio\'s ranking of the fintechs, banks and payments companies that are most active in the Nordic fintech community right now. Every company is scored in Fintech Award Points. The {DATE_LABEL} table covers {n} companies in {len(countries)} countries, and {RANKED[0]["name"]} is #1 with {fmt(RANKED[0]["pts"])} points.'),
        ('How are Fintech Award Points calculated?',
         'Every scored company starts at 105 points. Points are added for recent two-way conversations with our team, for replying again and again, for each person at the company who reads Stockholm Growth & Fintech (more for close readers), and for reaching the Stockholm community from outside Stockholm. We publish each company\'s total, never the individual signals or the people behind them.'),
        ('Can a company buy Fintech Award Points?',
         'No. Points cannot be bought, sponsored or traded for coverage, and working with Alexandra Studio earns no points. They measure engagement, not company size, funding or product quality.'),
        ('How can my company earn Fintech Award Points?',
         'Take part. Subscribe your team to Stockholm Growth & Fintech, come to an Insider Event, speak on a panel, co-host a room, or simply reply when we write to you. Companies outside Stockholm get extra points for reaching the Stockholm community.'),
        ('How often is the leaderboard updated?',
         f'We recalculate the points whenever we refresh our data. This table is a snapshot from {DATE_LABEL}; recent activity counts for more, so the order changes from month to month.'),
        ('Is this a fintech marketing award?',
         'It isn\'t a jury prize for one campaign. It rewards what good fintech marketing produces: buyers, partners and readers who engage. For campaigns and channels that earn that attention, see our guide to fintech marketing trends and strategy.'),
        ('My company is listed wrong. How do I change it?',
         'Use the add or remove forms linked under the leaderboard, and we will correct the profile or take it down.'),
    ]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": SITE + path, "url": SITE + path, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"},
         "dateModified": DATE_ISO, "inLanguage": "en",
         "mainEntity": {"@type": "ItemList", "name": "Fintech Awards 2026: Fintech Award Points", "numberOfItems": n,
                        "itemListOrder": "https://schema.org/ItemListOrderDescending",
                        "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                             "url": SITE + r['purl'] if r['purl'] else r['url'] or SITE + path,
                                             "name": r['name']} for i, r in enumerate(RANKED[:25])]}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
        crumbs_ld(trail)]}

    def blurb(r):
        return E(r['profile']['one_liner']) if r['profile'] else E(f"{sector_label(r)} company in {place(r)}.")
    podium = ''.join(
        f'<li><span class="aw-rank">{i + 1}</span><h3>{name_link(r)}</h3>'
        f'<span class="aw-sub"><span class="db-pts">+{fmt(r["pts"])}</span> · {E(place(r))}</span><p>{blurb(r)}</p></li>'
        for i, r in enumerate(RANKED[:3]))
    board_rows = ''.join(
        f'<tr><td class="num">{i + 4}</td><td>{name_link(r)}</td><td class="num"><span class="db-pts">+{fmt(r["pts"])}</span></td>'
        f'<td>{E(sector_label(r))}</td><td>{E(place(r))}</td></tr>' for i, r in enumerate(RANKED[3:30]))
    cats = ''.join(
        f'<li><span class="aw-cat">{E(label)}</span><span class="aw-win">{name_link(rs[0])} <span class="db-pts">+{fmt(rs[0]["pts"])}</span></span>'
        + (f'<span class="aw-runner">Runner-up: {name_link(rs[1])}, +{fmt(rs[1]["pts"])}</span>' if len(rs) > 1 else '') + '</li>'
        for label, rs in award_categories())
    faq_html = ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in faqs)
    bank_names = join_list([name_link(r) for r in banks10]) if banks10 else ''
    insight = (f'<p>{fmt(abroad25)} of the top 25 are based outside Sweden, and {SECTOR_SHORT.get(lead_sec, lead_sec).lower()} is the most common sector among them ({lead_k} of 25). '
               + (f'Banks are not waiting to be sold to: {bank_names} {"is" if len(banks10) == 1 else "are"} in the top 10. ' if banks10 else '')
               + 'The companies at the top have one thing in common: they show up. They answer, they read, they bring colleagues, and they take part in rooms they did not organise.</p>')

    page = head(title, desc, path, ld, css=PROFILE_CSS) + header('/trending.html') + f"""
<main id="main" class="ep gd">
  <div class="wrap">
    {crumbs(trail[1:])}
    <div class="ep-grid">
      <article class="ep-article">
        <p class="ep-kicker"><span class="dot"></span>Updated {DATE_LABEL} · {fmt(n)} companies scored</p>
        <h1 class="ep-title">Fintech Awards 2026</h1>
        <p class="ep-dek">The Fintech Award Points leaderboard: the Nordic and European fintechs, banks and payments companies most active with fintech buyers, partners and the readers of Stockholm Growth &amp; Fintech right now.</p>
        <nav class="gd-toc" aria-label="On this page"><a href="#winners">Top 3</a><a href="#leaderboard">Leaderboard</a><a href="#categories">Category winners</a><a href="#how">How points work</a><a href="#earn">Earn points</a><a href="#faq">FAQ</a></nav>
        <div class="gd-stats">
          <div class="gd-stat"><b>{fmt(n)}</b><span>companies with Fintech Award Points</span></div>
          <div class="gd-stat"><b>{len(countries)}</b><span>countries</span></div>
          <div class="gd-stat"><b>+{fmt(RANKED[0]['pts'])}</b><span>the top score, {E(RANKED[0]['name'])}</span></div>
        </div>
        <div class="ep-body">
          <h2 id="winners">The top 3</h2>
          <ol class="aw-podium">{podium}</ol>
          <h2 id="leaderboard">Leaderboard: places 4 to 30</h2>
          <div class="gd-scroll"><table class="gd-table"><thead><tr><th scope="col">#</th><th scope="col">Company</th><th scope="col">Points</th><th scope="col">Sector</th><th scope="col">Location</th></tr></thead><tbody>{board_rows}</tbody></table></div>
          <p>All {fmt(n)} companies with points are in the <a href="/trending.html">fintech database</a>, highest first. Every name links to a <a href="/fintech-company/">company profile</a>.</p>
          <h2 id="categories">Category winners</h2>
          <ul class="aw-cats">{cats}</ul>
          <h2>Fintech marketing awards, measured by engagement</h2>
          <p>Most fintech awards are judged on a submission: one campaign, one product launch, one good year. The Fintech Awards look at something harder to fake: whether buyers, partners and readers actually engage with a company, month after month. {fmt(nordic)} of the {fmt(n)} scored companies are Nordic; the rest reach in from {fmt(len(countries) - len([c for c in countries if c in NORDICS + ['Iceland']]))} other countries.</p>
          {insight}
          <p>For what drives that kind of attention, see <a href="/fintech-marketing-trends.html">fintech marketing trends and strategy for 2027</a>.</p>
          <h2 id="how">How Fintech Award Points work</h2>
          <ul>
            <li><b>Everyone starts at 105.</b> A company gets a score once it is active with us or our readers.</li>
            <li><b>Conversations count.</b> Recent two-way contact with our team adds points, and repeated replies add more.</li>
            <li><b>Readers count.</b> Every person at the company who reads Stockholm Growth &amp; Fintech adds points, and close readers add the most.</li>
            <li><b>Reach counts.</b> Companies based outside Stockholm get extra points for reaching the Stockholm community.</li>
            <li><b>Nothing is for sale.</b> Points can't be bought, and clients get none for being clients. We publish totals only, never the people or signals behind them.</li>
          </ul>
          <p>The table is a snapshot from {DATE_LABEL}. Recent activity counts for more, so the order moves as the community does.</p>
          <h2 id="earn">How to earn Fintech Award Points</h2>
          <ul>
            <li><b>Read.</b> Subscribe your team to <a href="https://stockholmgrowthfintech.substack.com/" target="_blank" rel="noopener">Stockholm Growth &amp; Fintech</a>.</li>
            <li><b>Show up.</b> Request a seat at an <a href="/insider-events.html">Insider Event</a>: executive breakfasts, dinners, build days.</li>
            <li><b>Take the stage.</b> Speak on a panel, co-host a room, or bring an API to a <a href="/fintech-hackathon-stockholm.html">fintech hackathon</a>.</li>
            <li><b>Reply.</b> When we write to you, write back.</li>
          </ul>
          <section class="ev-faq" id="faq" aria-labelledby="faq-title">
            <h2 id="faq-title">Questions about the Fintech Awards</h2>
            <div class="ev-faq-list">{faq_html}</div>
          </section>
        </div>
        <p class="db-source">Fintech Award Points from Alexandra Studio's own data, {DATE_LABEL}. Company details from the <a href="{SOURCE_URL}" target="_blank" rel="noopener">EU FinTech Map</a> and our own research. Listed wrong? <a href="{ADD_FORM}">Update your company</a> or <a href="{REMOVE_FORM}">remove it</a>.</p>
      </article>
      <aside class="ep-aside" aria-label="Fintech Awards">
        <div class="ep-card">
          <div class="pf-points"><b>+{fmt(RANKED[0]['pts'])}</b><span>#1 in the Fintech Awards 2026: {name_link(RANKED[0])}</span><span class="db-top">#1 Fintech Award</span></div>
          <a class="btn btn-sky" href="/trending.html">See all {fmt(n)} in the database</a>
          <a class="btn btn-line" href="/insider-events.html">Earn points at Insider Events</a>
          <p class="ep-note"><a href="/fintech-company/">Browse {fmt(len(PROFILED))} company profiles</a></p>
        </div>
      </aside>
    </div>
  </div>
</main>
""" + tail()
    (ROOT / 'fintech-awards.html').write_text(page, encoding='utf-8')

if __name__ == '__main__':
    build_json()
    build_trending()
    for h in HUBS:
        build_hub(h)
    for r in PROFILED:
        build_profile(r)
    build_profile_index()
    build_awards()
    print(f'{TOTAL} companies; trending.html, data/fintechs.json, {len(HUBS)} hub pages, '
          f'{len(PROFILED)} company profiles and the Fintech Awards page')
