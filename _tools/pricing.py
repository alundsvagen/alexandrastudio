"""Alexandra Studio pricing: the one place prices live. Every page generator reads
from here (build_gtm, build_howto, build_events, build_guides); hand-written pages
were updated to the same wording. Prices are written the Swedish way, 95 787 SEK,
with non-breaking spaces so a price never breaks across lines."""

PRICING_URL = '/fintech-go-to-market.html#pricing'
NBSP = ' '


def num(n):
    """95787 -> '95 787' (Swedish digit grouping, non-breaking spaces)."""
    return f'{n:,}'.replace(',', NBSP)


def sek(n):
    return num(n) + NBSP + 'SEK'


PREMIUM = dict(
    id='premium', name='Premium Package', title='IRL Brand Association Visibility', price=95787,
    lead='',
    items=['Special invites to exclusive network events',
           'VC magazine feature',
           'Three hosted podcasts with stars in your industry per month',
           'Hosting parties with other brands, plus a waitlist',
           'Team photoshoots and process documentation'])

FEATURE = dict(
    id='feature', name='Feature Package',
    title='Get hands-on help to start your own Newsletter, Podcast and Grow your Audience.', price=76120,
    lead='We do the hard parts, you show up and be the host.', items=[])

PACKAGES = [PREMIUM, FEATURE]

SINGLE_ITEMS = ['You’re featured on our podcast.', 'We match you with an ICP.', 'Brand work or Design Help.']
SINGLE_PRICE = 'Priced on request per client.'

# one sentence for FAQs, guides and llms.txt
SUMMARY = (f'The Premium Package (IRL brand association visibility) is {sek(PREMIUM["price"])} a month, '
           f'the Feature Package (hands-on help to start your own newsletter and podcast) is '
           f'{sek(FEATURE["price"])} a month, and single items such as a feature on our podcast, ICP matching '
           f'or brand and design help are priced on request per client.')

PRICE_RANGE = f'{num(FEATURE["price"])}–{sek(PREMIUM["price"])} a month'


def offers(site):
    """schema.org Offers for the two packages."""
    return [{"@type": "Offer", "name": f'{p["name"]}: {p["title"].rstrip(".")}',
             "priceSpecification": {"@type": "UnitPriceSpecification", "price": str(p['price']),
                                    "priceCurrency": "SEK", "unitText": "MONTH"},
             "url": f'{site}/fintech-go-to-market.html#{p["id"]}'} for p in PACKAGES]
