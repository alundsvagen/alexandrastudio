#!/usr/bin/env python3
"""Builds fintech-go-to-market.html, the page behind the "Learn More" button:
results first (big counters), then Build Your Audience pricing (Premium and
Feature packages), then the pick-what-you-need items on a black panel.

  cd _tools && python3 build_gtm.py

Styles: /gtm.css on top of /home.css. The counters use the odometer in home.js
(data-sep adds thousands separators). Prices come from pricing.py.
"""
from site_chrome import ROOT, SITE, E, head, header, tail
from pricing import PACKAGES, SINGLE_ITEMS, SINGLE_PRICE, num, sek, offers as price_offers

PATH = '/fintech-go-to-market.html'
CALENDLY = 'https://calendly.com/alexandra-alexandrastudio/30min'
ARROW = ('<svg viewBox="0 0 8 8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" '
         'aria-hidden="true"><path d="M1.5 6.5l5-5M2.5 1.5h4v4"/></svg>')

# (number, unit, caption). Numbers count up on scroll.
STATS = [
    (1200, '', 'Subscribers in Fintech Thought Leadership.'),
    (600, '', 'Subscribers in Marketing and Sales Thought Leadership.'),
    (650000, 'SEK', 'Revenue Earned.'),
    (12, '', 'Agentic Employees on our team.'),
]

# icons for the single items, in the order of pricing.SINGLE_ITEMS
ICONS = [
    '<path d="M12 2.5a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0v-6a3 3 0 0 0-3-3z"/><path d="M5.5 10.5a6.5 6.5 0 0 0 13 0M12 17v4.5M8.5 21.5h7"/>',
    '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/>',
    '<path d="M12 19.5l7-7 2.5 2.5-7 7z"/><path d="M18 13.5l-1.5-7.5L2.5 2.5l3.5 14 7.5 1.5z"/><path d="M2.5 2.5l7.6 7.6"/><circle cx="11.5" cy="11.5" r="2"/>',
]


def fmt(n):
    return num(n)


def stat(n, unit, caption):
    shown = '+' + fmt(n) + (' ' + unit if unit else '')
    sep = ' data-sep="\u00a0"' if n >= 1000 else ''
    unit_html = f'<span class="pct gt-unit" aria-hidden="true">{unit}</span>' if unit else ''
    return (f'        <div class="stat">\n'
            f'          <p class="stat-num"><span class="sr-only">{E(shown)}</span>'
            f'<span class="gt-plus" aria-hidden="true">+</span>'
            f'<span class="odo" data-to="{n}"{sep} aria-hidden="true">{fmt(n)}</span>{unit_html}</p>\n'
            f'          <p class="stat-copy">{E(caption)}</p>\n'
            f'        </div>')


def package(p):
    items = ''.join(f'<li>{E(i)}</li>' for i in p['items'])
    items = f'\n          <ul class="gt-list">{items}</ul>' if items else ''
    lead = f'\n          <p class="gt-plan-lead">{E(p["lead"])}</p>' if p['lead'] else ''
    return f'''      <article class="gt-plan gt-plan-{p['id']}" id="{p['id']}" aria-labelledby="{p['id']}-title">
        <div class="gt-plan-top">
          <p class="gt-kicker">{E(p['name'])}</p>
          <h3 class="gt-plan-title" id="{p['id']}-title">{E(p['title'])}</h3>{lead}{items}
        </div>
        <div class="gt-plan-foot">
          <p class="gt-price"><b>{sek(p['price'])}</b> <span>a month</span></p>
          <a class="btn btn-black" href="{CALENDLY}" target="_blank" rel="noopener">Book a meeting {ARROW}</a>
        </div>
      </article>'''


def build():
    title = 'Build Your Audience: Results and Pricing | Alexandra Studio'
    desc = ('Build your audience with Alexandra Studio: the Premium Package at ' + sek(PACKAGES[0]['price']) +
            ' a month for IRL brand association visibility, or the Feature Package at ' + sek(PACKAGES[1]['price']) +
            ' a month to start your own newsletter and podcast. Single items are priced on request per client.')
    offers = price_offers(SITE)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": SITE + PATH + '#webpage', "url": SITE + PATH, "name": title,
         "description": desc, "isPartOf": {"@id": f"{SITE}/#website"}, "about": {"@id": SITE + PATH + '#service'},
         "inLanguage": "en"},
        {"@type": "Service", "@id": SITE + PATH + '#service', "name": "Build Your Audience",
         "serviceType": "B2B audience building", "url": SITE + PATH,
         "provider": {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "Alexandra Studio",
                      "url": SITE + '/'},
         "areaServed": [{"@type": "City", "name": "Stockholm"}, {"@type": "Place", "name": "Europe"}],
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Build Your Audience packages",
                             "itemListElement": offers}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Alexandra Studio", "item": SITE + '/'},
            {"@type": "ListItem", "position": 2, "name": "Build Your Audience", "item": SITE + PATH}]}]}

    stats = '\n'.join(stat(*s) for s in STATS)
    plans = '\n'.join(package(p) for p in PACKAGES)
    items = '\n'.join(
        f'        <li class="gt-item"><span class="gt-circle"><svg viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{icon}</svg></span><p>{E(text)}</p></li>' for text, icon in zip(SINGLE_ITEMS, ICONS))

    page = head(title, desc, PATH, ld, css=('/gtm.css',)) + header() + f'''
<main id="main" class="gt-page">

  <section class="gt-hero" aria-labelledby="gt-title">
    <div class="wrap">
      <h1 class="gt-title" id="gt-title">Build Your Audience.</h1>
    </div>
  </section>

  <section class="research gt-results" id="results" aria-label="Our results">
    <div class="wrap research-grid">
      <p class="research-lead">We built our own audience first. Now we build yours: we do the hard parts, you show up and be the host.</p>

      <div class="stats gt-stats">
{stats}
      </div>
    </div>
  </section>

  <section class="gt-pricing" id="pricing" aria-labelledby="pricing-title">
    <div class="wrap">
      <h2 class="gt-h2" id="pricing-title">Build Your Audience Pricing.</h2>
      <div class="gt-plans">
{plans}
      </div>
    </div>
  </section>

  <section class="gt-pick" id="items" aria-labelledby="items-title">
    <div class="wrap">
      <div class="gt-pick-box">
        <h2 class="gt-pick-title" id="items-title">Or just the items you need.</h2>
        <ul class="gt-items">
{items}
        </ul>
        <p class="gt-pick-price">{E(SINGLE_PRICE)}</p>
        <a class="btn gt-btn-white" href="/contact.html">Contact us {ARROW}</a>
      </div>
    </div>
  </section>

</main>
''' + tail()
    (ROOT / 'fintech-go-to-market.html').write_text(page, encoding='utf-8')
    print('built fintech-go-to-market.html')


if __name__ == '__main__':
    build()
