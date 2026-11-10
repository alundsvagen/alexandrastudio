"""Shared <head>, nav and footer for generated pages, taken from index.html so
every page stays identical to the homepage. Used by build_database.py."""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://alexandrastudio.se'
E = html.escape

INDEX = (ROOT / 'index.html').read_text(encoding='utf-8')


def _rootify(block):
    """Relative links in index.html -> root-relative so they work in sub-folders."""
    return re.sub(r'href="(?!https?:|/|#|mailto:)([^"]+)"', r'href="/\1"', block)


HEADER = _rootify(re.search(r'<header class="hd">.*?</header>', INDEX, re.S).group(0))
FOOTER = _rootify(re.search(r'<footer class="ft">.*?</footer>', INDEX, re.S).group(0))
FONTS = re.search(r'<link href="https://fonts\.googleapis\.com/css2[^>]+>', INDEX).group(0)
FAVICON = re.search(r'<link rel="icon"[^>]+>', INDEX).group(0)
OG_DEFAULT = 'https://res.cloudinary.com/dxhph3qls/image/upload/v1784193454/Thumbnail_Image_zmvex6.png'


def header(current=None):
    h = HEADER
    if current:
        h = h.replace(f'<a href="{current}">', f'<a href="{current}" aria-current="page">', 1)
    return h


def head(title, desc, path, ld, css=(), og_image=OG_DEFAULT, preconnect=()):
    canonical = SITE + path
    links = '\n'.join(f'<link rel="stylesheet" href="{c}" />' for c in ('/home.css',) + tuple(css))
    pre = '\n'.join(f'<link rel="preconnect" href="{p}" />' for p in preconnect)
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
<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>
{FAVICON}
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
{FONTS}
{pre}
{links}
</head>

<body>

<a class="skip" href="#main">Skip to content</a>

'''


def tail(scripts=()):
    s = '\n'.join(f'<script src="{x}" defer></script>' for x in ('/home.js',) + tuple(scripts))
    return f'''
{FOOTER}

{s}

</body>
</html>
'''
