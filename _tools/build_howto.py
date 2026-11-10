#!/usr/bin/env python3
"""Builds how-to.html (Figma "How to Hyper Grow."), the page behind "How-to" in the nav:
the video box, Start Now, the three growth packages with prices, and how growth is measured.

  cd _tools && python3 build_howto.py

Reuses the homepage's video box (.growth) and numbered-list section (.calls) from home.css.
"""
from site_chrome import ROOT, SITE, E, head, header, tail

PATH = '/how-to.html'
CALENDLY = 'https://calendly.com/alexandra-alexandrastudio/30min'

ICONS = {  # 24px line icons: cable, earth, chart
    'cable': '<path d="M7 3v4M11 3v4M5 7h8v3a4 4 0 0 1-8 0V7ZM9 14v2a4 4 0 0 0 4 4h2a4 4 0 0 0 4-4V4"/>',
    'earth': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    'chart': '<path d="M2 18l6-6 4 4 9-9"/><path d="M15 7h6v6"/>',
}

PACKAGES = [
    dict(key='visibility', icon='cable', img='/img/home/card-1.webp', w=556, h=668,
         title='Market Visibility',
         text='Host a series of network events: your logo, your concepts. We work with you to co-host these events, '
              'reducing event costs and increasing visibility.',
         get=['Viral organic content', 'Newsletter coverage', 'In-person meetings with your target customer', 'Stage time'],
         price='100K SEK for a three-part series over six months.', amount=100000, unit=None),
    dict(key='pay-per-lead', icon='earth', img='/img/home/card-2.webp', w=544, h=666,
         title='Pay per Lead Package',
         text='Pay only for meetings booked: we book meetings and get you warm, relevant leads. 30 warm leads and '
              '5 meetings a month with a targeted list, or you don’t pay. Requires an ICP list of at least 200 '
              'companies for this price; shorter ICP lists increase the price.',
         get=['SEO content to attract leads', 'Lead magnets', 'Lists of potentials',
              'Booked meetings and podcasts with your target customer'],
         price='55K SEK per month.', amount=55000, unit='MON'),
    dict(key='hyper-growth', icon='chart', img='/img/home/card-3.webp', w=554, h=668,
         title='Hyper Growth Package.',
         text='Get the entire growth package: newsletter, podcast and a content system in a loop, plus events. '
              'Hyper grow your own audience and platform in 3 months. We build the structures, make it easy to '
              'run, and you own 100% of it.',
         get=['Your own newsletter', 'Your own podcast series with guests', 'Automated high-engagement content sequences',
              'Booked meetings and podcasts with potential distribution partners'],
         price='300K SEK and requires 3 months.', amount=300000, unit=None),
]

