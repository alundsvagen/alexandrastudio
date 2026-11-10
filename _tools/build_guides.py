#!/usr/bin/env python3
"""Builds the five keyword guides from the fintech database and our own data:

  fintech-marketing-trends.html     fintech marketing trends, strategy, campaigns, community
  fintech-marketing-agencies.html   best fintech marketing agencies, PR and communications, event agency, market entry services
  fintech-conferences-2027.html     fintech marketing conference 2027, Money20/20 Europe / Stockholm Fintech Week /
                                    Nordic Fintech Week side events, is a Money20/20 booth worth it?
  selling-to-nordic-banks.html      selling to Nordic banks, how to sell to banks, tier-1 banks, bank partnerships,
                                    go-to-market Nordics, fintech market entry Sweden, how to get leads in the Nordics
  fintech-hackathon-stockholm.html  fintech hackathon, bank hackathon, API hackathon Stockholm

Run after build_database.py:   cd _tools && python3 build_guides.py
"""
import collections, json, re
from site_chrome import ROOT, SITE, E, head, header, tail
from build_database import (ROWS, PROFILED, RANKED, RANK, N_TRENDING, TOTAL, AWARDS_URL, CONTACT_URL, PROFILE_CSS,
                            DATE_ISO, DATE_LABEL, fmt, place, sector_label, card_li, name_link, crumbs, crumbs_ld,
                            load_research, split_list)

NEWS = json.loads((ROOT / '_tools' / 'data' / 'newsletter-stats.json').read_text(encoding='utf-8'))
SUBSTACK = 'https://stockholmgrowthfintech.substack.com'
ALEXANDRA = {"@id": f"{SITE}/#alexandra"}

# --------------------------------------------------------------------------
# Numbers from the company research
# --------------------------------------------------------------------------
P = [r['profile'] for r in PROFILED]
N = len(P)

def share(rx, fields=('keywords', 'one_liner', 'summary', 'offering')):
    return sum(1 for p in P if re.search(rx, ' '.join(p[f] for f in fields).lower()))

def pct(k): return round(k * 100 / N)

AI = share(r'\bai\b|artificial intelligence|machine learning')
AGENTIC = share(r'agentic|ai agents?\b')
COMPLIANCE = share(r'compliance|\bkyc\b|\bkyb\b|\baml\b|fraud')
API = share(r'\bapis?\b')
OPEN_BANKING = share(r'open banking|open finance|psd2')
REALTIME = share(r'real-time|instant payment')
EMBEDDED = share(r'embedded')
SERVES = [('Banks and credit unions', r'\bbanks?\b|banking|credit union'),
          ('Merchants, retailers and e-commerce', r'merchant|retail|e-?commerce'),
          ('Other fintechs', r'fintech'),
          ('Enterprises and corporates', r'enterprise|corporat|large compan'),
          ('Wealth and asset managers', r'wealth|asset manag|investment firm|private bank'),
          ('Insurers', r'insur'),
          ('SMEs', r'\bsmes?\b|small and medium|small business'),
          ('Payment and e-money institutions', r'payment service provider|\bpsps?\b|e-money|payment institution|payment compan'),
          ('Consumers', r'consumer|individuals|households|private customer')]
SERVES_N = [(lab, share(rx, ('serves',))) for lab, rx in SERVES]
SERVES_N.sort(key=lambda t: -t[1])
BANKS_N = dict(SERVES_N)['Banks and credit unions']
KW = collections.Counter(k.lower() for p in P for k in split_list(p['keywords']))
SKIP_KW = {'fintech', 'nordics', 'sweden', 'denmark', 'saas', 'nordic', 'europe', 'b2b'}
TOP_KW = [(k, n) for k, n in KW.most_common(40) if k not in SKIP_KW][:15]
SECTOR_N = collections.Counter(t for r in PROFILED for t in r['tags'])
COUNTRY_N = collections.Counter(r['country'] for r in PROFILED)
def SECTOR_RANK(t):
    order = [s for s, _ in SECTOR_N.most_common()]
    return ['largest', 'second-largest', 'third-largest', 'fourth-largest'][order.index(t)] if order.index(t) < 4 else 'a large'

def by_domain(*doms):
    out = []
    for d in doms:
        for r in ROWS:
            if r['domain'] == d:
                out.append(r); break
    return out

NETWORK = {p['domain']: p for p in load_research() if p['vertical'] == 'Network'}

def net_card(dom, label):
    p = NETWORK.get(dom)
    if not p:
        return ''
    where = ', '.join(x for x in (p['city'], p['country']) if x)
    meta = label + (f' · {where}' if where else '')
    return (f'<li><h3><a href="https://{E(dom)}" target="_blank" rel="nofollow noopener">{E(p["name"])}</a></h3>'
            f'<span class="gd-card-meta">{E(meta)}</span><p>{E(p["one_liner"])}</p></li>')

def li_cards(rows):
    return '<ul class="gd-cards">' + ''.join(card_li(r) for r in rows) + '</ul>'

def table(head_cells, rows):
    th = ''.join(f'<th scope="col">{h}</th>' for h in head_cells)
    num = ' class="num"'
    isnum = lambda c: bool(re.fullmatch(r'[+#]?[\d,.]+%?', str(c)))
    trs = ''.join('<tr>' + ''.join(f'<td{num if i and isnum(c) else ""}>{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<div class="gd-scroll"><table class="gd-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

def stats(items):
    return '<div class="gd-stats">' + ''.join(f'<div class="gd-stat"><b>{a}</b><span>{b}</span></div>' for a, b in items) + '</div>'

# --------------------------------------------------------------------------
# Page template
# --------------------------------------------------------------------------
def render(g):
    path = '/' + g['slug'] + '.html'
    body = '\n'.join(g['sections'])
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    mins = max(4, round(words / 220))
    toc = ''.join(f'<a href="#{a}">{t}</a>' for a, t in g['toc'])
    faq = ''.join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>' for q, a in g['faqs'])
    rel = ''.join(f'<li><a href="{u}">{t}</a></li>' for t, u in g['related'])
    trail = [('Alexandra Studio', '/'), (g['crumb'], path)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": SITE + path + '#article', "headline": g['h1'], "description": g['desc'],
         "url": SITE + path, "mainEntityOfPage": SITE + path, "inLanguage": "en",
         "datePublished": DATE_ISO, "dateModified": DATE_ISO, "author": ALEXANDRA,
         "publisher": {"@id": f"{SITE}/#organization"}, "isPartOf": {"@id": f"{SITE}/#website"},
         "keywords": g['keywords'], "wordCount": words},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {
            "@type": "Answer", "text": re.sub(r'<[^>]+>', '', a)}} for q, a in g['faqs']]},
        crumbs_ld(trail)]}
    page = head(g['title'], g['desc'], path, ld, css=PROFILE_CSS) + header() + f"""
<main id="main" class="ep gd">
  <div class="wrap">
    {crumbs(trail)}
    <div class="ep-grid">
      <article class="ep-article">
        <p class="ep-kicker"><span class="dot"></span>{g['kicker']}</p>
        <h1 class="ep-title">{g['h1']}</h1>
        <p class="ep-dek">{g['dek']}</p>
        <p class="gd-meta">By <a href="/who-is-alexandra-grisanti.html">Alexandra Grisanti</a> · Updated {DATE_LABEL} · {mins} min read</p>
        <nav class="gd-toc" aria-label="On this page">{toc}<a href="#faq">FAQ</a></nav>
        {g.get('stats', '')}
        <div class="ep-body">
{body}
          <section class="ev-faq" id="faq" aria-labelledby="faq-title">
            <h2 id="faq-title">Questions people ask</h2>
            <div class="ev-faq-list">{faq}</div>
          </section>
          <h2>Keep reading</h2>
          <ul class="db-chips">{rel}</ul>
        </div>
      </article>
      <aside class="ep-aside" aria-label="Work with Alexandra Studio">
        <div class="ep-card">
          <p class="pf-aside-copy"><b>{g['cta_head']}</b><br>{g['cta_copy']}</p>
          <a class="btn btn-sky" href="{CONTACT_URL}" target="_blank" rel="noopener">Book a 15-minute call</a>
          <a class="btn btn-line" href="/insider-events.html">See Insider Events</a>
          <p class="ep-note"><a href="{AWARDS_URL}">Fintech Awards 2026</a> · <a href="/trending.html">Fintech database</a></p>
        </div>
      </aside>
    </div>
  </div>
</main>
""" + tail()
    (ROOT / (g['slug'] + '.html')).write_text(page, encoding='utf-8')
    return path, words

