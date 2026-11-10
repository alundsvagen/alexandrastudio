#!/usr/bin/env python3
"""Builds contact.html (Figma "Contact us."): company details, LinkedIn and booking,
then the founder section and Trending Topics + Podcast, which moved here from the homepage.

  cd _tools && python3 build_contact.py

The two moved sections live in _tools/partials/contact-sections.html.
"""
from site_chrome import ROOT, SITE, head, header, tail

PATH = '/contact.html'
CALENDLY = 'https://calendly.com/alexandra-alexandrastudio/30min'
LINKEDIN = 'https://www.linkedin.com/in/alexandragrisanti/'
ARROW = ('<svg viewBox="0 0 8 8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" '
         'aria-hidden="true"><path d="M1.5 6.5l5-5M2.5 1.5h4v4"/></svg>')

def build():
    title = 'Contact Alexandra Studio: Book a Meeting | B2B Growth Marketing for Fintechs, Stockholm'
    desc = ('Contact Alexandra Studio, B2B growth marketing for fintechs in Stockholm, Sweden. '
            'Book a meeting or connect with Alexandra Grisanti on LinkedIn.')
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ContactPage", "@id": SITE + PATH, "url": SITE + PATH, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "about": {"@id": f"{SITE}/#organization"},
         "mainEntity": {"@id": f"{SITE}/#organization"}, "inLanguage": "en"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Alexandra Studio", "item": SITE + '/'},
            {"@type": "ListItem", "position": 2, "name": "Contact us", "item": SITE + PATH}]}]}
    moved = (ROOT / '_tools' / 'partials' / 'contact-sections.html').read_text(encoding='utf-8')
    # on this page the founder section comes first, then Trending Topics + Podcast
    split = moved.index('  <!-- About Alexandra -->')
    topics, about = moved[:split], moved[split:]
    page = head(title, desc, PATH, ld, css=('/contact.css',),
                og_image='https://res.cloudinary.com/dxhph3qls/image/upload/v1788176088/ANS00799_1_lxwsnw.png') \
        + header('/contact.html') + f'''
<main id="main" class="ct-page">

  <section class="ct-hero" aria-labelledby="ct-title">
    <div class="wrap">
      <h1 class="ct-title" id="ct-title">Contact us.</h1>
      <address class="ct-details">
        <b>Alexandra Studio</b><br>
        B2B growth marketing for fintechs.<br>
        Stockholm, Sweden.<br>
        A. Grisanti Ventures · VAT SE930825284101<br>
        Approved for F-skatt.<br>
        <span class="ct-copy">© 2026 Alexandra Studio. All rights reserved.</span>
      </address>
      <p class="ct-ask">Connect on LinkedIn or book a meeting.</p>
      <div class="ct-actions">
        <a class="btn btn-black" href="{CALENDLY}" target="_blank" rel="noopener">Book a meeting {ARROW}</a>
        <a class="btn ct-outline" href="{LINKEDIN}" target="_blank" rel="noopener">Connect on LinkedIn {ARROW}</a>
      </div>
    </div>
  </section>

{about}
{topics}
</main>
''' + tail()
    (ROOT / 'contact.html').write_text(page, encoding='utf-8')
    print('built contact.html')

if __name__ == '__main__':
    build()
