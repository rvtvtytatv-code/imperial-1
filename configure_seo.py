from pathlib import Path
from urllib.parse import urlsplit
from html import escape
import sys
if len(sys.argv) != 2:
    raise SystemExit("Usage: python configure_seo.py https://YOUR-DOMAIN")
base = sys.argv[1].rstrip('/')
u = urlsplit(base)
if u.scheme not in ('http','https') or not u.hostname or u.path or u.query or u.fragment or u.username or u.password:
    raise SystemExit("Provide the real site origin, e.g. https://your-domain.com")
root = Path(__file__).resolve().parent
pages = {'home': {'en': ('index.html', base+'/'), 'ru': ('ru.html', base+'/ru.html')}, 'guide': {'en': ('poker-guide.html', base+'/poker-guide.html'), 'ru': ('poker-rules-ru.html', base+'/poker-rules-ru.html')}}
all_urls = [url for pair in pages.values() for _, url in pair.values()]
for group, lang, file in [(g, l, f) for g, pair in pages.items() for l, (f, _) in pair.items()]:
    urls = {code: url for code, (_, url) in pages[group].items()}
    p = root/file
    s = p.read_text(encoding='utf-8')
    import re
    s = re.sub(r'<!-- SEO URLs START -->.*?<!-- SEO URLs END -->', '', s, flags=re.S)
    e = escape
    tags = [f'<link rel="canonical" href="{e(urls[lang])}">']
    tags += [f'<link rel="alternate" hreflang="{code}" href="{e(urls[code])}">' for code in ('en','ru')]
    tags += [f'<link rel="alternate" hreflang="x-default" href="{e(urls["en"])}">']
    tags += [f'<meta property="og:url" content="{e(urls[lang])}">',f'<meta property="og:image" content="{e(base)}/og-image.jpg">','<meta property="og:image:width" content="1200">','<meta property="og:image:height" content="630">',f'<meta name="twitter:image" content="{e(base)}/og-image.jpg">']
    s = s.replace('</head>', '<!-- SEO URLs START -->\n'+'\n'.join(tags)+'\n<!-- SEO URLs END -->\n</head>',1)
    p.write_text(s, encoding='utf-8')
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{escape(url)}</loc></url>\n' for url in all_urls) + '</urlset>\n'
(root/'sitemap.xml').write_text(xml, encoding='utf-8')
(root/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+base+'/sitemap.xml\n', encoding='utf-8')
print('SEO URLs and sitemap configured.')