# --------------------------------------------------------------------------
# Shared links
# --------------------------------------------------------------------------
L_TRENDS = '/fintech-marketing-trends.html'
L_AGENCIES = '/fintech-marketing-agencies.html'
L_CONF = '/fintech-conferences-2027.html'
L_BANKS = '/selling-to-nordic-banks.html'
L_HACK = '/fintech-hackathon-stockholm.html'
GUIDES = [('Fintech marketing trends 2027', L_TRENDS), ('Fintech marketing, PR and event agencies', L_AGENCIES),
          ('Fintech conferences and side events 2027', L_CONF), ('Selling to Nordic banks', L_BANKS),
          ('Fintech, bank and API hackathons', L_HACK), ('Fintech Awards 2026', AWARDS_URL)]
def related(skip, *extra):
    return [(t, u) for t, u in GUIDES if u != skip] + list(extra)

TOP = RANKED[0]
STARS3 = sum(NEWS['stars'][k] for k in ('5', '4', '3'))
BUILD_DAY = ('the <a href="/roi.html">Embedded Finance Build Day</a> on 25 August 2026 cost SEK 25,000 and no paid advertising: '
             '98 registrations, 72 approved places, 44 builders in 15 teams, 15 working prototypes, 26 companies in the room '
             'and 14 warm leads at SEK 1,785 each')

