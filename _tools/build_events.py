#!/usr/bin/env python3
"""Builds insider-events.html and events/<slug>.html from the EVENTS list below.

Run from the repo root:   python3 _tools/build_events.py
Folders starting with "_" are not published by GitHub Pages, so this script
stays private. To add dates later, fill in start / end (and reg_close if
registration closes before the event starts) and run it again.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://alexandrastudio.se'
LUMA_IMG = 'https://images.lumacdn.com/cdn-cgi/image/format=auto,fit=cover,dpr=2,background=white,quality=80,width={w},height={w}{path}'
SPRING_COUNT = 16

E = html.escape

# --------------------------------------------------------------------------
# Events. Times are Stockholm time with the UTC offset (+01:00 winter, +02:00 summer).
# --------------------------------------------------------------------------
EVENTS = [
  # ---------------- upcoming ----------------
  dict(
    slug='end-of-year-tech-demo-2026', status='upcoming',
    title='End of Year Tech Demo 2026', luma='https://luma.com/5oziemqf',
    cover='/uploads/1z/9b78c58d-f6ce-4968-9129-a3383d4b9729.png',
    start=None, end=None, reg_close=None, date_label=None,
    venue='Stockholm. The address is shared with approved guests.',
    hosts=['Alexandra Grisanti'], presented='Operator Network', views=204,
    seo_title='End of Year Tech Demo 2026, Stockholm | Insider Events',
    meta='An invite-only demo night in Stockholm closing 2026: live product demos for a SaaS and fintech executive network of operators and investors.',
    dek="The Operator Network closes 2026 with live demos: what Stockholm's builders shipped this year, shown to the executives, operators and investors who will use, buy or back it.",
    body=[
      ('h2', 'What it is'),
      ('p', 'Insider Events are the rooms of the Operator Network, a hands-on executive network for getting in, getting seen and getting heard by the industry. The End of Year Tech Demo is the year-end edition, built around working products rather than slides.'),
      ('h2', "Who it's for"),
      ('p', 'Founders and product, engineering and go-to-market leads with something live to show, and the SaaS and fintech executives, operators and investors who want to see it first. The guest list is kept small so every demo gets a real conversation afterwards.'),
      ('h2', 'How to join'),
      ('p', 'Every seat is approved by the host, Alexandra Grisanti. Request to join on Luma. Approved guests receive the exact address in Stockholm and the details for the evening.'),
    ]),
  dict(
    slug='vc-founder-dinner', status='upcoming',
    title='VC Founder Dinner', luma='https://luma.com/f9cyd5yl',
    cover='/uploads/1s/f1c62d43-1a62-4766-8010-56c9157befd5.png',
    start=None, end=None, reg_close=None, date_label=None,
    venue='Stockholm. The address is shared with approved guests.',
    hosts=['Alexandra Grisanti'], presented='Operator Network', views=109,
    seo_title='VC Founder Dinner, Stockholm | Insider Events',
    meta='An invite-only dinner in Stockholm where founders sit with investors and operators: operator-led growth and investment in Sweden, around one table.',
    dek='A small dinner in Stockholm that seats founders next to the investors and operators who back companies like theirs.',
    body=[
      ('h2', 'What it is'),
      ('p', "Most founder and investor conversations happen in a twenty-minute pitch slot. This one happens over dinner, with a guest list small enough for one conversation around the table. It's part of Insider Events, the Operator Network's invite-only series for Stockholm's SaaS and fintech executive network."),
      ('h2', 'Operator-led growth and investment in Sweden'),
      ('p', 'Some of the most useful early backers in the Nordics are operators: people who have built, sold or scaled companies and now invest in the next ones. They bring growth advice and introductions along with the capital. The dinner is set up for that kind of conversation: what is working, what is not, and who should meet whom.'),
      ('p_sv', 'VC Founder Dinner är en liten middag i Stockholm där grundare möter investerare och operatörer. Fokus ligger på operator-led growth och investeringar i Sverige: tillväxtråd, kapital och introduktioner från människor som själva har byggt och skalat bolag.'),
      ('h2', 'How to join'),
      ('p', 'Every seat is approved by the host, Alexandra Grisanti. Request to join on Luma. Approved guests receive the exact address in Stockholm and the details for the evening.'),
    ]),
  dict(
    slug='post-tech-arena-vip-dinner', status='upcoming',
    title='Post Tech Arena VIP Dinner', luma='https://luma.com/wq6ym0th',
    cover='/uploads/4m/17d4ec66-d242-4b9e-aebe-114fa7b4de17.png',
    start=None, end=None, reg_close=None, date_label=None,
    venue='Stockholm. The address is shared with approved guests.',
    hosts=['Alexandra Grisanti'], presented='Operator Network', views=157,
    seo_title='Post Tech Arena VIP Dinner, Stockholm | Insider Events',
    meta='An invite-only VIP dinner in Stockholm after Tech Arena, for executives, speakers and partners from a SaaS and fintech executive network.',
    dek='After Tech Arena, a seated dinner for a short guest list of executives, speakers and partners, away from the expo floor.',
    body=[
      ('h2', 'What it is'),
      ('p', 'Conference days are crowded and short on time. The conversations that lead somewhere usually start once the badges come off. The Post Tech Arena VIP Dinner gives a small group a table, a good meal and time to talk after the main event.'),
      ('h2', 'Why a side event'),
      ('p', 'A booth buys ten-minute conversations with people who are also there to sell. A side event buys a few hours with the people you actually want to meet. We wrote about the trade-off in <a href="/how-alexandra-studio-works.html#compare">Agency, hire or booth?</a>'),
      ('h2', 'How to join'),
      ('p', 'Every seat is approved by the host, Alexandra Grisanti. Request to join on Luma. Approved guests receive the exact address in Stockholm and the details for the evening.'),
    ]),

  # ---------------- previous ----------------
  dict(
    slug='embedded-finance-build-day', status='past',
    title='Embedded Finance Build Day', luma='https://luma.com/iu1vjsov',
    cover='/uploads/b3/8a700730-2e09-47ce-ad21-8fc1c0e90786.png',
    start='2026-08-25T08:00:00+02:00', end='2026-08-25T20:00:00+02:00',
    date_label='Tuesday 25 August 2026 · 08:00–20:00', short_date='25 Aug 2026',
    venue_name='A House, Katarinahuset', street='Stadsgården 6', postal='116 45',
    venue='A House, Katarinahuset, Stadsgården 6, 116 45 Stockholm (Slussen)',
    hosts=['Alexandra Grisanti', 'Ellen Freij'], presented='Operator Network', went=91,
    seo_title='Embedded Finance Build Day: Bank Hackathon, Stockholm | Insider Events',
    meta='A vendor-neutral, one-day bank and API hackathon in Stockholm on 25 August 2026: 44 builders, 15 teams and 15 working prototypes on partners’ banking APIs.',
    dek='For the first time, banks built together: a closed, one-day hackathon where developers and go-to-market leaders from financial institutions built finance agents on real banking APIs.',
    body=[
      ('h2', 'What happened'),
      ('p', 'A vendor-neutral, one-day hackathon at the intersection of agentic AI and financial infrastructure. Developers and go-to-market leaders from financial institutions across Stockholm spent the day building finance agents with the APIs and technologies shaping the next layer of finance, including Open Payments and Zwapgrid.'),
      ('h2', 'In numbers'),
      ('ul', ['<b>98</b> registrations and <b>72</b> approved places',
              '<b>44</b> builders in <b>15</b> teams, who built <b>15</b> working prototypes',
              '<b>26</b> companies in the room',
              '<b>14</b> warm leads, at SEK 1,785 each',
              'SEK 25,000 in total, with no paid advertising']),
      ('h2', 'The jury'),
      ('ul', ['Dan Hyyrynen, CTO, Froda',
              'Ola Hjorth, Head of Technology and Engineering for Digital Services, Worldline',
              'Christie H. Kristensen, Partnerships Manager for Open Banking, Danske Bank',
              'Mats Persson Bergius, CEO, Zinova',
              'Rebecca Koskinen, CEO, Stackby Investment Platform',
              'Charles Arvidsson, CEO, AI Nordics']),
      ('h2', 'Partners'),
      ('p', 'Open Payments, Zwapgrid, Danske Bank, Froda, Worldline and Dun &amp; Bradstreet, alongside Solvapay. Read the full <a href="/roi.html">Build Day case study</a> for how the numbers were counted.'),
    ]),
  dict(
    slug='ceo-cfo-breakfast-is-growth-a-judgement-call', status='past',
    title='CEO + CFO Breakfast: Is Growth a Judgement Call?', short='Is Growth a Judgement Call?', luma='https://luma.com/2iyy4xc0',
    cover='/uploads/14/8c71bfb1-3ad3-4b92-b21b-8f13af8331f6.png',
    start='2026-09-04T07:45:00+02:00', end='2026-09-04T09:00:00+02:00',
    date_label='Friday 4 September 2026 · 07:45–09:00', short_date='4 Sep 2026',
    venue_name='Embassy House', street='Medborgarplatsen', postal='',
    venue='Embassy House, Medborgarplatsen, Stockholm',
    hosts=['Alexandra Grisanti', 'Tobias Fridell', 'Vidhi Kumar', 'Sten Krinpus', 'Anders Nilsson'],
    presented='Operator Network, with Cardboard', went=18,
    seo_title='CEO + CFO Breakfast: Is Growth a Judgement Call? | Insider Events',
    meta='A round-table breakfast in Stockholm on how the CEO and CFO relationship actually works, opened by Andreas Hedlund of Gilion and Simon Linderoth of Fairlo.',
    dek='How the CEO and CFO relationship actually works: a breakfast round table for CEOs and CFOs, with sixteen seats.',
    body=[
      ('h2', 'The format'),
      ('p', 'Andreas Hedlund, CFO of Gilion, and Simon Linderoth of Fairlo opened the conversation. From there it was a round table: no panel, no slides, no audience. Everyone at the table had sat in one of the two chairs and had something to say about the other one.'),
      ('h2', 'Run of show'),
      ('ul', ['<b>07:45</b> Breakfast', '<b>08:00–09:00</b> Discussion']),
      ('h2', 'Why it was built this way'),
      ('p', 'The breakfast was hosted with Cardboard, a Norwegian company with no Swedish network, which sat in Stockholm next to Gilion and Fairlo. Co-hosting with brands the room already trusts is how we <a href="/how-alexandra-studio-works.html#new-bank">reach people we don’t know yet</a>.'),
    ]),
  dict(
    slug='payment-layer-build-night', status='past',
    title='The Payment Layer: Build Night by SolvaPay', short='The Payment Layer: Build Night', luma='https://luma.com/akuhm6vq',
    cover='/uploads/v0/66711961-dfbe-4b05-9ef0-ebe0d6c84b13.png',
    start='2026-06-15T17:00:00+02:00', end=None,
    date_label='Monday 15 June 2026 · from 17:00', short_date='15 Jun 2026',
    venue_name="Antler, King's Garden (Kungsträdgården)", street='Jussi Björlings allé', postal='111 47',
    venue="Antler, King's Garden (Kungsträdgården), Jussi Björlings allé, 111 47 Stockholm",
    hosts=['Alexandra Grisanti', 'Viggo Stenseth', 'Laura Halonen'], presented='SolvaPay', went=30,
    seo_title='The Payment Layer: Build Night by SolvaPay, Stockholm | Insider Events',
    meta='A hands-on build night on payments for AI agents at Antler in Kungsträdgården, Stockholm, on 15 June 2026, with Kindly, Zwapgrid and SolvaPay.',
    dek='The second SolvaPay Build Night: demos, a few hours of building and an after-party, on payments for AI agents.',
    body=[
      ('h2', 'What happened'),
      ('p', "The Payment Layer is SolvaPay's build-night series on payments for AI agents. The second night took over Antler's office in Kungsträdgården: short demos to set the scene, then teams formed around the problems and built through the evening."),
      ('h2', 'Agenda'),
      ('ul', ['<b>17:00</b> Welcome and mingle',
              '<b>17:15</b> Kindly: a demo of new MCP functionality',
              '<b>17:25</b> Zwapgrid and SolvaPay demo',
              '<b>17:35</b> SolvaPay',
              'Building groups form, then a dinner break',
              '<b>18:15–20:15</b> Building',
              '<b>20:15</b> Kindly and SolvaPay chat-payment demo, plus a Zwapgrid and SolvaPay demo',
              'Feedback, questions and the after-party']),
      ('h2', 'Who was in the room'),
      ('p', 'Thirty people went: builders and fintech contacts invited by the hosts, with Antler, Zwapgrid and Kindly in the room. Across the Build Night series, AndSend, Open Payments, Visa, Cardboard and Kindly came out as potential customers for SolvaPay. See every event in the <a href="/alexandra-studio-track-record.html">track record</a>.'),
    ]),
  dict(
    slug='cmo-breakfast-trust-is-your-product', status='past',
    title='CMO Breakfast: Trust Is Your Product and Also Your Constraint', short='CMO Breakfast: Trust Is Your Product', luma='https://luma.com/x13z5vhj',
    cover='/uploads/7x/e662797b-ec02-49ca-af0f-267a5a89619f.png',
    start='2026-06-11', end=None,
    date_label='Thursday 11 June 2026', short_date='11 Jun 2026',
    venue_name='Heijbel Growth', street='Bondegatan 21', postal='116 33',
    venue='Heijbel Growth, Bondegatan 21, 116 33 Stockholm',
    hosts=['Alexandra Grisanti', 'Emilia Nygren', 'Lorenzo Alessandri', 'Solveig Rundquist'],
    presented='Operator Network, with Heijbel Growth', went=None, with_text='With Mindler and Natural Cycles',
    seo_title='CMO Breakfast: Trust Is Your Product, Stockholm | Insider Events',
    meta='A breakfast for CMOs at Heijbel Growth in Stockholm on marketing with stakes: speed, trust and staying sane in health tech, with Mindler and Natural Cycles.',
    dek='Marketing with stakes: a breakfast for CMOs on speed, trust and staying sane, hosted at Heijbel Growth.',
    body=[
      ('h2', 'The conversation'),
      ('p', 'The third CMO Breakfast with Heijbel Growth took on marketing where the stakes are personal: health tech, where companies market sensitive decisions such as mental health and fertility, and sell into systems that move slowly, like hospitals, regions and insurers.'),
      ('h2', 'The questions on the table'),
      ('ul', ['When speed and brand consistency collide, what is non-negotiable and what can give a little? Has that line moved in health and wellness compared with other sectors?',
              'How do you set the urgency of a message when the topic itself needs patience and care?',
              'When you sell into hospitals, regions and insurers, is looking too fast or too loud a commercial risk?',
              'What is the one thing marketing owns in your company that no one else could do, and does your leadership know it?']),
      ('h2', 'The series'),
      ('p', 'CMO Breakfasts are a series Alexandra Studio runs with Heijbel Growth: <em>Inspiration, Plot-Twist &amp; Authenticity in Marketing Strategy</em> on 17 February, <em>Enduring Speed while Building Trust</em> on 24 March, and this one on 11 June.'),
    ]),
]

# --------------------------------------------------------------------------
# Shared chrome, taken from index.html so the nav and footer stay identical.
# --------------------------------------------------------------------------
INDEX = (ROOT / 'index.html').read_text(encoding='utf-8')

def rootify(block):
    """Relative links in index.html -> root-relative, so they work from /events/ too."""
    block = re.sub(r'href="(?!https?:|/|#|mailto:)([^"]+)"', r'href="/\1"', block)
    block = block.replace('href="#trending"', 'href="/#trending"').replace('href="#main"', 'href="#main"')
    return block

HEADER = rootify(re.search(r'<header class="hd">.*?</header>', INDEX, re.S).group(0))
HEADER = HEADER.replace('<a href="/insider-events.html">Insider Events</a>',
                        '<a href="/insider-events.html" aria-current="page">Insider Events</a>')
FOOTER = rootify(re.search(r'<footer class="ft">.*?</footer>', INDEX, re.S).group(0))
FONTS = re.search(r'<link href="https://fonts\.googleapis\.com/css2[^>]+>', INDEX).group(0)
FAVICON = re.search(r'<link rel="icon"[^>]+>', INDEX).group(0)

ORG = {"@id": f"{SITE}/#organization"}

def img(path, w):
    return LUMA_IMG.format(w=w, path=path)

ICON_EYE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>'
ICON_CLOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
ICON_TICKET = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'
ARROW = '<svg viewBox="0 0 8 8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" aria-hidden="true"><path d="M1.5 6.5l5-5M2.5 1.5h4v4"/></svg>'
AVATARS = '<span class="avatars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></span>'

def head(title, desc, canonical, og_image, ld, extra=''):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<meta name="theme-color" content="#FAFAF9" />
<script>document.documentElement.classList.add('js')</script>
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}" />
<meta name="author" content="Alexandra Grisanti" />
<meta name="robots" content="index, follow" />
<link rel="canonical" href="{canonical}" />
<meta name="geo.region" content="SE-AB" />
<meta name="geo.placename" content="Stockholm" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Alexandra Studio" />
<meta property="og:title" content="{E(title)}" />
<meta property="og:description" content="{E(desc)}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{og_image}" />
<meta property="og:locale" content="en_SE" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{E(title)}" />
<meta name="twitter:description" content="{E(desc)}" />
<meta name="twitter:image" content="{og_image}" />
{extra}<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>
{FAVICON}
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
{FONTS}
<link rel="preconnect" href="https://images.lumacdn.com" />
<link rel="stylesheet" href="/home.css" />
<link rel="stylesheet" href="/events.css" />
</head>

<body>

<a class="skip" href="#main">Skip to content</a>

{HEADER}
'''

def tail():
    return f'''
{FOOTER}

<script src="/home.js" defer></script>
<script src="/events.js" defer></script>

</body>
</html>
'''

def url(ev):
    return f'/events/{ev["slug"]}.html'

def card_title(ev):
    return ev.get('short') or ev['title']

def countdown_pill(ev):
    if ev.get('start'):
        return (f'<span class="ev-pill" data-countdown data-start="{ev["start"]}"'
                f'{(" data-end=" + chr(34) + ev["end"] + chr(34)) if ev.get("end") else ""} aria-hidden="true">'
                f'{ICON_CLOCK}<span data-out>Counting down</span></span>')
    return f'<span class="ev-pill" aria-hidden="true">{ICON_CLOCK}<span>Date to be announced</span></span>'

def reg_left(ev):
    attrs = ''
    if ev.get('start'): attrs += f' data-start="{ev["start"]}"'
    if ev.get('reg_close'): attrs += f' data-close="{ev["reg_close"]}"'
    return f'<span class="ev-reg" data-regleft{attrs}>{ICON_TICKET}<span data-out>Registration open</span></span>'

def views(ev, mode):
    return (f'<span class="ev-views" data-views data-key="{ev["slug"]}" data-seed="{ev["views"]}" data-mode="{mode}">'
            f'{ICON_EYE}<b>{ev["views"]}</b><span class="sr-only"> views</span></span>')

def went(ev, big=False):
    cls = 'ev-went ev-went-lg' if big else 'ev-went'
    if ev.get('went'):
        return f'<p class="{cls}">{AVATARS}<span><b>{ev["went"]}</b> went</span></p>'
    return f'<p class="{cls}">{AVATARS}<span>{E(ev.get("with_text", "Invite only"))}</span></p>'

def upcoming_card(ev, heading='h3'):
    meta = ev.get('date_label') or 'Stockholm · Date to be announced'
    return f'''        <a class="ev-card" href="{url(ev)}">
          <div class="ev-thumb">
            <img src="{img(ev["cover"], 400)}" alt="Cover image for {E(ev["title"])}" width="800" height="800" loading="lazy" decoding="async" />
            {countdown_pill(ev)}
          </div>
          <div class="ev-body">
            <p class="ev-meta">{E(meta)} · Invite only</p>
            <{heading}>{E(card_title(ev))}</{heading}>
            <div class="ev-row">
              {reg_left(ev)}
              {views(ev, 'get')}
            </div>
          </div>
        </a>'''

def past_card(ev, heading='h3'):
    return f'''        <a class="ev-card ev-past" href="{url(ev)}">
          <div class="ev-thumb">
            <img src="{img(ev["cover"], 400)}" alt="Cover image for {E(ev["title"])}" width="800" height="800" loading="lazy" decoding="async" />
            <span class="ev-tag">Past event</span>
          </div>
          <div class="ev-body">
            <p class="ev-meta">{E(ev["short_date"])} · Stockholm</p>
            <{heading}>{E(card_title(ev))}</{heading}>
            <div class="ev-row">{went(ev)}</div>
          </div>
        </a>'''

UPCOMING = [e for e in EVENTS if e['status'] == 'upcoming']
PAST = [e for e in EVENTS if e['status'] == 'past']

def event_ld(ev):
    loc = {"@type": "Place", "name": ev.get('venue_name') or 'Stockholm',
           "address": {"@type": "PostalAddress", "addressLocality": "Stockholm", "addressCountry": "SE"}}
    if ev.get('street'): loc['address']['streetAddress'] = ev['street']
    if ev.get('postal'): loc['address']['postalCode'] = ev['postal']
    d = {"@type": "Event", "@id": f"{SITE}{url(ev)}#event", "name": ev['title'], "description": ev['meta'],
         "url": f"{SITE}{url(ev)}", "image": [img(ev['cover'], 600)],
         "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
         "location": loc,
         "organizer": [ORG, {"@type": "Organization", "name": ev['presented'].split(',')[0]}]
                      + [{"@type": "Person", "name": h} for h in ev['hosts']],
         "sameAs": ev['luma']}
    if ev.get('start'): d['startDate'] = ev['start']
    if ev.get('end'): d['endDate'] = ev['end']
    return d

# --------------------------------------------------------------------------
# Index page
# --------------------------------------------------------------------------
def build_index():
    title = 'Insider Events: SaaS Executive Network, Stockholm | Alexandra Studio'
    desc = ('Invite-only dinners, demo nights, breakfasts and build days for a SaaS and fintech executive network in Stockholm. '
            'Operator-led growth and investment in Sweden, in the room.')
    canonical = f'{SITE}/insider-events.html'
    graph = [
        {"@type": "CollectionPage", "@id": canonical, "url": canonical, "name": "Insider Events", "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "about": ORG, "inLanguage": "en",
         "mainEntity": {"@type": "ItemList", "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": f"{SITE}{url(e)}", "name": e['title']} for i, e in enumerate(UPCOMING + PAST)]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Alexandra Studio", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Insider Events", "item": canonical}]},
    ] + [event_ld(e) for e in PAST + [u for u in UPCOMING if u.get('start')]]
    ld = {"@context": "https://schema.org", "@graph": graph}
    og = img(UPCOMING[0]['cover'], 600)

    up_cards = '\n'.join(upcoming_card(e) for e in UPCOMING)
    past_cards = '\n'.join(past_card(e) for e in PAST)
    page = head(title, desc, canonical, og, ld) + f'''
<main id="main">

  <section class="ev-hero" aria-labelledby="ev-title">
    <div class="wrap">
      <h1 class="hero-title" id="ev-title">Insider Events</h1>
      <div class="ev-box odo-scope">
        <p class="ev-box-num"><span class="sr-only">{SPRING_COUNT}</span><span class="odo" data-to="{SPRING_COUNT}" aria-hidden="true">{SPRING_COUNT}</span></p>
        <p class="ev-box-copy">Events coming for Spring 2027. Invite only and limited capacity.</p>
      </div>
    </div>
  </section>

  <section class="ev-section" id="upcoming" aria-labelledby="up-title">
    <div class="wrap">
      <div class="ev-head">
        <h2 class="sec-title" id="up-title">Upcoming Events:</h2>
        <p>Request to join on Luma. Every seat is approved by the host.</p>
      </div>
      <div class="ev-grid ev-grid-3">
{up_cards}
      </div>
    </div>
  </section>

  <section class="ev-section" id="previous" aria-labelledby="past-title">
    <div class="wrap">
      <div class="ev-head">
        <h2 class="sec-title" id="past-title">Previous Events:</h2>
        <p>Rooms we have already run in Stockholm in 2026.</p>
      </div>
      <div class="ev-grid ev-grid-4">
{past_cards}
      </div>
    </div>
  </section>

  <section class="ev-section" aria-labelledby="about-title">
    <div class="wrap">
      <div class="ev-about">
        <h2 id="about-title">A SaaS and fintech executive network, in the room.</h2>
        <div>
          <p>Insider Events are the invite-only rooms of the <a href="https://theoperatornetwork.se/" target="_blank" rel="noopener">Operator Network</a>, run by Alexandra Studio: dinners, demo nights, CMO and CFO breakfasts and build days for founders, executives, operators and investors in Stockholm. Every guest list is built by hand and kept small enough for one conversation.</p>
          <p>The thread through all of them is operator-led growth: advice, introductions and investment from people who have built and scaled companies themselves. See every room we have run in the <a href="/alexandra-studio-track-record.html">track record</a>, or read why we choose <a href="/how-alexandra-studio-works.html#compare">rooms over booths</a>.</p>
          <p class="sv" lang="sv">Insider Events är Operator Networks slutna träffar i Stockholm för grundare, chefer och investerare inom SaaS och fintech. Ett exekutivt nätverk kring operator-led growth och investeringar i Sverige: middagar, demokvällar och rundabordssamtal där de som bygger, säljer och investerar sitter vid samma bord.</p>
        </div>
      </div>

      <div class="ev-invite">
        <div>
          <h2>Want a seat at the next one?</h2>
          <p>Events are invite only. Request to join on Luma, or book a call if you want to co-host a room with your buyers in it.</p>
        </div>
        <div class="ev-invite-actions">
          <a class="btn btn-blue" href="https://luma.com/user/stockholmgrowth" target="_blank" rel="noopener">See all events on Luma</a>
          <a class="btn btn-line-white" href="https://calendly.com/alexandra-alexandrastudio/30min" target="_blank" rel="noopener">Co-host a room</a>
        </div>
      </div>
    </div>
  </section>

</main>
''' + tail()
    (ROOT / 'insider-events.html').write_text(page, encoding='utf-8')

# --------------------------------------------------------------------------
# One page per event
# --------------------------------------------------------------------------
def body_html(blocks):
    out = []
    for kind, val in blocks:
        if kind == 'h2': out.append(f'          <h2>{E(val)}</h2>')
        elif kind == 'p': out.append(f'          <p>{val}</p>')
        elif kind == 'p_sv': out.append(f'          <p lang="sv">{val}</p>')
        elif kind == 'ul': out.append('          <ul>\n' + '\n'.join(f'            <li>{li}</li>' for li in val) + '\n          </ul>')
    return '\n'.join(out)

def build_event(ev):
    canonical = f'{SITE}{url(ev)}'
    upcoming = ev['status'] == 'upcoming'
    graph = [event_ld(ev) if (ev.get('start') or not upcoming) else
             {"@type": "WebPage", "@id": canonical, "url": canonical, "name": ev['title'], "description": ev['meta'],
              "about": {"@type": "Thing", "name": ev['title']}, "isPartOf": {"@id": f"{SITE}/#website"}},
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Alexandra Studio", "item": f"{SITE}/"},
                 {"@type": "ListItem", "position": 2, "name": "Insider Events", "item": f"{SITE}/insider-events.html"},
                 {"@type": "ListItem", "position": 3, "name": ev['title'], "item": canonical}]}]
    ld = {"@context": "https://schema.org", "@graph": graph}

    when = ev.get('date_label') or 'Date to be announced. Approved guests are told first.'
    facts = [('When', E(when)), ('Where', E(ev['venue'])), ('Hosts', E(', '.join(ev['hosts']))),
             ('Presented by', E(ev['presented'])), ('Format', 'Invite only. Every seat is approved by the host.')]
    facts_html = '\n'.join(f'            <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in facts)

    if upcoming:
        if ev.get('start'):
            end_attr = f' data-end="{ev["end"]}"' if ev.get('end') else ''
            count = f'''          <div class="ep-count" data-countdown data-full data-start="{ev["start"]}"{end_attr} role="timer" aria-label="Time until the event">
            <div><b data-d>–</b><span>Days</span></div>
            <div><b data-h>–</b><span>Hours</span></div>
            <div><b data-m>–</b><span>Min</span></div>
            <div><b data-s>–</b><span>Sec</span></div>
          </div>'''
        else:
            count = '          <p class="ep-tba">Date to be announced</p>'
        aside = f'''{count}
          <div class="ev-row">
            {reg_left(ev)}
            {views(ev, 'hit')}
          </div>
          <a class="btn btn-black" href="{ev["luma"]}" target="_blank" rel="noopener">Request to join on Luma {ARROW}</a>
          <p class="ep-note">Invite only and limited capacity. The host approves every request.</p>'''
        kicker = '<p class="ep-kicker"><span class="dot"></span>Upcoming · Invite only</p>'
    else:
        aside = f'''          {went(ev, big=True)}
          <a class="btn btn-line" href="{ev["luma"]}" target="_blank" rel="noopener">See the event on Luma {ARROW}</a>
          <a class="btn btn-black" href="/insider-events.html#upcoming">See upcoming events</a>'''
        kicker = f'<p class="ep-kicker past"><span class="dot"></span>Past event · {E(ev["short_date"])}</p>'

    mobile_cta = (f'\n        <a class="btn btn-black ep-mobile-cta" href="{ev["luma"]}" target="_blank" rel="noopener">Request to join on Luma {ARROW}</a>'
                  if upcoming else '')
    more = [e for e in UPCOMING if e is not ev][:3]
    more_html = '\n'.join(upcoming_card(e) for e in more)

    page = head(ev['seo_title'], ev['meta'], canonical, img(ev['cover'], 600), ld) + f'''
<main id="main" class="ep">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/insider-events.html">Insider Events</a><span aria-hidden="true">/</span><span>{E(card_title(ev))}</span></nav>

    <div class="ep-grid">
      <article class="ep-article">
        {kicker}
        <h1 class="ep-title">{E(ev["title"])}</h1>
        <p class="ep-dek">{E(ev["dek"])}</p>
        <dl class="ep-facts">
{facts_html}
        </dl>{mobile_cta}
        <div class="ep-body">
{body_html(ev["body"])}
        </div>
      </article>

      <aside class="ep-aside" aria-label="Event details">
        <div class="ep-card">
          <div class="ev-thumb"><img src="{img(ev["cover"], 600)}" alt="Cover image for {E(ev["title"])}" width="1200" height="1200" fetchpriority="high" decoding="async" /></div>
{aside}
        </div>
      </aside>
    </div>

    <section class="ev-section" aria-labelledby="more-title">
      <div class="ev-head">
        <h2 class="sec-title" id="more-title">More Insider Events:</h2>
        <p><a href="/insider-events.html#previous">See previous events</a></p>
      </div>
      <div class="ev-grid ev-grid-3">
{more_html}
      </div>
    </section>
  </div>
</main>
''' + tail()
    out = ROOT / 'events' / f'{ev["slug"]}.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')

if __name__ == '__main__':
    build_index()
    for ev in EVENTS:
        build_event(ev)
    print('built insider-events.html and', len(EVENTS), 'event pages')
