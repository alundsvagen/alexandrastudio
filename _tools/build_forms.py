#!/usr/bin/env python3
"""Builds fintech-list.html: Download a list, Add a company, Remove your company.

Each section embeds a Fillout form. Paste each form's ID below (in Fillout: Share >
Embed > Standard, the value of data-fillout-id) and run:

  cd _tools && python3 build_forms.py

A section without an ID shows a placeholder with a link to book a call.
"""
from site_chrome import ROOT, SITE, E, head, header, tail
from build_database import TOTAL, CONTACT_URL, fmt

FORMS = {
    'download': '43UzY2iF8Aus',   # Download a list of 100 (300 SEK)  https://form.fillout.com/t/43UzY2iF8Aus
    'add': '3Yj2TmqfNmus',        # Add a company                      https://form.fillout.com/t/3Yj2TmqfNmus
    'remove': '3AJ3FT4KJ3us',     # Remove your company                https://form.fillout.com/t/3AJ3FT4KJ3us
}
FILLOUT_JS = 'https://server.fillout.com/embed/v1/'
PATH = '/fintech-list.html'

SECTIONS = [
    ('download', 'h1', 'Download A List',
     'Our lists cost 300 SEK (for admin and agents) and you get 100 companies that include their Name, URL, '
     'Description and Location.', 'fl-lead fl-wide'),
    ('add', 'h2', 'Add a Company',
     'You’re in good company, welcome to our network. Glad you found our site and we’re glad to have you on the list.',
     'fl-lead'),
    ('remove', 'h2', 'Remove your Company',
     'We require that you give a company email address linked to the company’s domain address so we can confirm '
     'the validity of the request.', 'fl-lead'),
]

def form_html(key, title):
    fid = FORMS.get(key, '').strip()
    if fid:
        # Fillout's standard embed: the container needs a height, which dynamic-resize then adjusts
        return (f'<div class="fl-form fl-live" data-fillout-id="{E(fid)}" data-fillout-embed-type="standard" '
                f'style="width:100%;height:500px;" data-fillout-inherit-parameters data-fillout-dynamic-resize></div>'
                f'<noscript><p class="fl-noscript"><a href="https://form.fillout.com/t/{E(fid)}">Open the {E(title.lower())} form</a></p></noscript>')
    return (f'<div class="fl-form fl-soon"><p>The {E(title.lower())} form opens here soon.</p>'
            f'<a class="btn-glass" href="{CONTACT_URL}" target="_blank" rel="noopener">Book a 15-minute call instead</a></div>')

def build():
    title = 'Download a Fintech Company List, Add or Remove Your Company | Alexandra Studio'
    desc = (f'Download a list of 100 fintech companies that match your ICP for 300 SEK, with name, URL, description and '
            f'location, or add or remove your company in our database of {fmt(TOTAL)} European fintechs.')
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": SITE + PATH, "url": SITE + PATH, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"}, "inLanguage": "en"},
        {"@type": "Product", "name": "List of 100 fintech companies matching your ICP",
         "description": "100 fintech companies from the Alexandra Studio database, with name, URL, description and location.",
         "brand": {"@id": f"{SITE}/#organization"},
         "offers": {"@type": "Offer", "price": "300", "priceCurrency": "SEK", "url": SITE + PATH + '#download',
                    "availability": "https://schema.org/InStock"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Alexandra Studio", "item": SITE + '/'},
            {"@type": "ListItem", "position": 2, "name": "Fintech database", "item": SITE + '/trending.html'},
            {"@type": "ListItem", "position": 3, "name": "Download a list", "item": SITE + PATH}]}]}
    secs = ''.join(f'''
  <section class="fl-sec" id="{key}" aria-labelledby="{key}-title">
    <div class="wrap">
      <{tag} class="fl-title{' fl-h1' if tag == 'h1' else ''}" id="{key}-title">{E(t)}</{tag}>
      <p class="{cls}">{E(lead)}</p>
      {form_html(key, t)}
    </div>
  </section>''' for key, tag, t, lead, cls in SECTIONS)
    scripts = (FILLOUT_JS,) if any(v.strip() for v in FORMS.values()) else ()
    page = head(title, desc, PATH, ld, css=('/forms.css',)) + header() + f'''
<main id="main" class="fl-page">{secs}
  <p class="fl-back wrap"><a href="/trending.html">Back to the fintech database</a></p>
</main>
''' + tail(scripts)
    (ROOT / 'fintech-list.html').write_text(page, encoding='utf-8')
    print('built fintech-list.html; forms embedded:', ', '.join(k for k, v in FORMS.items() if v.strip()) or 'none yet')

if __name__ == '__main__':
    build()