# ==========================================================================
# 1. Fintech marketing trends and strategy
# ==========================================================================
kw_rows = [(E(k), str(n), f'{pct(n)}%') for k, n in TOP_KW]
serve_rows = [(lab, str(n), f'{pct(n)}%') for lab, n in SERVES_N]
trends = dict(
    slug='fintech-marketing-trends', crumb='Fintech marketing trends 2027',
    title='Fintech Marketing Trends 2027 and Strategy: Data from 220 Fintechs | Alexandra Studio'.replace('220', str(N)),
    desc=(f'Fintech marketing trends for 2027 from our own data: what {N} Nordic and European fintechs sell and who they sell to, '
          'plus a fintech marketing strategy, what makes campaigns work, and where the community is.'),
    h1='Fintech marketing trends for 2027',
    kicker='Fintech marketing strategy · Our data, 10 November 2026',
    dek=(f'What {N} fintechs in the Nordic market say they sell, who they sell it to, and what that means for your fintech '
         'marketing strategy, your campaigns and your community in 2027.'),
    keywords=['fintech marketing trends', 'fintech marketing strategy', 'best fintech marketing campaigns',
              'fintech marketing community', 'best fintech marketing', 'B2B fintech marketing'],
    toc=[('short', 'Short version'), ('trends', 'Five trends'), ('data', 'The data'), ('strategy', 'Strategy'),
         ('campaigns', 'Campaigns'), ('community', 'Community')],
    stats=stats([(f'{pct(BANKS_N)}%', f'of {N} fintechs list banks as customers'),
                 (f'{pct(COMPLIANCE)}%', 'lead with compliance, KYC, AML or fraud'),
                 (f'{pct(AI)}%', 'describe their product with AI'),
                 (f'{pct(AGENTIC)}%', 'already say “agentic” or “AI agents”'),
                 (f'{pct(API)}%', 'sell an API'),
                 (f'{fmt(NEWS["subscribers"])}', 'readers of Stockholm Growth &amp; Fintech')]),
    sections=[
        '<h2 id="short">The short version</h2>',
        f'<p>We researched {N} fintechs, banks and payments companies that are active in the Nordic market: what each one sells, who it sells to and how it describes itself. Their profiles are in our <a href="/fintech-company/">company directory</a>. Read together, they show where fintech marketing is crowded and where there is still room.</p>',
        '<ul>'
        f'<li><b>Everyone is selling to the same buyer.</b> {pct(BANKS_N)}% list banks or credit unions as customers.</li>'
        f'<li><b>AI is now table stakes.</b> {pct(AI)}% describe their product with AI, and {pct(AGENTIC)}% already use “agentic” or “AI agents”.</li>'
        f'<li><b>Compliance has become a growth message.</b> {pct(COMPLIANCE)}% lead with compliance, KYC, AML or fraud.</li>'
        f'<li><b>Infrastructure is the product.</b> {pct(API)}% sell an API; open banking and real-time payments are features, not stories.</li>'
        '<li><b>Rooms beat reach.</b> When everyone makes the same claim to the same buyer, time in person with that buyer is what moves a deal.</li>'
        '</ul>',
        '<h2 id="trends">Five fintech marketing trends for 2027</h2>',
        '<h3>1. Everyone sells to the bank</h3>',
        f'<p>{BANKS_N} of the {N} companies ({pct(BANKS_N)}%) name banks or credit unions among their customers, far ahead of merchants ({pct(dict(SERVES_N)["Merchants, retailers and e-commerce"])}%) or other fintechs ({pct(dict(SERVES_N)["Other fintechs"])}%). The same few hundred people at Nordic banks receive almost every pitch. More content and more ads add to the noise. What still gets through is a warm introduction, a stage, or a seat at a table with peers. Our guide to <a href="{L_BANKS}">selling to Nordic banks</a> covers how.</p>',
        '<h3>2. AI is table stakes; “agentic” is the new claim</h3>',
        f'<p>{pct(AI)}% of the companies describe their product with AI. “Agentic” has quickly become a positioning word too: {AGENTIC} companies ({pct(AGENTIC)}%) already use it. When a word is on every homepage it stops differentiating. Buyers believe what they see working, so show the agent doing the job: a live demo, a pilot result, or a prototype built on your API at a <a href="{L_HACK}">bank hackathon</a>. More on positioning in our newsletter: <a href="{SUBSTACK}/p/the-positioning-lag" target="_blank" rel="noopener">The Positioning Lag</a>.</p>',
        '<h3>3. Compliance is a growth message</h3>',
        f'<p>{pct(COMPLIANCE)}% of the companies lead with compliance, KYC, AML or fraud prevention, and regtech is the {SECTOR_RANK('Regtech')} sector in our profiles ({SECTOR_N["Regtech"]} companies). The EU\'s new anti-money-laundering rulebook applies from July 2027, so banks and payment companies are buying now. The marketing opportunity is to be useful rather than alarming: explain what changes, by when, and what to do first.</p>',
        '<h3>4. Infrastructure is the product, so the buyer is technical</h3>',
        f'<p>{pct(API)}% of the companies sell an API, {pct(OPEN_BANKING)}% mention open banking or PSD2 and {pct(REALTIME)}% mention real-time or instant payments. For these buyers, the developer experience is the marketing. Docs, sandboxes, a fast first API call, and engineers who show up to builder nights do more than a brand campaign.</p>',
        '<h3>5. Rooms beat reach</h3>',
        f'<p>Digital channels are crowded with the same claims to the same buyers. In-person formats with a sharp question and a short guest list cut through: executive breakfasts, partner dinners, builder nights, build days. One example: {BUILD_DAY}. We report counted results separately from estimates.</p>',
        '<h2 id="data">The data: what fintechs sell, and who they sell to</h2>',
        f'<p>The most common keywords across the {N} profiles, leaving out generic words such as “fintech” and country names:</p>',
        table(['Keyword', 'Companies', f'Share of {N}'], kw_rows),
        '<p>Who the companies say they serve. A company can serve several groups, so the shares add up to more than 100%:</p>',
        table(['Customer group', 'Companies', f'Share of {N}'], serve_rows),
        f'<p>By sector: payments ({SECTOR_N["Payments"]}), regtech ({SECTOR_N["Regtech"]}), banking ({SECTOR_N["Banking"]}), finance software ({SECTOR_N["Financial Management"]}), lending ({SECTOR_N["Lending"]}) and wealth ({SECTOR_N["Wealth Management"]}). By country: Sweden ({COUNTRY_N["Sweden"]}), the United Kingdom ({COUNTRY_N["United Kingdom"]}), Denmark ({COUNTRY_N["Denmark"]}) and Germany ({COUNTRY_N["Germany"]}) lead. Method: one profile per company, written by the Alexandra Studio team from public company information in November 2026; keywords and customer groups as stated by each company.</p>',
        '<h2 id="strategy">A fintech marketing strategy for 2027</h2>',
        '<p>For a B2B fintech selling to banks, payment companies and other licensed buyers, this is the system we run for clients:</p>',
        '<ul>'
        '<li><b>Name the accounts.</b> Start from 30 to 50 target companies and the roles on each buying committee, not a persona.</li>'
        '<li><b>Host the room.</b> One sharp question, the right size and format: breakfast, dinner, panel, builder night or build day.</li>'
        '<li><b>Borrow trust.</b> Co-host with a brand your buyers already know, so the invitation reads as an event rather than a pitch.</li>'
        '<li><b>Record it.</b> A podcast episode, a short video, quotes and photos from the day.</li>'
        '<li><b>Post together.</b> Everyone in the room posts and tags each other. Joint organic reach goes into the second-degree networks of the people you want.</li>'
        '<li><b>Follow up the same week,</b> by name, with the people who came and the people who engaged without coming.</li>'
        '</ul>',
        '<p>More on the method: <a href="/fintech-go-to-market.html">GTM for fintech</a>, <a href="/executive-roundtables-b2b-pipeline.html">executive roundtables for B2B pipeline</a> and <a href="/how-alexandra-studio-works.html">how Alexandra Studio works</a>.</p>',
        '<h2 id="campaigns">The best fintech marketing campaigns, and why they work</h2>',
        '<p>The campaigns people remember share a few traits, whether they target consumers or a bank\'s buying committee:</p>',
        '<ul>'
        '<li><b>One feeling, not a feature list.</b> Relief, control, pride: consumer fintech campaigns that work lead with how money feels.</li>'
        '<li><b>Proof for B2B.</b> For banks the emotion is safety, and safety is shown with named peers, results and regulators\' language.</li>'
        '<li><b>A real person.</b> A founder, a customer or an engineer on camera beats a stock photo of a phone.</li>'
        '<li><b>Built for sharing.</b> The best B2B campaigns give partners something to post, so reach compounds.</li>'
        '</ul>',
        f'<p>We broke down three campaigns for different audiences in <a href="{SUBSTACK}/p/trend-setting-emotional-fintech-ad" target="_blank" rel="noopener">Trend-setting emotional fintech ad campaigns</a>. Companies that keep showing up are ranked in the <a href="{AWARDS_URL}">Fintech Awards 2026</a>.</p>',
        '<h2 id="community">The fintech marketing community in Stockholm</h2>',
        f'<p><a href="{SUBSTACK}/" target="_blank" rel="noopener">Stockholm Growth &amp; Fintech</a> is Alexandra Grisanti\'s newsletter on Stockholm fintech and B2B growth. On {DATE_LABEL} it had {fmt(NEWS["subscribers"])} subscribers, {NEWS["work_email_pct"]}% on a work email across {fmt(NEWS["organisations"])} organisations. {NEWS["opened_30d_pct"]}% opened an issue in the last 30 days, and {fmt(STARS3)} readers have a three-star or higher engagement rating from Substack. (Some email apps register opens automatically, so treat open rates as an upper bound.)</p>',
        '<p>Around it: the <a href="https://theoperatornetwork.se/" target="_blank" rel="noopener">Operator Network</a>, a curated community for founders and executives in Stockholm; <a href="/insider-events.html">Insider Events</a>, its invite-only rooms; and the <a href="' + AWARDS_URL + f'">Fintech Awards</a>, which rank the {fmt(N_TRENDING)} companies most active in it. Newsletter and podcast features are editorial; they are not sold.</p>',
    ],
    faqs=[
        ('What are the biggest fintech marketing trends for 2027?',
         f'From our research on {N} fintechs: almost everyone sells to banks ({pct(BANKS_N)}%), AI is table stakes ({pct(AI)}% use it, {pct(AGENTIC)}% already say “agentic”), compliance has become a growth message ({pct(COMPLIANCE)}%), infrastructure companies sell to technical buyers ({pct(API)}% sell an API), and in-person rooms cut through where digital channels are crowded.'),
        ('What is a good fintech marketing strategy?',
         'For B2B fintech: name 30 to 50 target accounts, host rooms those buyers want to attend, co-host with a brand they already trust, record the day, post together for joint organic reach, and follow up the same week by name.'),
        ('How do you market a fintech to banks?',
         f'Banks rarely respond to cold vendor pitches. Borrow trust through a co-host the bank already works with, offer a stage before asking for a meeting, and find the person who connects business goals with digital delivery. See <a href="{L_BANKS}">selling to Nordic banks</a>.'),
        ('What makes a fintech marketing campaign work?',
         'One clear feeling for consumers, proof and named peers for B2B buyers, a real person on camera, and something partners can share.'),
        ('Where is the fintech marketing community in the Nordics?',
         f'In Stockholm: the Stockholm Growth &amp; Fintech newsletter ({fmt(NEWS["subscribers"])} subscribers), the Operator Network and its Insider Events, Stockholm Fintech Week in March, and the side events around it. Copenhagen has Nordic Fintech Week and Helsinki the Nordic Fintech Summit. See <a href="{L_CONF}">fintech conferences 2027</a>.'),
    ],
    related=related(L_TRENDS, ('Company profiles', '/fintech-company/')),
    cta_head='Want your fintech in the room with these buyers?',
    cta_copy='We design and host co-branded rooms with the accounts you name, and report who came, by name.',
)

