#!/usr/bin/env python3
"""Builds the fintech database:

  trending.html                       the Trending page (filterable table, 10 rows, bottom 5 blurred)
  data/fintechs.json                  the data the table filters (no emails)
  fintech-companies/<slug>.html       one page per country, sector, the Nordics and Stockholm,
                                      each listing every company so search engines can index them

Run from the repo root:   python3 _tools/build_database.py
Source list: _tools/data/fintech-companies.csv (cleaned; emails removed).
"""
import csv, collections, json, re, statistics
from site_chrome import ROOT, SITE, E, head, header, tail

DATA = ROOT / '_tools' / 'data' / 'fintech-companies.csv'
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
           'Slovenia': 'Slovenian', 'Norway': 'Norwegian', 'Switzerland': 'Swiss'}
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
def load():
    rows = list(csv.DictReader(open(DATA, encoding='utf-8')))
    for r in rows:
        r['tags'] = [t for t in r['sectors'].split('|') if t] if r['sectors'] else []
        r['year'] = int(r['founded']) if r['founded'] else 0
        w = r['website'].strip()
        r['url'] = w if w.startswith('http') else ('https://' + w if w else '')
        h = r['url'].split('//', 1)[-1].split('/', 1)[0].lower() if r['url'] else ''
        r['host'] = h[4:] if h.startswith('www.') else h
        # the source sometimes puts a street address where the city should be
        c = re.sub(r'^\d[\d\s-]*', '', r['city']).strip()
        r['city'] = '' if (re.search(r'\d', c) or re.search(r'(str\.|straat|strasse|straße|street|road|calle|via |rue |avenue|ul\.)', c, re.I)) else c
    # default order: complete records first (sector + city + website), newest first, then A-Z
    rows.sort(key=lambda r: (-(bool(r['tags']) and bool(r['city']) and bool(r['url'])), -r['year'], r['name'].lower()))
    return rows

ROWS = load()
TOTAL = len(ROWS)
COUNTRIES = [c for c, _ in collections.Counter(r['country'] for r in ROWS).most_common()]

def fmt(n): return f'{n:,}'
def sector_label(r): return ', '.join(SECTOR_SHORT.get(t, t) for t in r['tags']) or 'Other fintech'
def place(r): return f"{r['city']}, {r['country']}" if r['city'] else r['country']

# --------------------------------------------------------------------------
# Shared bits
# --------------------------------------------------------------------------
def row_html(r, blur=0):
    hidden = f' class="is-blur b{blur}" aria-hidden="true"' if blur else ''
    name = E(r['name'])
    if r['url'] and not blur:
        name_html = f'<a href="{E(r["url"])}" target="_blank" rel="nofollow noopener">{name}</a>'
    else:
        name_html = name
    host = f'<span class="db-host">{E(r["host"])}</span>' if r['host'] else ''
    return (f'<tr{hidden}><td class="db-name"><span class="db-co">{name_html}</span>{host}</td>'
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
    if len(rs) >= 10:
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
         "citation": {"@type": "Dataset", "name": "EU FinTech Map", "url": SOURCE_URL},
         "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [
             {"@type": "ListItem", "position": i + 1,
              "item": {"@type": "Organization", "name": r['name'], **({"url": r['url']} if r['url'] else {}),
                       **({"foundingDate": str(r['year'])} if r['year'] else {}),
                       "address": {"@type": "PostalAddress", "addressCountry": r['country'],
                                   **({"addressLocality": r['city']} if r['city'] else {})}}}
             for i, r in enumerate(rs[:100])]}},
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

    rows_html = '\n'.join('          ' + row_html(r) for r in rs)
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
        <h2 class="sec-title" id="list-title">All {fmt(n)} companies</h2>
        <label class="db-search"><span class="sr-only">Filter this list</span>
          <input type="search" placeholder="Filter by name, city or sector" data-hub-filter autocomplete="off" />
        </label>
      </div>
      <div class="db-table-wrap">
        <table class="db-table">
          {table_head()}
          <tbody data-hub-rows>
{rows_html}
          </tbody>
        </table>
      </div>
      <p class="db-source">Source: <a href="{SOURCE_URL}" target="_blank" rel="noopener">{E(SOURCE_NAME)}</a>, compiled and cleaned by Alexandra Studio. Updated {UPDATED}. Is your company missing or listed wrong? <a href="{ADD_FORM}">Add your company</a> or <a href="{REMOVE_FORM}">remove it</a>.</p>
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
            # [name, sectorBitmask, countryIndex, city, year, url]
            "rows": [[r['name'], sum(1 << SECTORS.index(t) for t in r['tags']), countries.index(r['country']),
                      r['city'], r['year'], r['url']] for r in ROWS]}
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
         "hasPart": [{"@type": "WebPage", "name": hub_title(h)[1], "url": SITE + hub_url(h)} for h in HUBS]},
        {"@type": "Dataset", "name": "Alexandra Studio fintech database", "description": desc, "url": SITE + path,
         "creator": {"@id": f"{SITE}/#organization"}, "isBasedOn": SOURCE_URL, "dateModified": "2026-11-10",
         "spatialCoverage": "Europe", "variableMeasured": ["Company", "Sector", "Country", "City", "Founding year"]},
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
          <p class="db-count" id="dbCount">Showing 10 of {fmt(TOTAL)} fintechs, newest first</p>
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
          <p class="db-source">Source: <a href="{SOURCE_URL}" target="_blank" rel="noopener">{E(SOURCE_NAME)}</a>, compiled and cleaned by Alexandra Studio. Updated {UPDATED}.</p>
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

if __name__ == '__main__':
    build_json()
    build_trending()
    for h in HUBS:
        build_hub(h)
    print(f'{TOTAL} companies; trending.html, data/fintechs.json and {len(HUBS)} hub pages')