def svg(name):
    return (f'<svg class="ht-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

def numbered(items):
    return '<ol class="calls-list">' + ''.join(
        f'<li><span class="n">{i:02d}</span><p>{t}</p></li>' for i, t in enumerate(items, 1)) + '</ol>'

def build():
    title = 'How to Hyper Grow: Fintech Growth Packages and Pricing | Alexandra Studio'
    desc = ('How to hyper grow a B2B fintech: three growth packages from Alexandra Studio. Market Visibility '
            '(100K SEK), Pay per Lead (55K SEK a month) and the Hyper Growth Package (300K SEK), measured in '
            'booked meetings, not impressions.')
    offers = []
    for p in PACKAGES:
        price = {"@type": "UnitPriceSpecification", "price": str(p['amount']), "priceCurrency": "SEK",
                 **({"unitCode": p['unit']} if p['unit'] else {})}
        offers.append({"@type": "Offer", "name": p['title'].rstrip('.'), "description": p['text'],
                       "priceSpecification": price, "url": SITE + PATH + '#' + p['key']})
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": SITE + PATH, "url": SITE + PATH, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "about": {"@id": f"{SITE}/#organization"}, "inLanguage": "en"},
        {"@type": "Service", "name": "Fintech growth packages", "provider": {"@id": f"{SITE}/#organization"},
         "areaServed": "Nordics", "audience": {"@type": "BusinessAudience", "audienceType": "B2B fintech companies"},
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Growth packages", "itemListElement": offers}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Alexandra Studio", "item": SITE + '/'},
            {"@type": "ListItem", "position": 2, "name": "How to Hyper Grow", "item": SITE + PATH}]}]}

    pkgs = ''.join(f'''
          <article class="ht-pkg" id="{p['key']}">
            <img class="ht-card" src="{p['img']}" alt="" width="{p['w']}" height="{p['h']}" loading="lazy" decoding="async" />
            <div class="ht-pkg-body">
              {svg(p['icon'])}
              <h3>{E(p['title'])}</h3>
              <p>{E(p['text'])}</p>
              <p class="ht-get">You get:</p>
              <ul>{''.join(f'<li>{E(x)}</li>' for x in p['get'])}</ul>
              <p class="ht-price">{E(p['price'])}</p>
            </div>
          </article>''' for p in PACKAGES)

    page = head(title, desc, PATH, ld, css=('/howto.css',)) + header('/how-to.html') + f'''
<main id="main" class="ht-page">

  <section class="ht-hero" aria-labelledby="ht-title">
    <div class="wrap"><h1 class="ht-title" id="ht-title">How to Hyper Grow.</h1></div>
  </section>

  <section class="growth ht-growth" aria-labelledby="growth-title">
    <div class="growth-wrap">
      <div class="growth-box">
        <div class="growth-video" data-yt="kiv24h_9Rbc" data-start="0" aria-hidden="true"></div>
        <div class="growth-shade" aria-hidden="true"></div>
        <div class="growth-body">
          <h2 id="growth-title">A growth team that understands B2B Fintech</h2>
          <div class="growth-row"><p>For exceptional teams ready to scale</p></div>
        </div>
      </div>
    </div>
  </section>

  <section class="ht-start" aria-labelledby="start-title">
    <div class="wrap"><h2 class="ht-h2 ht-center" id="start-title">Start Now.</h2></div>
  </section>

  <section class="calls ht-calls" aria-labelledby="rank-title">
    <div class="wrap calls-grid">
      <div class="calls-text">
        <h2 class="calls-title" id="rank-title">Start Ranking &amp; Attending our Events</h2>
        <p class="calls-lead">We talk with a range of fintechs in all geographies. Although we are Nordic focused and based here in Stockholm, we believe in connecting the world fintech ecosystem.</p>
        {numbered(['Join Our Podcast', 'Apply to Join one of our Dinners or Panels', 'Meet us at a Fintech Conference', 'Don’t be a stranger'])}
        <a class="btn btn-green" href="/fintech-awards.html#earn">Learn More</a>
      </div>
      <figure class="calls-media">
        <img src="/img/home/podium.webp" alt="" width="1180" height="1422" loading="lazy" decoding="async" />
      </figure>
    </div>
  </section>

  <section class="ht-packages" aria-labelledby="packages-title">
    <div class="wrap">
      <h2 class="ht-h2" id="packages-title">When you’re serious about Growth.</h2>
      <p class="ht-sub">We Offer Three Growth Packages.</p>
      <p class="ht-lead">Our growth packages are tailored to our clients’ needs, always ICP focused, so your buyer is engaging with you, showing up, talking with you and getting into your network.</p>
      <div class="ht-pkgs">{pkgs}
      </div>
    </div>
  </section>

  <section class="calls ht-calls" aria-labelledby="measure-title">
    <div class="wrap calls-grid">
      <div class="calls-text">
        <h2 class="calls-title" id="measure-title">Is 2027 your Year of Hyper Growth?</h2>
        <p class="calls-lead">Marketing shouldn’t only cost you money. Marketing must make you money. Do you want to know how we measure that?</p>
        {numbered(['Number of Booked Meetings', 'Potential Customers Attending Your Events, in-person', 'Podcasts and Content articles with Potential Customers', 'Organic Reach through LinkedIn Content, measured by Companies and Decision Makers reached'])}
        <a class="btn btn-green" href="/roi.html">See How We Measure</a>
      </div>
      <figure class="calls-media ht-cutout">
        <img src="/img/home/people-4.webp" alt="" loading="lazy" decoding="async" />
      </figure>
    </div>
  </section>

</main>
''' + tail()
    (ROOT / 'how-to.html').write_text(page, encoding='utf-8')
    print('built how-to.html')

if __name__ == '__main__':
    build()