# ==========================================================================
# 2. Agencies: marketing, PR and communications, events, market entry
# ==========================================================================
agency_cards = ''.join([
    '<li><h3><a href="/fintech-go-to-market.html">Alexandra Studio</a> <span class="gd-card-meta" style="display:inline">(that\'s us)</span></h3>'
    '<span class="gd-card-meta">B2B fintech growth studio · Stockholm, Sweden</span>'
    '<p>Works only with fintechs. Gets the buyers you name into a room you co-host with a brand they trust: executive breakfasts, dinners, panels, builder nights and build days, plus podcast and content from the room.</p></li>',
    net_card('heijbelgrowth.com', 'Growth and performance marketing'),
    net_card('growthhackers.se', 'Growth marketing'),
    net_card('precis.com', 'Digital marketing'),
    net_card('topvisible.se', 'Digital marketing'),
    net_card('hartmanagency.se', 'Design and web'),
    net_card('storykit.io', 'Video and content'),
])
venue_cards = ''.join([net_card('ahouse.se', 'Venue · our Build Day venue'), net_card('embassy.house', 'Venue · our CEO + CFO breakfast'),
                       net_card('munchenbryggeriet.se', 'Venue · Stockholm Fintech Week'), net_card('convendum.se', 'Venue')])
eco = by_domain('stockholmfintech.com', 'swefintech.se', 'copenhagenfintech.dk', 'goosevalley.vc')
eco_list = ', '.join(name_link(r) for r in eco)
agencies = dict(
    slug='fintech-marketing-agencies', crumb='Fintech marketing agencies',
    title='Best Fintech Marketing Agencies in the Nordics (2027): Marketing, PR and Event Agencies | Alexandra Studio',
    desc=('How to choose a fintech marketing agency in the Nordics: marketing, PR and communications, event agencies and '
          'market entry services, with the agencies and partners in our Stockholm network.'),
    h1='Fintech marketing, PR and event agencies in the Nordics',
    kicker='Best fintech marketing agencies · 2027 guide',
    dek=('How to choose a fintech marketing agency, what fintech PR and communications should do for you, when you need a '
         'fintech event agency, and who to call in Stockholm.'),
    keywords=['best fintech marketing agencies', 'fintech marketing agency', 'fintech PR and communications agencies',
              'fintech event agency', 'market entry services', 'best fintech marketing'],
    toc=[('short', 'Short answer'), ('choose', 'How to choose'), ('agencies', 'Agencies'), ('pr', 'PR and comms'),
         ('events', 'Event agency'), ('market-entry', 'Market entry')],
    sections=[
        '<h2 id="short">The short answer</h2>',
        '<p>There is no single best fintech marketing agency; there is a best agency for the job in front of you. Choose by the job:</p>',
        table(['The job', 'Who does it', 'What you get'], [
            ('Brand, website, content', 'Brand, design and content agencies', 'Positioning, a site, a content engine'),
            ('Demand from ads and search', 'Performance and growth agencies', 'Leads from paid and organic channels'),
            ('Media, analysts, reputation', 'PR and communications agencies', 'Coverage, briefings, crisis readiness'),
            ('Time with named buyers', 'Fintech event agencies', 'Rooms with your target accounts'),
            ('A new country', 'Market entry services', 'Local network, regulation, first customers'),
        ]),
        '<p>Most fintechs selling to banks need two of these at once: something that builds trust at scale (brand, content, PR) and something that gets the buying committee into a room (events, partnerships).</p>',
        '<h2 id="choose">How to choose a fintech marketing agency: eight questions</h2>',
        '<ul>'
        '<li><b>Have you sold to banks, payment companies or other licensed buyers?</b> Six to ten people sign off a bank deal; ask how they reach each one.</li>'
        '<li><b>Do you know the marketing rules for financial services?</b> Consumer credit, investment and payments marketing each have rules. An agency should know where the lines are.</li>'
        '<li><b>Who will actually do the work?</b> Ask to meet them, not just the pitch team.</li>'
        '<li><b>How many fintech clients do you have now, and are any competitors?</b> Some agencies, ours included, take one client per vertical.</li>'
        '<li><b>What do you report, and how often?</b> Named accounts and meetings beat impressions.</li>'
        '<li><b>What is counted and what is estimated?</b> Pipeline estimates should be labelled as estimates.</li>'
        '<li><b>What does your team need from ours?</b> Hours a week, approvals, subject-matter experts.</li>'
        '<li><b>How do we stop?</b> Month to month, or a long lock-in?</li>'
        '</ul>',
        '<h2 id="agencies">Fintech marketing agencies and partners in our Stockholm network</h2>',
        '<p>These are agencies and partners in our own network, with a line on what each does. It is not a paid ranking and nobody paid to be listed. Disclosure: Alexandra worked at Heijbel Growth as an ad designer, and Heijbel Growth has been a client.</p>',
        f'<ul class="gd-cards">{agency_cards}</ul>',
        '<h2 id="pr">Fintech PR and communications: what good looks like</h2>',
        '<p>In the Nordics, fintech PR works best when it is earned rather than pitched. A good fintech PR and communications agency, or an in-house team, should:</p>',
        '<ul>'
        '<li><b>Lead with data.</b> Journalists cover new numbers. Your own data (transaction trends, survey results, a ranking like our <a href="' + AWARDS_URL + '">Fintech Awards</a>) is the most reliable route into the trade press.</li>'
        '<li><b>Get you on stages before it gets you in print.</b> Panels at Stockholm Fintech Week, Nordic Fintech Week and the Nordic Fintech Summit put you in front of the same editors and buyers, and give them a reason to quote you.</li>'
        '<li><b>Plan for bank approvals.</b> A bank customer\'s name in a press release can take months to approve. Agree it in the contract.</li>'
        '<li><b>Know the Nordic media.</b> Breakit for Swedish tech and startups, Nordic Fintech Magazine and Sifted for fintech, plus podcasts and newsletters read by the industry.</li>'
        '<li><b>Be ready for a bad day.</b> An outage or a regulator\'s letter needs a plan written before it happens.</li>'
        '</ul>',
        f'<p>Our own content work is built from the rooms we host: podcast episodes, short videos and posts that everyone in the room shares. See <a href="/b2bleadership.html">B2B content systems</a>. Features in Stockholm Growth &amp; Fintech ({fmt(NEWS["subscribers"])} subscribers) are editorial, not sold.</p>',
        '<h2 id="events">When you need a fintech event agency</h2>',
        '<p>You need an event agency when the deal depends on people meeting: a tier-1 bank that won\'t take a cold meeting, a market where nobody knows you yet, or a conference where a booth buys ten minutes with people who are also selling. A good fintech event agency designs the room around one question, brings a co-host the guests trust, fills the seats with the accounts you named, and reports who came.</p>',
        f'<p>In 2026 we ran eleven in-person B2B events in Stockholm, Gothenburg and Amsterdam; {BUILD_DAY}. See our <a href="/alexandra-studio-track-record.html">track record</a> and the <a href="/insider-events.html">Insider Events</a> schedule. Venues in our network that work well for fintech rooms:</p>',
        f'<ul class="gd-cards">{venue_cards}</ul>',
        '<h2 id="market-entry">Market entry services for fintechs entering the Nordics</h2>',
        '<p>Help for fintechs entering Sweden or the Nordics comes from four places:</p>',
        '<ul>'
        '<li><b>Public trade and investment agencies:</b> Business Sweden and Invest Stockholm help foreign companies set up and find partners.</li>'
        f'<li><b>Fintech hubs and associations:</b> {eco_list}, and Fintech Farm in Helsinki, which runs the Nordic Fintech Summit.</li>'
        '<li><b>The regulator:</b> Finansinspektionen authorises payment and e-money institutions in Sweden; firms licensed elsewhere in the EU can passport in.</li>'
        f'<li><b>Go-to-market partners:</b> people who already have rooms with your buyers. That is what <a href="/fintech-go-to-market.html">our GTM service</a> does, and our guide to <a href="{L_BANKS}">selling to Nordic banks</a> covers the rest.</li>'
        '</ul>',
    ],
    faqs=[
        ('What is the best fintech marketing agency?',
         'The best one for your job: brand and content agencies for positioning, performance agencies for paid demand, PR agencies for coverage, event agencies for time with named buyers, and market entry partners for a new country. Ask whether they have sold to banks and licensed buyers, who does the work, and what is counted versus estimated.'),
        ('What does a fintech PR and communications agency do?',
         'Earns coverage and reputation: data-led stories for the trade press, speaking slots, analyst briefings, customer announcements (with bank approvals planned in), and a plan for bad days.'),
        ('What is a fintech event agency?',
         'An agency that gets your target buyers into a room: executive breakfasts, partner dinners, panels, builder nights and build days, usually co-hosted with a brand the guests trust, with a report of who came.'),
        ('What market entry services exist for the Nordics?',
         'Public agencies such as Business Sweden and Invest Stockholm, fintech hubs and associations, the regulator Finansinspektionen for licensing, and go-to-market partners who already have rooms with your buyers.'),
        ('Is Alexandra Studio a fintech marketing agency?',
         'Alexandra Studio is a Stockholm B2B growth studio that works only with fintechs, as a fintech marketing and event agency. The growth engagement is free for the first month, then SEK 55,000 a month excluding VAT, invoiced only for months that reach 30 qualified leads and 5 held calls.'),
    ],
    related=related(L_AGENCIES, ('How Alexandra Studio works', '/how-alexandra-studio-works.html')),
    cta_head='Looking for a fintech event agency?',
    cta_copy='Tell us the accounts you need to meet. We will name the room, the co-host and the route in.',
)

# ==========================================================================
# 3. Conferences 2027 and side events, booth or not
# ==========================================================================
cal = [
    ('Techarena 2027', '3–4 Feb 2027', 'Strawberry Arena, Stockholm', 'Scandinavia\'s largest tech and business event, with hundreds of partner side events. Our <a href="/events/post-tech-arena-vip-dinner.html">Post Tech Arena VIP Dinner</a> is on 4 February.'),
    ('Stockholm Fintech Week 2027', '17–18 Mar 2027', 'Stockholm', '17 March is a day of side events across the city; 18 March is the conference at Münchenbryggeriet. The ninth edition.'),
    ('The Financial Brand Forum 2027', '5–7 Apr 2027', 'ARIA, Las Vegas', 'The big US conference on bank and credit union marketing, CX and digital growth.'),
    ('Nordic Fintech Summit 2027', '13 May 2027', 'Helsinki', 'Run by Fintech Farm. Alexandra hosted its Nordic Fintech Highlights Stage in 2026.'),
    ('Money20/20 Europe 2027', '8–10 Jun 2027', 'RAI, Amsterdam', 'Europe\'s largest payments and fintech show.'),
    ('Nordic Fintech Week 2027', 'Not yet announced', 'Copenhagen', 'In 2026 the main conference days were 23–24 September at TAP1.'),
]
conf = dict(
    slug='fintech-conferences-2027', crumb='Fintech conferences 2027',
    title='Fintech Conferences 2027 and Side Events: Money20/20 Europe, Stockholm Fintech Week, Nordic Fintech Week | Alexandra Studio',
    desc=('The 2027 fintech conference calendar for the Nordics and Europe, how side events work around Money20/20 Europe, '
          'Stockholm Fintech Week and Nordic Fintech Week, and whether a Money20/20 booth is worth it.'),
    h1='Fintech conferences and side events in 2027',
    kicker='Fintech marketing conference 2027 · Dates checked 10 November 2026',
    dek=('The 2027 dates for the Nordic and European fintech calendar, how to win the side events around Money20/20 Europe, '
         'Stockholm Fintech Week and Nordic Fintech Week, and an honest answer to “is a Money20/20 booth worth it?”'),
    keywords=['fintech marketing conference 2027', 'fintech marketing conference', 'Money20/20 Europe side events',
              'Stockholm Fintech Week side events', 'Nordic Fintech Week side events', 'Is a Money20/20 booth worth it',
              'fintech event agency'],
    toc=[('calendar', '2027 calendar'), ('which', 'Which to pick'), ('money2020', 'Money20/20 side events'),
         ('sfw', 'Stockholm Fintech Week'), ('nfw', 'Nordic Fintech Week'), ('booth', 'Booth worth it?')],
    sections=[
        '<h2 id="calendar">The 2027 fintech conference calendar</h2>',
        '<p>Dates as published by the organisers on 10 November 2026. Check the official sites before you book travel.</p>',
        table(['Event', 'When', 'Where', 'Why it matters'], [(f'<b>{a}</b>', b, c, d) for a, b, c, d in cal]),
        '<p>Our own invite-only rooms in Stockholm before the spring season: the <a href="/events/end-of-year-tech-demo-2026.html">End of Year Tech Demo</a> on 15 December 2026, the <a href="/events/vc-founder-dinner.html">VC Founder Dinner</a> on 26 January 2027 and the Post Tech Arena VIP Dinner on 4 February 2027. See <a href="/insider-events.html">Insider Events</a>.</p>',
        '<h2 id="which">Which fintech marketing conference should you pick in 2027?</h2>',
        '<ul>'
        '<li><b>To meet Nordic banks:</b> Stockholm Fintech Week, Nordic Fintech Week and the Nordic Fintech Summit. Smaller crowds and more bank people per square metre.</li>'
        '<li><b>To meet the global payments industry:</b> Money20/20 Europe.</li>'
        '<li><b>To learn bank marketing craft:</b> The Financial Brand Forum, if your buyers are US banks and credit unions.</li>'
        '<li><b>For investors and the wider Stockholm tech scene:</b> Techarena.</li>'
        '</ul>',
        '<p>Whichever you pick, most of the business happens around the conference rather than on the floor: in the breakfasts, dinners and side events where twelve people can talk for two hours.</p>',
        '<h2 id="money2020">Money20/20 Europe side events</h2>',
        '<p>Money20/20 Europe runs 8–10 June 2027 at the RAI in Amsterdam. During the show, the evenings fill up with partner dinners, receptions and parties across the city. What works:</p>',
        '<ul>'
        '<li><b>Invite early.</b> Senior guests fill their evenings weeks before the show. Send personal invitations at least four weeks ahead.</li>'
        '<li><b>Keep it small.</b> A dinner for 12 to 20 named guests beats a party for 200 you have never met.</li>'
        '<li><b>Co-host.</b> Two or three companies that sell to the same buyer, without competing, share the cost and each other\'s networks.</li>'
        '<li><b>Stay close to the RAI,</b> or near the hotels guests already use, so nobody has to cross the city.</li>'
        '</ul>',
        '<p>In June 2026 we ran a partner dinner in Amsterdam after Money20/20 Europe with Copenhagen Fintech, Swedish Fintech, Surfboard Payments, Movitz Payments, Narvi Payments and Griffin Bank. Our newsletter covered the show in <a href="' + SUBSTACK + '/p/money-2020-the-payments-jungle" target="_blank" rel="noopener">Money 20/20: The Payments Jungle</a>.</p>',
        '<h2 id="sfw">Stockholm Fintech Week side events</h2>',
        '<p>For 2027 the organisers have made side events official: 17 March is a full day of side events across Stockholm, the day before the conference on 18 March. That makes it the best day of the year to host a fintech breakfast or dinner in Stockholm, and the most crowded. To stand out:</p>',
        '<ul>'
        '<li><b>Book the venue now.</b> Good rooms for 15 to 40 people go first.</li>'
        '<li><b>Pick a time slot others avoid.</b> Breakfast on the side-event day, or a dinner after the conference, competes less than the evening of the 17th.</li>'
        '<li><b>Invite the delegations.</b> Copenhagen Fintech and other hubs bring member delegations to Stockholm Fintech Week and look for side events to join.</li>'
        '<li><b>Give it one question.</b> “Is growth a judgement call?” fills a breakfast; “networking” does not.</li>'
        '</ul>',
        '<p>Alexandra spoke on a Stockholm Fintech Week 2026 panel. If you want a side event on 17 March 2027, we can design, co-host and fill it; see <a href="' + L_AGENCIES + '#events">fintech event agency</a>.</p>',
        '<h2 id="nfw">Nordic Fintech Week side events</h2>',
        '<p>Nordic Fintech Week is Copenhagen\'s fintech week, run by Copenhagen Fintech. The 2027 dates have not been announced yet; in 2026 the main conference days were 23–24 September at TAP1. Around the conference there are roundtables, receptions, a morning run and partner side events hosted by banks and fintechs. The same rules apply: a short guest list, a co-host, one question, and invitations out four weeks ahead. Our newsletter wrote about <a href="' + SUBSTACK + '/p/1o-fintechs-at-nordic-fintech-week" target="_blank" rel="noopener">10 fintechs at Nordic Fintech Week</a>.</p>',
        '<h2 id="booth">Is a Money20/20 booth worth it?</h2>',
        '<p>Sometimes. A booth buys presence: 10 to 20 minutes at a time with people who are often there to sell, too. Add up the cost first:</p>',
        '<ul>'
        '<li><b>Floor space,</b> priced by the organiser.</li>'
        '<li><b>The stand itself.</b> The show contractor\'s ready-made stand packages for Money20/20 have been listed from €4,800 for 9 m² and €7,500 for 18 m², excluding VAT and the space.</li>'
        '<li><b>Passes for your team.</b> Delegate passes have been listed from about €1,200 a person.</li>'
        '<li><b>Travel, hotels in Amsterdam in June, and three days of your best people.</b></li>'
        '</ul>',
        table(['Option', 'Time with buyers', 'Best when'], [
            ('A booth', '10–20 minutes, with people walking past', 'You launch to a global payments audience, or already have meetings booked'),
            ('A side-event dinner', 'Two hours with 12–20 guests you chose', 'You sell to a short list of named accounts'),
            ('Both', 'Presence by day, conversations at night', 'You have the budget and the team to staff both'),
        ]),
        '<p>A booth is worth it when you need to be seen by a broad payments audience, or when your meetings are already booked and the booth is where they happen. It is rarely worth it when you sell to a short list of Nordic banks; a dinner beside the show buys more time with them for less. Our full comparison of booth, hire and agency is in <a href="/how-alexandra-studio-works.html#compare">Agency, hire or booth?</a></p>',
    ],
    faqs=[
        ('When is Money20/20 Europe 2027?', '8–10 June 2027 at the RAI in Amsterdam.'),
        ('When is Stockholm Fintech Week 2027?', '17–18 March 2027. 17 March is a day of side events across Stockholm; the conference is on 18 March at Münchenbryggeriet.'),
        ('When is Nordic Fintech Week 2027?', 'The 2027 dates had not been announced on 10 November 2026. In 2026 the main conference days were 23–24 September at TAP1 in Copenhagen.'),
        ('What is the best fintech marketing conference in 2027?',
         'For Nordic banks: Stockholm Fintech Week (17–18 March), the Nordic Fintech Summit (13 May, Helsinki) and Nordic Fintech Week (Copenhagen). For global payments: Money20/20 Europe (8–10 June). For US bank marketing: The Financial Brand Forum (5–7 April, Las Vegas).'),
        ('Is a Money20/20 booth worth it?',
         'It can be if you need broad visibility with the global payments industry or already have meetings booked. If you sell to a short list of named banks, a side-event dinner for 12 to 20 of them usually buys more time with your buyers for less.'),
        ('How do I host a side event at Stockholm Fintech Week?',
         'Pick one sharp question, book a venue for 15 to 40 people early, co-host with a brand your guests trust, and send personal invitations at least four weeks ahead. 17 March 2027 is the official side-event day.'),
    ],
    related=related(L_CONF, ('Insider Events', '/insider-events.html')),
    cta_head='Hosting a side event in 2027?',
    cta_copy='We design, co-host and fill side events around Stockholm Fintech Week, Money20/20 Europe and Nordic Fintech Week.',
)

# ==========================================================================
# 4. Selling to Nordic banks
# ==========================================================================
NORDIC_BANKS = ['Nordea', 'Danske Bank', 'SEB', 'Handelsbanken', 'Svea Bank', 'Lunar', 'SBAB', 'Marginalen Bank', 'Nordnet']
bank_rows = []
for nm in NORDIC_BANKS:
    r = next((x for x in ROWS if x['name'] == nm), None)
    if r:
        bank_rows.append((name_link(r), E(place(r)),
                          f'<span class="db-pts">+{fmt(r["pts"])}</span> (#{RANK[id(r)]})' if r['pts'] else '–'))
sellers = [r for r in RANKED if r['profile'] and re.search(r'\bbanks?\b|banking|credit union', r['profile']['serves'].lower())
           and r['name'] not in NORDIC_BANKS][:8]
banks = dict(
    slug='selling-to-nordic-banks', crumb='Selling to Nordic banks',
    title='Selling to Nordic Banks: How to Sell to Banks, Tier-1 Partnerships and Market Entry in Sweden | Alexandra Studio',
    desc=('How fintechs sell to Nordic banks: who buys, how long it takes, what DORA and procurement ask of you, '
          'how to partner with tier-1 banks, enter Sweden and get leads in the Nordics.'),
    h1='Selling to Nordic banks',
    kicker='How to sell to banks · Go-to-market in the Nordics',
    dek=('How fintechs get into Nordic banks: who buys, how long it takes, what procurement and regulation ask of you, how to '
         'partner with a tier-1 bank, and how to get leads in the Nordics when banks don\'t take cold pitches.'),
    keywords=['selling to Nordic banks', 'how to sell to banks', 'selling to tier-1 banks', 'fintech bank partnerships',
              'go-to-market Nordics', 'fintech market entry Sweden', 'how to get leads in the Nordics', 'market entry services'],
    toc=[('short', 'Short answer'), ('banks', 'The banks'), ('committee', 'Who buys'), ('time', 'Why it takes time'),
         ('tier1', 'Tier-1 banks'), ('partnerships', 'Partnerships'), ('sweden', 'Entering Sweden'), ('leads', 'Getting leads')],
    stats=stats([(f'{pct(BANKS_N)}%', f'of {N} fintechs we researched sell to banks'),
                 ('6–10', 'people sign off a typical bank deal'),
                 (f'#{RANK[id(TOP)]}', f'{E(TOP["name"])} tops the Fintech Awards 2026')]),
    sections=[
        '<h2 id="short">The short answer</h2>',
        '<p>Nordic banks don\'t answer cold vendor pitches. You get in by borrowing trust: a co-host the bank already works with, a stage you offer before you ask for anything, and the one person inside the bank who connects business goals with digital delivery. Then you need patience for procurement, and paperwork that is ready before they ask.</p>',
        f'<p>You will not be alone. {BANKS_N} of the {N} fintechs in our <a href="/fintech-company/">company profiles</a> ({pct(BANKS_N)}%) list banks as customers, so the people you want to reach hear the same pitch every week. Trust and access are the difference.</p>',
        '<h2 id="banks">The Nordic banks in our data</h2>',
        '<p>Banks are not only buyers; they are active in the community. Here is where the main Nordic banks stand in the <a href="' + AWARDS_URL + '">Fintech Awards 2026</a>, which rank engagement with fintech buyers, partners and our readers:</p>',
        table(['Bank', 'Headquarters', 'Fintech Award Points'], bank_rows),
        '<p>Where we have met each bank, and how many of their people read our newsletter, is listed bank by bank in <a href="/how-alexandra-studio-works.html#banks">Bank access: where we stand</a>.</p>',
        '<h2 id="committee">Who buys inside a bank</h2>',
        '<p>A fintech sale to a bank usually needs six to ten people to agree:</p>',
        '<ul>'
        '<li><b>The business owner</b> whose numbers improve: head of payments, cards, lending or a business area.</li>'
        '<li><b>The digital or product lead</b> who connects business goals with delivery. Often the best first contact.</li>'
        '<li><b>Architecture and IT</b>, who decide whether you fit the stack.</li>'
        '<li><b>Information security</b>, who review your controls.</li>'
        '<li><b>Compliance and risk</b>, who decide whether you create a regulatory problem.</li>'
        '<li><b>Procurement and vendor management</b>, who run the process and the contract.</li>'
        '<li><b>Legal</b>, and for big deals, a <b>sponsor in the executive team</b>.</li>'
        '</ul>',
        '<p>Most of them won\'t be reached by an ad. They do come to a well-chosen room: a breakfast with peers, a panel, a dinner, or a build day on an API they are curious about.</p>',
        '<h2 id="time">Why selling to banks takes time, and how to shorten it</h2>',
        '<p>Banks have to check their suppliers. Under the EU\'s Digital Operational Resilience Act (DORA), which applies from 17 January 2025, banks must manage the risk from their ICT providers, keep a register of them, and put specific terms in their contracts. Outsourcing of critical or important functions also falls under the European Banking Authority\'s outsourcing guidelines. In practice, have these ready before the first meeting:</p>',
        '<ul>'
        '<li>Security documentation: certifications such as ISO 27001 or SOC 2 reports, penetration test summaries, an incident process.</li>'
        '<li>Where data is stored and processed, and your sub-processors.</li>'
        '<li>Contract terms banks will ask for: audit rights, service levels, incident reporting, an exit plan.</li>'
        '<li>Financial information that shows you will still be there in three years.</li>'
        '</ul>',
        '<p>This is not legal advice; check the details with counsel. But a fintech that arrives with the pack ready saves months.</p>',
        '<h2 id="tier1">Selling to tier-1 banks</h2>',
        '<ul>'
        '<li><b>Start with a problem they have already named</b> in a strategy, an annual report or a talk by one of their people.</li>'
        '<li><b>Offer a stage first.</b> A panel seat, a podcast episode or a keynote slot. People who have been offered a stage take the next meeting.</li>'
        '<li><b>Go through someone they already buy from.</b> Core banking providers, consultancies and cloud partners already approved by the bank can bring you in faster than procurement can.</li>'
        '<li><b>Make the first step small.</b> A sandbox, a pilot or a build day is easier to say yes to than a contract.</li>'
        '<li><b>Map the whole committee.</b> A champion without a sponsor stalls at procurement.</li>'
        '</ul>',
        '<h2 id="partnerships">Fintech bank partnerships: four models</h2>',
        table(['Model', 'The bank is…', 'What it takes'], [
            ('Bank as customer', 'buying your product', 'Procurement, security review, a business case'),
            ('Bank as distributor', 'offering your product to its customers, often white-label or embedded', 'Product fit, revenue share, brand approval'),
            ('Bank as infrastructure', 'holding the licence or accounts behind your product (BaaS)', 'Compliance alignment, a long contract'),
            ('Bank as co-host', 'sharing a stage, a room or a report with you', 'A good idea and a short ask'),
        ]),
        '<p>The fourth is the easiest way to start the other three. See <a href="/co-marketing-vs-partner-led-growth-fintech.html">co-marketing vs partner-led growth</a> and <a href="/nordic-fintech-partner-led-go-to-market.html">how Nordic fintechs build a partner-led go-to-market</a>.</p>',
        '<h2 id="sweden">Go-to-market in the Nordics: fintech market entry in Sweden</h2>',
        '<ul>'
        '<li><b>Licensing.</b> Finansinspektionen authorises banks, payment institutions and e-money institutions in Sweden. If you are licensed in another EU country, you can usually passport in after notifying your home regulator.</li>'
        '<li><b>Local rails.</b> Swedes identify with BankID and pay each other with Swish; Denmark has MitID and MobilePay, Norway BankID and Vipps. Fit in with them.</li>'
        '<li><b>Language.</b> English works for B2B sales and events; consumer products and documents usually need Swedish.</li>'
        '<li><b>Proof from next door.</b> A Danish, Finnish or Norwegian reference opens Swedish doors faster than one from further away.</li>'
        '<li><b>A local network.</b> The hardest part to build alone. Cardboard, a Norwegian company with no Swedish network, was positioned in Stockholm next to Gilion and Fairlo at a breakfast we ran.</li>'
        '</ul>',
        f'<p>For the regulation in plain language, see our newsletter\'s <a href="{SUBSTACK}/p/opportunities-in-regulation-the-swedish" target="_blank" rel="noopener">Swedish Regulation Cheat Sheet</a>. For market entry help, see <a href="{L_AGENCIES}#market-entry">market entry services</a> and our <a href="/fintech-go-to-market.html">GTM for fintech</a>.</p>',
        '<h2 id="leads">How to get leads in the Nordics</h2>',
        '<ul>'
        '<li><b>Warm introductions</b> from people your buyers already trust.</li>'
        '<li><b>Co-hosted rooms</b> with a short guest list of named accounts.</li>'
        '<li><b>A stage before a sales call:</b> panels, podcasts, newsletter features.</li>'
        f'<li><b>Build days and hackathons</b> on your API. {BUILD_DAY}.</li>'
        f'<li><b>Side events</b> around Stockholm Fintech Week and Money20/20 Europe; see <a href="{L_CONF}">fintech conferences 2027</a>.</li>'
        '</ul>',
        '<p>More in <a href="/reach-senior-fintech-buyers-without-paid-ads.html">how to reach senior fintech buyers without paid ads</a>. Fintechs in our data that sell to banks and rank highest in the Fintech Awards:</p>',
        li_cards(sellers),
    ],
    faqs=[
        ('How do you sell to banks?',
         'Borrow trust through a co-host the bank already works with, offer a stage before asking for a meeting, find the person who connects business goals with digital delivery, map the whole buying committee, and arrive with security, data and contract documentation ready.'),
        ('How long does it take to sell to a Nordic bank?',
         'Usually months rather than weeks, because six to ten people need to agree and the bank has to check you as a supplier. Having your security, data and contract pack ready, and starting with a small pilot, shortens it.'),
        ('What does DORA mean for fintechs selling to banks?',
         'Since 17 January 2025, EU banks must manage risk from their ICT providers, keep a register of them and include specific contract terms. Expect questions on security, incidents, data location, audit rights and exit plans. Check details with counsel.'),
        ('How do fintechs partner with banks?',
         'Four common models: the bank as customer, as distributor of your product, as the licensed infrastructure behind it, or as co-host of a room, stage or report. Co-hosting is the easiest place to start.'),
        ('How do I enter the Swedish fintech market?',
         'Sort out licensing with Finansinspektionen or passport in from another EU country, fit in with local rails such as BankID and Swish, bring a reference from a neighbouring Nordic country, and borrow a local network through co-hosted rooms and partners.'),
        ('How do you get leads in the Nordics?',
         'Warm introductions, co-hosted rooms with named accounts, a stage before a sales call, build days on your API and side events around the big conferences. Cold outreach to banks rarely works.'),
    ],
    related=related(L_BANKS, ('Bank access, bank by bank', '/how-alexandra-studio-works.html#banks')),
    cta_head='Need a way into a Nordic bank?',
    cta_copy='Send us your target banks. The proposal names the role we would approach at each one and the route in.',
)

# ==========================================================================
# 5. Hackathons in Stockholm
# ==========================================================================
apis = sorted([r for r in PROFILED if r['profile']['vertical'] == 'Hackathons'], key=lambda r: (-r['pts'], r['name'].lower()))
hack = dict(
    slug='fintech-hackathon-stockholm', crumb='Fintech hackathons in Stockholm',
    title='Fintech Hackathons in Stockholm: Bank Hackathons and API Hackathons | Alexandra Studio',
    desc=('Fintech, bank and API hackathons in Stockholm: what they are for, how to run one that produces pipeline, '
          'results from our Embedded Finance Build Day, and banking APIs builders can use.'),
    h1='Fintech, bank and API hackathons in Stockholm',
    kicker='Fintech hackathon · Bank hackathon · API hackathon Stockholm',
    dek=('What a bank hackathon is for, how to run an API hackathon in Stockholm that produces pipeline rather than pizza boxes, '
         'and the banking and fintech APIs builders can use.'),
    keywords=['fintech hackathon', 'bank hackathon', 'API hackathon Stockholm', 'fintech hackathon Stockholm',
              'embedded finance hackathon', 'build day'],
    toc=[('short', 'Short answer'), ('build-day', 'The Build Day'), ('types', 'Three kinds'), ('how', 'How to run one'),
         ('apis', 'APIs to build on'), ('hackathons-2027', 'In 2027')],
    stats=stats([('15', 'working prototypes in one day'), ('44', 'builders in 15 teams'), ('SEK 1,785', 'per warm lead, no paid ads')]),
    sections=[
        '<h2 id="short">The short answer</h2>',
        '<p>A fintech hackathon is one of the few formats where a bank\'s developers, product people and go-to-market leads spend a whole day with your API. Done well, it produces working prototypes, named leads and a day\'s worth of content. Done badly, it produces pizza boxes. The difference is the problem statement, the guest list and the follow-up.</p>',
        '<h2 id="build-day">Case: the Embedded Finance Build Day</h2>',
        f'<p>On 25 August 2026, at A House by Slussen in Stockholm, we ran a vendor-neutral, one-day hackathon where developers and go-to-market leads, including people from financial institutions, built finance agents on real banking APIs. Partners were Open Payments, Zwapgrid, Danske Bank, Froda, Worldline and Dun &amp; Bradstreet, with Solvapay. In short, {BUILD_DAY}. Seven of fifteen teams chose the same problem on their own, which is product validation you cannot buy.</p>',
        '<p>142 organisations were reached organically, including target accounts such as SEB Embedded, Fortnox, Klarna and Insurely whose people engaged without registering. Pipeline value is an estimate and reported separately; see the <a href="/roi.html">case study</a> and our <a href="/alexandra-studio-track-record.html">track record</a>.</p>',
        '<p>Smaller formats work too. <a href="/events/payment-layer-build-night.html">The Payment Layer: Build Night by SolvaPay</a> on 15 June 2026 at Antler in Stockholm brought builders together for demos and a few hours of building on payments for AI agents, with Kindly, Zwapgrid and SolvaPay.</p>',
        '<h2 id="types">Fintech hackathon, bank hackathon or API hackathon?</h2>',
        table(['Format', 'Who builds', 'What it is for'], [
            ('Fintech hackathon', 'Startup teams, students, developers', 'Ideas and talent around a fintech theme'),
            ('Bank hackathon', 'Teams from banks, often with fintechs', 'New products on the bank\'s own data and systems, internal change'),
            ('API hackathon', 'Developers from your target customers', 'Adoption of one or more APIs, and leads for the API providers'),
        ]),
        '<p>Our build days sit between the last two: closed, curated guest lists, real banking APIs, and builders who work at the companies the partners want to sell to.</p>',
        '<h2 id="how">How to run a bank or API hackathon that produces pipeline</h2>',
        '<ul>'
        '<li><b>One problem statement</b> your buyers already care about. Not “innovate in payments”.</li>'
        '<li><b>Sandboxes that work at 9 am.</b> Test data, keys and docs ready before the day; a partner engineer on hand.</li>'
        '<li><b>A curated guest list.</b> Approve every seat. The value is who builds, not how many.</li>'
        '<li><b>Mentors from the banks.</b> People from a bank on the floor make the day worth attending for everyone else.</li>'
        '<li><b>A jury and a deadline.</b> Working prototypes demoed by the end of the day.</li>'
        '<li><b>Content from the room.</b> Every team and partner posts; that is where the organic reach comes from.</li>'
        '<li><b>Follow-up within a week,</b> by name, and counted results reported separately from estimates.</li>'
        '</ul>',
        '<h2 id="apis">Banking and fintech APIs builders can use</h2>',
        '<p>Companies from our hackathon research that offer APIs, data or platforms teams can build on. Being listed does not mean a company has taken part in one of our events.</p>',
        li_cards(apis[:12]),
        '<p>More in the <a href="/fintech-company/">company profiles</a> and the <a href="/fintech-companies/regtech.html">regtech</a> and <a href="/fintech-companies/payments.html">payments</a> lists.</p>',
        '<h2 id="hackathons-2027">API and bank hackathons in Stockholm in 2027</h2>',
        '<p>We run build days and builder nights with partners who bring their APIs. Upcoming rooms are on <a href="/insider-events.html#upcoming">Insider Events</a>, starting with the End of Year Tech Demo on 15 December 2026. If you want to co-host a build day on your API, with banks in the room, talk to us.</p>',
    ],
    faqs=[
        ('What is a bank hackathon?',
         'A day or two where teams, often including people from banks, build prototypes on banking data and APIs around one problem. The best ones have curated guest lists, working sandboxes, bank mentors and a jury.'),
        ('How much does a fintech hackathon cost?',
         'It depends on size and venue. Our Embedded Finance Build Day in Stockholm cost SEK 25,000 with no paid advertising and produced 14 warm leads, SEK 1,785 per lead.'),
        ('Is there an API hackathon in Stockholm in 2027?',
         'We run build days and builder nights with API partners in Stockholm. Upcoming dates are on Insider Events; partners can also co-host their own build day with us.'),
        ('How do you get value from sponsoring a hackathon?',
         'Bring a working sandbox and an engineer, set a problem your buyers care about, make sure your target accounts are among the builders, and follow up with every team within a week.'),
        ('Who comes to a bank hackathon?',
         'At our Build Day: developers, product people and go-to-market leads, with co-founders, CTOs and Heads of Digital in the room, from 26 companies.'),
    ],
    related=related(L_HACK, ('Build Day case study', '/roi.html')),
    cta_head='Want to co-host a build day on your API?',
    cta_copy='We bring the room, the builders and the banks. You bring the sandbox.',
)

if __name__ == '__main__':
    for g in (trends, agencies, conf, banks, hack):
        path, words = render(g)
        print(f'{path}: {words} words')
