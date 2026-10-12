import urllib.parse
"""Генератор статичного сайту GREENODIN з catalog.json (дизайн — макети замовника)."""
import json, re, os, shutil, glob, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.environ.get('GREENODIN_OUT', os.path.join(REPO, 'public'))
BUILD = os.path.join(HERE, 'build'); os.makedirs(BUILD, exist_ok=True)
CAT = json.load(open(os.path.join(HERE, 'data', 'catalog.json'), encoding='utf-8'))
GI = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'group_intro.json'), encoding='utf-8'))
GB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grow_blocks.json'), encoding='utf-8'))
import textclean; textclean.walk(CAT['products'])
LOCAL = json.load(open(os.path.join(HERE, 'data', 'local_imgs.json'), encoding='utf-8'))
ZIPDIR = glob.glob(os.path.join(HERE, 'data', 'zipx', '*/'))[0]
E = lambda s: html.escape(str(s or ''), quote=True)

# ---------- дані ----------
SECTIONS = CAT['sections']
SEC = {s['id']: s for s in SECTIONS}
GROUPS = CAT['groups']
GRP = {g['id']: g for g in GROUPS}
PRODUCTS = [p for p in CAT['products'] if p['kind'] != 'crop_guide']
FIELDS = [p for p in CAT['products'] if p['kind'] == 'crop_guide']
LINES = {p['series']: p for p in PRODUCTS if p['kind'] == 'line'}
SH = CAT['shared']
COLOR = {'gray': '#5f7266', 'brown': '#6b4a2f', 'black': '#000', 'white': '#9fb0a5', 'red': '#a8362b',
         'melior': '#2f9e4f', 'multihumate': '#2f9e4f', 'microbox': '#2f9e4f'}
SERIES_NAME = lambda s: 'GREENODIN ' + s.upper()
LINE_ORDER = ['white', 'gray', 'brown', 'black', 'red', 'melior', 'multihumate', 'microbox']
LOCAL['495'] = ['_Товарів_Тюльпаны-350x350.jpg.webp']
GROUP_IMG = {'zernovi': 'fertilizers-for-cereals-photo-200x200.jpg.webp',
             'zernobobovi': 'udobreniya-dlya-zernobobovyh-kultur-200x200.jpg.webp',
             'tehnichni': 'udobreniya-dlya-tehnicheskih-kultur-200x200.jpg.webp'}
FIELD_IMG = {'dobryva-dlya-konopli-greenodin': 'udobrenie-dlya-konopli-foto-200x200.jpg.webp'}

def page_of(p):
    return ('k/' if p['kind'] == 'crop_guide' else 'p/') + p['slug'] + '.html'

# ---------- зображення ----------
os.makedirs(OUT + '/img/p', exist_ok=True)
IMGS = {}
def copy_grow_imgs():
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grow_img'); os.makedirs(OUT + '/img/grow', exist_ok=True)
    for f in os.listdir(src): shutil.copy(os.path.join(src, f), OUT + '/img/grow/' + f)

def img_for(p):
    """локальні шляхи фото товару (від кореня сайту)"""
    key = str(p.get('id'))
    out = []
    if p.get('id') == 472: out.append('img/kavun-main.jpg')
    for i, f in enumerate(LOCAL.get(key, [])):
        dst = f"img/p/{p['slug']}-{i+1}.webp"
        shutil.copy(ZIPDIR + f, OUT + '/' + dst); out.append(dst)
    if p['kind'] == 'crop_guide':
        own = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'field_img', p['slug'] + '.webp')
        f = FIELD_IMG.get(p['slug']) or GROUP_IMG.get(p['group'])
        if os.path.exists(own):   # власні фото полів (768×768)
            dst = f"img/p/{p['slug']}.webp"; shutil.copy(own, OUT + '/' + dst); out.append(dst)
        elif f:
            dst = f"img/p/{p['slug']}.webp"; shutil.copy(ZIPDIR + f, OUT + '/' + dst); out.append(dst)
    return out
for p in PRODUCTS + FIELDS:
    IMGS[p['slug']] = img_for(p)
copy_grow_imgs()
shutil.copytree(os.path.join(HERE, 'static'), OUT, dirs_exist_ok=True)
if os.path.exists(OUT + '/img/p/dobrivo-dlya-kartopl-greenodin-gray-granuli-1.webp'):
    IMGS['dobrivo-dlya-kartopl-greenodin-gray-granuli'] = ['img/kartoplia-card.jpg'] + IMGS['dobrivo-dlya-kartopl-greenodin-gray-granuli']

def img_alt(p):
    if p['kind'] == 'crop_guide': return f'Поле {p["crop_uk"]}' if p.get('crop_uk') else p['name']['uk']
    n = p['name']['uk']
    return n if 'GREENODIN' in n else f'{n} GREENODIN {(p.get("series") or "").upper()}'.strip()
# ---------- тексти ----------
BAD = re.compile(r'(?i)garden\s*soil|купити|грн|задати питання|написати відгук')
def paragraphs(t):
    t = re.sub(r'\s+', ' ', t or '').strip().replace('¶', '\n')
    t = re.sub(r'(?<=[a-zа-яіїєґ0-9.!?:;)»%])(?=[А-ЯІЇЄҐ][а-яіїєґ’\'])', '\n', t)
    t = re.sub(r'(?<=[A-Z])(?=[А-ЯІЇЄҐ][а-яіїєґ’\'])', '\n', t)
    t = re.sub(r'(?<=[A-Z]{2})(?=[УВЗІЯ] [а-яіїєґ])', '\n', t)
    t = re.sub(r'(?<=[.!?;])(?=(?:УВАГА|Важливо|Примітка)\b)', '\n', t)
    out = []
    for seg in t.split('\n'):
        sents = [s for s in re.split(r'(?<=[.!?])\s+', seg) if s.strip() and not BAD.search(s)]
        seg = ' '.join(sents).strip()
        if len(seg) < 3: continue
        if seg.startswith('• '):
            out.append(('li', seg[2:].strip(' ;'))); continue
        head = len(seg) < 95 and not seg.endswith(('.', ':', ';', '!', '?', ',')) and len(seg.split()) >= 2
        out.append(('h' if head else 'p', seg))
    # прибрати заголовки, після яких нічого немає
    clean = [x for i, x in enumerate(out) if not (x[0] == 'h' and (i + 1 == len(out) or out[i+1][0] == 'h'))]
    return clean
def article_html(t):
    out, ul = '', []
    for k, s in paragraphs(t) + [('end', '')]:
        if k == 'li': ul.append(s); continue
        if ul: out += '<ul class="al">' + ''.join(f'<li>{E(x)}</li>' for x in ul) + '</ul>'; ul = []
        if k == 'h': out += f'<h3>{E(s)}</h3>'
        elif k == 'p': out += f'<p>{E(s)}</p>'
    return out
def first_sentence(t, n=110):
    s = re.split(r'(?<=[.!?])\s', t or '')[0]
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + '…'

# ---------- іконки ----------
ICON = {
 'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
 'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
 'pin': '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
 'field': '<path d="M12 21V8"/><path d="M12 8c-2-1-3-3-3-5 2 1 3 3 3 5z"/><path d="M12 8c2-1 3-3 3-5-2 1-3 3-3 5z"/><path d="M12 13c-2-1-4-1-5-3 2 0 4 1 5 3z"/><path d="M12 13c2-1 4-1 5-3-2 0-4 1-5 3z"/><path d="M12 18c-2-1-4-1-5-3 2 0 4 1 5 3z"/><path d="M12 18c2-1 4-1 5-3-2 0-4 1-5 3z"/>',
 'garden': '<path d="M12 7c-3-2-8-1-8 5 0 5 3 9 5.5 9 1 0 1.5-.5 2.5-.5s1.5.5 2.5.5C16.5 21 20 17 20 12c0-6-5-7-8-5z"/><path d="M12 7c0-2 1-3 3-4"/>',
 'home': '<path d="M7 14h10l-1.5 7h-7z"/><path d="M12 14V9"/><path d="M12 10c-3 0-5-2-5-5 3 0 5 2 5 5z"/><path d="M12 10c3 0 5-2 5-5-3 0-5 2-5 5z"/>',
 'line': '<polygon points="12 3 3 8 12 13 21 8"/><path d="M3 12l9 5 9-5"/><path d="M3 16l9 5 9-5"/>',
 'up': '<polyline points="3 17 9 11 13 15 21 7"/><polyline points="15 7 21 7 21 13"/>',
 'sprout': '<path d="M12 21v-8"/><path d="M12 13c0-4 3-6 7-6 0 4-3 6-7 6z"/><path d="M12 15c0-3-2-5-6-5 0 3 2 5 6 5z"/>',
 'drop': '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
 'flask': '<path d="M9 3h6"/><path d="M10 3v6l-5 10a1.5 1.5 0 0 0 1.4 2h11.2a1.5 1.5 0 0 0 1.4-2l-5-10V3"/><path d="M8.5 15h7"/>',
 'star': '<polygon points="12 3 14.8 8.8 21 9.7 16.5 14 17.6 20.2 12 17.2 6.4 20.2 7.5 14 3 9.7 9.2 8.8"/>',
 'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
 'heart': '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
 'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 'doc': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/>',
 'check': '<polyline points="20 6 9 17 4 12"/>',
 'arrow': '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
}
svg = lambda k: f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICON[k]}</svg>'
SEC_ICON = {'pole': 'field', 'sad': 'garden', 'dim': 'home', 'liniyka': 'line'}
SEC_SUB = {'pole': 'Зернові, зернобобові, технічні культури', 'sad': 'Овочі та картопля, ягоди, плодові дерева',
           'dim': 'Квіти, хвойні, газон', 'liniyka': 'Базові добрива GREENODIN'}

# ---------- каркас сторінки ----------
SITE_URL = 'https://greenodin.vercel.app/'   # домен для canonical, sitemap.xml, Open Graph. Після підключення домену змінити на https://greenodin.site/ і зібрати знову
EMAIL = 'office@avelife.pro'
PHONE, PHONE_T = '+380432509090', '+38 043 250 90 90'
ADDR = 'Вінниця, вул. Миколи Оводова, 51, корп. 1, 5 поверх'
MAP_Q = 'Вінниця, вулиця Миколи Оводова, 51'
NAV = [('#about', 'Про GREENODIN'), ('/blog/', 'Блог'), ('patents.html', 'Патенти'), ('#partners', 'Партнерам'), ('kontakty.html', 'Контакти')]
CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>'
def header(pre, main=False):
    home = pre or './'
    def href(h):
        if h.startswith('/'): return h
        if not h.startswith('#'): return pre + h
        return h if main else (pre or './') + h
    links = ''.join(f'<a href="{href(h)}">{t}</a>' for h, t in NAV)
    def block(s):
        if s['id'] == 'liniyka':
            items = ''.join(f'<li><a href="{pre}{page_of(LINES[x])}"><i class="dot" style="background:{COLOR[x]}"></i>{x.upper()}</a></li>' for x in LINE_ORDER if x in LINES)
        else:
            items = ''.join(f'<li><a href="{pre}g/{gr["id"]}.html">{E(gr["name"]["uk"])}</a></li>' for gr in GROUPS if gr['section'] == s['id'])
        return f'<div class="ddc"><b>{E(s["name"]["uk"])}</b><ul>{items}</ul></div>'
    layout = [['pole'], ['sad', 'dim'], ['liniyka']]
    cols = ''.join('<div class="ddcol">' + ''.join(block(SEC[x]) for x in col) + '</div>' for col in layout)
    mega = (f'<div class="dd" id="dd"><a class="ddt" href="{pre}katalog.html" aria-haspopup="true" aria-expanded="false">Продукція{CHEV}</a>'
            f'<div class="ddm" role="menu"><div class="ddg">{cols}</div><a class="dda" href="{pre}katalog.html">Весь каталог →</a></div></div>')
    mob_groups = ''.join(f'<a class="ms" href="{pre}g/{gr["id"]}.html">{E(gr["name"]["uk"])}</a>' for gr in GROUPS)
    mob = (f'<details class="mdd"><summary>Продукція{CHEV}</summary><a class="ms" href="{pre}katalog.html"><b>Весь каталог</b></a>{mob_groups}</details>{links}')
    return (f'<header><div class="w hb"><a class="logo" href="{home}" aria-label="GREENODIN — на головну">'
            f'<img src="{pre}img/logo.png" alt="GREENODIN" width="131" height="20"></a>'
            f'<nav aria-label="Головне меню">{mega}{links}</nav>'
            f'<a class="hph" href="tel:{PHONE}" aria-label="Зателефонувати {PHONE_T}">{svg("phone")}<span>{PHONE_T}</span></a>'
            f'<button class="bg" id="bg" type="button" aria-expanded="false" aria-controls="m" aria-label="Меню"><span class="bgl"><i></i><i></i><i></i></span></button></div>'
            f'<div id="m">{mob}</div></header>')
def footer(pre):
    return (f'<footer><div class="w"><a href="{pre or "./"}">© GREENODIN</a><a href="{pre}patents.html">Патенти та сертифікати</a><a href="{pre}kontakty.html">Контакти</a><a href="{pre}sitemap.html">Карта сайту</a>'
            f'<a href="#">Політика конфіденційності</a></div></footer>')
HEAD = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700;800&display=swap">')
CRUMB_LD = []
def ld_script(d):
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>'
def meta_desc(d, n=160):
    d = re.sub(r'\s+', ' ', d).strip()
    if len(d) <= n: return d
    cut = d[:n]
    m = max(cut.rfind('. '), cut.rfind('! '), cut.rfind('? '))
    if m >= 90: return cut[:m + 1]
    return cut[:cut.rfind(' ')].rstrip(' ,;:—–-') + '…'
OG_CACHE = {}
def og_image(rel):
    """Картинка 1200×630 JPEG для соцмереж і месенджерів (webp і малі квадрати показуються погано)."""
    rel = rel or 'img/hero.jpg'
    if rel in OG_CACHE: return OG_CACHE[rel]
    from PIL import Image
    src = os.path.join(OUT, rel)
    if not os.path.exists(src): src = os.path.join(OUT, 'img/hero.jpg'); rel = 'img/hero.jpg'
    name = re.sub(r'[^A-Za-z0-9_-]+', '-', os.path.splitext(rel)[0]).strip('-') + '.jpg'
    dst = os.path.join(OUT, 'img', 'og', name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src).convert('RGB'); W, H = 1200, 630
    if im.width / im.height > 1.5:   # широка: заповнюємо кадр
        k = max(W / im.width, H / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        l, t = (im.width - W) // 2, (im.height - H) // 2
        out = im.crop((l, t, l + W, t + H))
    else:                            # квадратна: по центру на світлому тлі
        k = 560 / im.height
        im = im.resize((round(im.width * k), 560), Image.LANCZOS)
        out = Image.new('RGB', (W, H), (243, 246, 244)); out.paste(im, ((W - im.width) // 2, 35))
    out.save(dst, 'JPEG', quality=85, optimize=True)
    OG_CACHE[rel] = 'img/og/' + name
    return OG_CACHE[rel]
def doc(path, title, desc, body, main=False, extra_js='', ld=None, image=None, head_extra=''):
    pre = '../' * path.count('/')
    desc = meta_desc(desc)
    url = SITE_URL + ('' if path == 'index.html' else path)
    img = SITE_URL + og_image(image)
    lds = list(ld or [])
    if CRUMB_LD:
        lds.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, **({'item': u} if u else {})} for i, (n, u) in enumerate(CRUMB_LD)]})
        CRUMB_LD.clear()
    head = (f'<title>{E(title)}</title><meta name="description" content="{E(desc)}">'
            f'<link rel="canonical" href="{url}">'
            f'<meta property="og:type" content="{"website" if main else "article"}"><meta property="og:site_name" content="GREENODIN">'
            f'<meta property="og:locale" content="uk_UA"><meta property="og:title" content="{E(title)}">'
            f'<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg">'
            f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}">{HEAD}'
            f'<link rel="icon" href="{pre}favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="{pre}img/favicon-32.png">'
            f'<link rel="apple-touch-icon" href="{pre}img/apple-touch-icon.png"><link rel="manifest" href="{pre}site.webmanifest"><meta name="theme-color" content="#0d3b22">'
            f'<link rel="stylesheet" href="{pre}assets/style.css">' + head_extra + ''.join(ld_script(x) for x in lds))
    inner = f'{header(pre, main)}{body}{footer(pre)}<script src="{pre}assets/site.js"></script>{extra_js}'
    full = (f'<!doctype html><html lang="uk"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">{head}</head>'
            f'<body>{inner}</body></html>')
    os.makedirs(os.path.dirname(OUT + '/' + path) or OUT, exist_ok=True)
    open(OUT + '/' + path, 'w', encoding='utf-8').write(head + inner if main else full)
    if main:  # повна версія для хостингу (в архіві замінює index.html)
        open(BUILD + '/site_index_full.html', 'w', encoding='utf-8').write(full)
    PAGES.append(path)
PAGES = []

def crumbs(pre, items):
    CRUMB_LD.clear(); CRUMB_LD.append(('Головна', SITE_URL))
    for href, t in items:
        CRUMB_LD.append((t, (SITE_URL + href[len(pre):]) if href else None))
    parts = [f'<a href="{pre or "./"}">Головна</a>']
    for href, t in items[:-1]:
        parts.append(f'<a href="{href}">{E(t)}</a>')
    parts.append(f'<span aria-current="page">{E(items[-1][1])}</span>')
    return '<nav class="crumbs" aria-label="Навігація">' + '<span>/</span>'.join(parts) + '</nav>'


# ---------- schema.org ----------
ORG = {'@type': 'Organization', 'name': 'GREENODIN', 'url': SITE_URL, 'logo': SITE_URL + 'img/logo.png',
       'telephone': '+380432509090', 'email': EMAIL,
       'address': {'@type': 'PostalAddress', 'streetAddress': 'вул. Миколи Оводова, 51, корп. 1', 'addressLocality': 'Вінниця', 'addressCountry': 'UA'}}
def product_ld(p, name):
    ims = IMGS.get(p['slug'], [])
    d = {'@context': 'https://schema.org', '@type': 'Product', 'name': name, 'description': p['lead']['uk'],
         'brand': {'@type': 'Brand', 'name': 'GREENODIN'}, 'manufacturer': {'@type': 'Organization', 'name': 'НВ ТОВ «Сінта»'},
         'url': SITE_URL + page_of(p), 'category': GRP[p['group']]['name']['uk']}
    if p.get('sku'): d['sku'] = p['sku']
    if ims: d['image'] = [SITE_URL + x for x in ims[:1]]
    return d
def itemlist_ld(name, items):
    return {'@context': 'https://schema.org', '@type': 'ItemList', 'name': name, 'numberOfItems': len(items),
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE_URL + page_of(x), 'name': x['name']['uk']} for i, x in enumerate(items)]}

# ---------- картки ----------
def card(p, pre):
    ims = IMGS.get(p['slug'], [])
    if p['kind'] == 'crop_guide':
        label = 'Лінійки: ' + ', '.join(s.upper() for s in p.get('recommended_series', []))
        ds = label
    else:
        ds = first_sentence(p['lead']['uk'])
    ser = p.get('series') or ''
    if ims:
        ph = f'<div class="ph im"><img src="{pre}{ims[0]}" alt="{E(img_alt(p))}" loading="lazy" draggable="false"></div>'
    else:
        ph = f'<div class="ph" style="background:{COLOR.get(ser, "var(--dg)")}">{"GREENODIN " + ser.upper() if ser else "Для полів"}</div>'
    tag = f'<span class="cs">{E(SERIES_NAME(ser))}</span>' if ser and p['kind'] != 'line' else ''
    return (f'<a class="cd" href="{pre}{page_of(p)}" data-n="{E((p["name"]["uk"] + " " + (p.get("crop_uk") or "")).lower())}">{ph}'
            f'<div class="cb">{tag}<h3>{E(p["name"]["uk"])}</h3><p class="ds">{E(ds)}</p></div></a>')

def items_of_group(gid):
    its = [p for p in PRODUCTS if p['group'] == gid] + [p for p in FIELDS if p['group'] == gid]
    if gid == 'liniyka':
        its.sort(key=lambda p: LINE_ORDER.index(p['series']))
    else:
        its.sort(key=lambda p: p['name']['uk'])
    return its

ARROWS = '<span class="ars"><button class="ar" type="button" data-d="-1" aria-label="Назад">‹</button><button class="ar" type="button" data-d="1" aria-label="Вперед">›</button></span>'

def slider(title, its, pre, sub='', gid=None, more=None):
    sm = f'<small>{E(sub)}</small>' if sub else ''
    mr = f'<a class="more" href="{more}">Усі {len(its)}</a>' if more else ''
    hid = f' id="g-{gid}"' if gid else ''
    return f'<div class="gh"{hid}><span>{E(title)}</span>{sm}{mr}{ARROWS}</div><div class="sl">{"".join(card(p, pre) for p in its)}</div>'

def crop_row(p, pre):
    ims = IMGS.get(p['slug'], [])
    im = f'<img src="{pre}{ims[0]}" alt="{E(img_alt(p))}" loading="lazy">' if ims else '<span class="noim"></span>'
    return f'<li><a href="{pre}{page_of(p)}">{im}<span>{E(p["name"]["uk"])}</span>{svg("arrow")}</a></li>'

# ---------- блоки сторінки товару ----------
def facts(rows):
    return '<dl class="facts">' + ''.join(f'<div><dt>{E(a)}</dt><dd>{b}</dd></div>' for a, b in rows if b) + '</dl>'

def tabs(panels, pid=''):
    btn = ''.join(f'<button class="c{" on" if i == 0 else ""}" role="tab" id="{pid}tb{i}" aria-controls="{pid}tp{i}" aria-selected="{"true" if i == 0 else "false"}" type="button">{E(t)}</button>' for i, (t, _) in enumerate(panels))
    pan = ''.join(f'<section class="tp{" on" if i == 0 else ""}" role="tabpanel" id="{pid}tp{i}" aria-labelledby="{pid}tb{i}">{h}</section>' for i, (_, h) in enumerate(panels))
    return f'<div class="acs"><div class="tabs ch" id="{pid}tabs" role="tablist" aria-label="Інформація">{btn}</div><div class="tps">{pan}</div></div>'

CERT = SH['granules']['organic_standard']
KF = (f'<div class="kf"><div><small>Сертифікат</small><b>Organic Standard</b><span>№ {CERT["cert_no"]} від 16.10.2023</span></div>'
      f'<div><small>Регламент ЄС</small><b>2018/848</b></div><div><small>Технічні умови</small><b>{E(CERT["tu"])}</b></div></div>')

ADV_ICON = {'fertility': 'sprout', 'yield': 'up', 'toxicity': 'shield', 'vitality': 'heart', 'growth': 'up',
            'water': 'drop', 'stress': 'sun', 'prolonged': 'clock'}
def advantages(p):
    cl = p.get('claims', {})
    li = []
    for a in SH['advantages']:
        if a['claim'] and not cl.get(a['claim']): continue
        txt = a['text_uk'].replace('{water_pct}', str(cl.get('water_pct', '')))
        li.append(f'<li><span class="ic">{svg(ADV_ICON[a["key"]])}</span><div><b>{E(a["title_uk"])}</b><p>{E(txt)}</p></div></li>')
    return '<ul class="bn pv">' + ''.join(li) + '</ul>'

COMPOSITION = [
 ('Природні мінеральні компоненти', 'Леонардит, збагачений гуміновими та фульвовими кислотами: природне живлення рослин і корисних бактерій'),
 ('Аморфний кремній', 'Підтримує потрібну кислотність pH, накопичує й структурує воду, живить коріння капілярним способом'),
 ('Макро- та мікроелементи', 'Для росту рослин і стійкості до стресових факторів'),
 ('Корисні бактерії', 'Агрономічно корисні мікроорганізми, що запускають гумусоутворення'),
 ('Органічна речовина (C)', '<b>не менше 50–55%</b>'),
 ('Азот (N)', '<b>не менше 150 мг/100 г</b>'),
 ('Фосфор (P₂O₅)', '<b>не менше 150 мг/100 г</b>'),
 ('Калій (K)', '<b>не менше 200 мг/100 г</b>'),
]
comp_html = '<table class="tb">' + ''.join(f'<tr><th>{a}</th><td>{b}</td></tr>' for a, b in COMPOSITION) + '</table>'

BIO = [('Кислотність', 'нормалізує кислотність ґрунту до потрібної рослині'), ('Флора', 'пригнічує патогенну флору ґрунту'),
 ('Гумусоутворення', 'створює середовище для природного гумусоутворення й розвитку корисних бактерій'),
 ('Якість ґрунту', 'поліпшує якість ґрунту'), ('Фітотоксичність', 'знижує фітотоксичність ґрунту'),
 ('Імунітет', 'зміцнює імунну систему рослин'), ('Ефект', 'пролонгований, дає змогу щосезону знижувати норму внесення на 20%'),
 ('Шкідники', 'відштовхує шкідників'), ('Стреси', 'підвищує стійкість до стресів'), ('Морозостійкість', 'формує морозостійкість рослин'),
 ('Посуха і спека', 'підвищує посухо- та жаростійкість'), ('Полив', 'знижує норми поливу')]
bio_html = '<ul class="bi">' + ''.join(f'<li>{svg("check")}<span><b>{a}:</b> {b}</span></li>' for a, b in BIO) + '</ul>'

METHOD = '<div class="nt"><b>Спосіб внесення:</b> кореневе. Розкидати й полити, можна присипати землею.</div>'
def dose_html(p):
    t = p.get('dose_type')
    tiles = []
    if t == 'shrub_tree':
        tiles = [('При посадці', '25 г', 'на 1 л ґрунту або субстрату'), ('Висота 0,5–1 м', '50 г', 'під рослину'),
                 ('Висота 1–1,5 м', '75 г', 'під рослину, 2 рази на рік')]
        note = 'Дія пролонгована, тому щороку норму зменшують на 20%.'
    elif t == 'substrate':
        v = p['dose_text_uk'].split(' на ')[0]
        tiles = [('При посадці або пересаджуванні', v, 'на 1 л субстрату, перемішати перед посадкою'),
                 ('Наступні роки', '−20%', 'норму щороку зменшують завдяки накопичувальному ефекту')]
        note = ''
    elif t == 'conifer_page':
        tiles = [('По площі', '25 г/м²', '2,5 кг на сотку · 250 кг/га'), ('Живопліт', '25 г', 'на погонний метр рядка'),
                 ('Під рослину', '25 г', 'під кожну хвойну рослину')]
        note = 'Щороку норму зменшують на 20%, до 8 г/м² (80 кг/га) на 6-й сезон.'
    else:
        tiles = [('1-й рік', '25 г/м²', '2,5 кг на сотку · 250 кг/га, 2 рази на рік'), ('2–4 роки', '−20%', 'норму щороку зменшують на 20%'),
                 ('5-й рік і далі', '8 г/м²', '0,8 кг на сотку · 80 кг/га, далі норма не змінюється')]
        note = ''
    dz = '<div class="dz">' + ''.join(f'<div><small>{E(a)}</small><b>{E(b)}</b><span>{E(c)}</span></div>' for a, b, c in tiles) + '</div>'
    return dz + (f'<p class="hint">{E(note)}</p>' if note else '') + METHOD

def line_chip(s, pre, note=''):
    lp = LINES.get(s)
    inner = f'<span class="dot" style="background:{COLOR[s]}"></span><span><b>{E(SERIES_NAME(s))}</b>{"<small>" + E(note) + "</small>" if note else ""}</span>{svg("arrow")}'
    return f'<a class="lk" href="{pre}{page_of(lp)}">{inner}</a>' if lp else f'<span class="lk">{inner}</span>'

def details(title, body):
    return f'<details class="art"><summary>{E(title)}</summary><div class="artb">{body}</div></details>' if body else ''



# ---------- вкладка «Вирощування»: розділи-акордеон ----------
PREPS = {'в','у','з','із','зі','на','для','до','по','та','і','й','від','при','під','над','без','через','про','за','або','як','що'}
STOPCAP = ('Україн', 'Європ', 'Київ', 'Миколаїв', 'Одес', 'Вінниц', 'Поділл', 'Степ', 'Полісс', 'Лісостеп', 'Карпат', 'Пасльон', 'Органік', 'Інститут')
JUNK = re.compile(r'(?i)читайте статтю|купіть|стадії рішення|звіти про застосування|внизу сторінки')
def split_heading(s):
    w = s.split(' ')
    if len(w) < 6 or not re.match(r'^[А-ЯІЇЄҐA-Z]', w[0]): return None
    for i in range(2, min(8, len(w) - 3)):
        x = w[i]
        if '.' in ' '.join(w[:i]) or ':' in ' '.join(w[:i]) or ',' in w[i - 1]: return None
        if re.match(r'^[А-ЯІЇЄҐ][а-яіїєґ’\'-]{2,}$', x) and w[i - 1].lower() not in PREPS and not x.startswith(STOPCAP) \
           and re.match(r'^[а-яіїєґa-z0-9’\'-]+$', w[i - 1]) and len(' '.join(w[:i])) <= 70:
            return ' '.join(w[:i]), ' '.join(w[i:])
    return None
def chunk(p, n=650):
    if len(p) <= n: return [p]
    sents, out, cur = re.split(r'(?<=[.!?])\s+', p), [], ''
    for s in sents:
        if cur and len(cur) + len(s) > n: out.append(cur); cur = s
        else: cur = (cur + ' ' + s).strip()
    if cur: out.append(cur)
    return out
def grow_html(t):
    segs = []
    for k, s in paragraphs(t):
        if k != 'p' and k != 'h': segs.append((k, s)); continue
        if JUNK.search(s) or s.count('л/') >= 3 or s.count('+') >= 3: 
            s = ' '.join(x for x in re.split(r'(?<=[.!?])\s+', s) if not JUNK.search(x) and x.count('л/') < 3 and x.count('+') < 3)
            if len(s) < 40: continue
        if k == 'p':
            sp = split_heading(s)
            if sp: segs.append(('h', sp[0])); s = sp[1]
        segs.append((k, s))
    def ok_h(s):
        return len(s) >= 5 and not re.search(r'\d', s) and ',' not in s and not s.startswith('Больше')
    def numeric(s):
        return sum(c.isdigit() for c in s) > 0.15 * max(len(s), 1)
    segs = [('p' if k == 'h' and not ok_h(s) else k, s) for k, s in segs if not numeric(s)]
    # довгий абзац зі списком через «;»
    sp = []
    for k, s in segs:
        if k == 'p' and s.count(';') >= 3:
            parts = [x.strip(' .') for x in s.split(';') if x.strip(' .')]
            sp.append(('p', parts[0] + ':')); sp += [('li', x) for x in parts[1:]]
        else: sp.append((k, s))
    segs = sp
    # списки: короткі абзаци після речення з двокрапкою
    out, lst = [], False
    for k, s in segs:
        if k == 'p' and lst and len(s) <= 240 and not s.endswith(':') and not re.match(r'^(УВАГА|Важливо|Примітка)', s):
            out.append(('li', s.rstrip(' ;.'))); continue
        lst = (k in ('p', 'li') and s.rstrip().endswith(':')) or (k == 'li' and lst)
        out.append((k, s))
    # блоки: li з «Етап: норма» -> таблиця
    blocks, i = [], 0
    while i < len(out):
        k, s = out[i]
        if k == 'li':
            j = i
            while j < len(out) and out[j][0] == 'li': j += 1
            items = [x[1] for x in out[i:j]]
            m = [re.match(r'^([^:]{3,70}):\s*(.*\d.*)$', x) for x in items]
            if len(items) >= 2 and all(m) and all(re.search(r'\d\s*(г|кг|мл|л|%|см|м)', x.group(2)) for x in m):
                blocks.append({'t': 'table', 'rows': [['Етап', 'Норма або дія']] + [[x.group(1).strip(), x.group(2).strip().rstrip('.')] for x in m]})
            else:
                blocks += [{'t': 'li', 'x': x} for x in items]
            i = j; continue
        blocks.append({'t': k, 'x': s}); i += 1
    return grow_blocks_html(blocks, '')

def grow_blocks_html(bl, pre):
    """«Вирощування» зі структурних блоків старого сайту: списки, таблиці, фото"""
    def body(items):
        out, ul, pr = '', [], []
        def flush_ul():
            nonlocal out, ul
            if ul: out += '<ul class="al">' + ''.join(f'<li>{E(x)}</li>' for x in ul) + '</ul>'; ul = []
        def flush_pr():
            nonlocal out, pr
            if pr: out += '<div class="proto">' + ''.join(f'<p>{E(x)}</p>' for x in pr) + '</div>'; pr = []
        for b in items:
            k = b['t']
            if k == 'li': flush_pr(); ul.append(b['x']); continue
            flush_ul()
            if k == 'p' and re.match(r'^\d+(\.\d+)*\.?\s', b['x']) and len(b['x']) < 260: pr.append(b['x']); continue
            flush_pr()
            if k == 'p': out += ''.join(f'<p>{E(c)}</p>' for c in chunk(b['x']))
            elif k == 'table':
                rows = b['rows']
                cap = f'<caption>{E(b["cap"])}</caption>' if b.get('cap') else ''
                isn = lambda c: bool(re.match(r"^[\d\s,.\-–]+$", c))
                numcol = [i > 0 and all(isn(r[i]) for r in rows[1:] if i < len(r) and r[i]) for i in range(len(rows[0]))]
                th = ''.join(f'<th class="{"n" if numcol[i] else ""}">{E(c)}</th>' for i, c in enumerate(rows[0]))
                tr = ''.join('<tr>' + ''.join(f'<td class="{"n" if i < len(numcol) and numcol[i] else ""}">{E(c)}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows[1:])
                out += f'<div class="tw"><table class="tm gt">{cap}<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
            elif k == 'img':
                cp = f'<figcaption>{E(b["cap"])}</figcaption>' if b.get('cap') else ''
                out += f'<figure class="gf"><img src="{pre}{b["src"]}" width="{b["w"]}" height="{b["h"]}" alt="{E(b["alt"])}" loading="lazy">{cp}</figure>'
        flush_ul(); flush_pr()
        return out
    intro, secs = [], []
    for b in bl:
        if b['t'] == 'h': secs.append([b['x'], []])
        elif secs: secs[-1][1].append(b)
        else: intro.append(b)
    secs = [x for x in secs if x[1]]
    html_ = f'<div class="glead artb">{body(intro)}</div>' if intro else ''
    html_ += '<div class="acc">' + ''.join(
        f'<details class="sec"{" open" if i == 0 and not intro else ""}><summary>{E(h)}</summary><div class="artb">{body(items)}</div></details>'
        for i, (h, items) in enumerate(secs)) + '</div>'
    return html_


# ---------- вкладка «Питання» + розмітка FAQPage ----------
def faq_html(p):
    items = (p.get('faq') or {}).get('uk') or []
    if not items: return ''
    return '<div class="acc faq">' + ''.join(
        f'<details class="sec"{" open" if i == 0 else ""}><summary>{E(x["q"])}</summary><div class="artb"><p>{E(x["a"])}</p></div></details>'
        for i, x in enumerate(items)) + '</div>'
def faq_ld(p):
    items = (p.get('faq') or {}).get('uk') or []
    if not items: return ''
    data = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': x['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': x['a']}} for x in items]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'

# ---------- вкладка «Документи» ----------
def doc_applies(d, p):
    a = d.get('applies', {})
    if a.get('all'): return True
    if p['kind'] == 'line': return p['series'] in a.get('lines', [])
    if p['kind'] == 'crop_guide': return p['slug'] in a.get('fields', [])
    return p.get('id') in a.get('products', [])
def docs_tab(p, pre):
    D = CAT['site']['uk']['docs']
    def row(href, thumb, title, meta, extra=''):
        return (f'<li><a href="{pre}patents.html#{href}"><img src="{pre}img/docs/{thumb}-t.webp" alt="{E(title)}" loading="lazy">'
                f'<span><b>{E(title)}</b><small>{E(meta)}</small>{extra}</span>{svg("arrow")}</a></li>')
    certs = [row(c['id'], c['pages'][0][0], c['title'], c['sub']) for c in D['certs'] if doc_applies(c, p)]
    pats = [row('p' + x['no'], x['pages'][0][0], x['title'], f'Патент України № {x["no"]} · {x["date"]}') for x in D['patents'] if doc_applies(x, p)]
    reps = [row(r['id'], r['pages'][0][0], r['title'], f'Звіт {r["year"]} · {r["meta"]}',
                f'<em>{E(r["result"])}</em>' if r.get('result') else '') for r in D['reports'] if doc_applies(r, p)]
    out = ''
    for title, rows in (('Звіти випробувань', reps), ('Сертифікати', certs), ('Патенти', pats)):
        if rows: out += f'<h3 class="dlh">{title}</h3><ul class="dlist">{"".join(rows)}</ul>'
    return out

# ---------- сторінка товару (культура) ----------
def product_page(p):
    path = page_of(p); pre = '../'
    g = GRP[p['group']]; s = SEC[p['section']]
    ser = p['series']
    ims = IMGS.get(p['slug'], [])
    gal = (f'<div class="gal"><img src="{pre}{ims[0]}" alt="{E(p["name"]["uk"])}, упаковка {E(SERIES_NAME(ser))}" width="700" height="700">'
           + '</div>') if ims else \
          f'<div class="gal"><div class="phb" style="background:{COLOR[ser]}">{E(SERIES_NAME(ser))}</div></div>'
    h1 = f'{p["name"]["uk"]} {SERIES_NAME(ser)}'
    tags = f'<div class="tags"><span class="tg">{E(SERIES_NAME(ser))}</span><span class="tg l">Гранули</span><span class="tg l">Organic Standard</span></div>'
    also = ''
    lines_block = f'<p class="lb">Базова лінійка</p><div class="lks">{line_chip(ser, pre)}</div>'
    if p.get('also_suitable'):
        also = '<p class="lb">Також підходять</p><div class="lks">' + ''.join(line_chip(a['series'], pre, a['note_uk']) for a in p['also_suitable']) + '</div>'
    fx = facts([('Тип', 'Комплексне, 100% органічне, пролонгованої дії, з живими бактеріями'), ('Форма', 'Гранули'),
                ('Виробник', 'Україна'), ('Сертифікація', 'Organic Standard, Регламент (ЄС) 2018/848'),
                ('Термін придатності', '3 роки з моменту відкриття упаковки'), ('Безпека', 'Безпечне для людей, бджіл і тварин'),
                ('Артикул', E(p.get('sku')))])
    src = (p.get('subcategory_article') or {}).get('uk') if p.get('subcategory_article') else None
    art = article_html(src or p['description']['uk'])
    desc = f'<p>{E(p["lead"]["uk"])}</p>{KF}'
    body = (f'<main id="top"><div class="w">{crumbs(pre, [(pre + "katalog.html", "Каталог"), (pre + "g/" + g["id"] + ".html", g["name"]["uk"]), (None, p["name"]["uk"])])}'
            f'<div class="pg">{gal}<div class="info">{tags}<h1 class="pt">{E(h1)}</h1><p class="lead">{E(p["lead"]["uk"])}</p>'
            f'{lines_block}{also}{fx}</div></div>'
            + tabs([x for x in [('Опис', desc), ('Переваги', advantages(p)), ('Склад', comp_html), ('Норми', dose_html(p)), ('Дія', bio_html), ('Вирощування', grow_blocks_html(GB[p['slug']], pre) if p['slug'] in GB else grow_html(src or p['description']['uk'])), ('Питання', faq_html(p)), ('Документи', docs_tab(p, pre))] if x[1]]))
    rel = [x for x in items_of_group(p['group']) if x['slug'] != p['slug']]
    if rel:
        body += f'<div class="rel">{slider("Інші добрива: " + g["name"]["uk"].lower(), rel, pre, more=pre + "g/" + g["id"] + ".html")}</div>'
    body += '</div></main>' + faq_ld(p)
    doc(path, f'{h1} — органічне добриво', p['lead']['uk'], body, ld=[product_ld(p, h1)], image=(ims or [None])[0])


LINE_SECTIONS = [
 ('pryzn', r'Призначення (?:органічного добрива |рекультивату |меліоранту |субстрату )?GREENODIN'),
 ('rek', r'Рекомендац\w+ (?:до|для) застосування'),
 ('sklad', r'Склад (?:рекультивату|органічного субстрату|меліоранта|субстрату)'),
 ('norm', r'Норма внесення'),
 ('pack', r'Упаковка'),
 ('vnes', r'Спосіб (?:внесення|застосування)|Замішування рекультивату'),
 ('perev', r'Переваги, які Ви отримаєте'),
 ('tu', r'Технічні умови:'),
]
def split_line(t):
    t = re.sub(r'\s+', ' ', t or '').strip()
    pos = []
    for k, rx in LINE_SECTIONS:
        m = re.search(rx, t)
        if m: pos.append((m.start(), k))
    pos.sort()
    out = {'intro': t[:pos[0][0]] if pos else t}
    for i, (s, k) in enumerate(pos):
        e = pos[i + 1][0] if i + 1 < len(pos) else len(t)
        c = t[s:e]
        if k == 'pack': c = c[len('Упаковка'):]
        elif k != 'tu':
            c = re.sub(r'^.{0,90}?GREENODIN\s+[A-Za-z]+(?:\s+субстрат)?\s*', '', c, count=1) if re.match(r'^.{0,90}?GREENODIN', c) else re.sub(r'^\S+\s+\S+\s*', '', c, count=1)
        c = re.sub(r'(?<=[а-яіїєґa-z0-9.):,])\s?-\s', '¶• ', c)
        c = re.sub(r'(?<=[а-яіїєґ.])(?=(?:силікат калію|трепел|модифіковані|макроелементи|агрономічно корисні|природні кремн|лігніт|діатоміт|торф|Діюча речовина|бентоніт))', '¶• ', c)
        c = re.sub(r'(?<=розсіюємо)(?=[а-яіїєґ])', '¶', c)
        if k == 'sklad' and not c.startswith('• '): c = '• ' + c
        out[k] = (out.get(k, '') + ' ' + c).strip()
    return out

# ---------- сторінка лінійки ----------
def line_page(p):
    path = page_of(p); pre = '../'
    ser = p['series']; ims = IMGS.get(p['slug'], [])
    gal = (f'<div class="gal"><img src="{pre}{ims[0]}" alt="Упаковка {E(SERIES_NAME(ser))}" width="700" height="700"></div>') if ims else \
          f'<div class="gal"><div class="phb" style="background:{COLOR[ser]}">{E(SERIES_NAME(ser))}</div></div>'
    crops = [x for x in PRODUCTS if x['kind'] == 'crop_fertilizer' and x['series'] == ser]
    also = [x for x in PRODUCTS if any(a['series'] == ser for a in x.get('also_suitable', []))]
    fields = [x for x in FIELDS if ser in x.get('recommended_series', [])]
    use = crops + also + fields
    use_html = ('<ul class="clist">' + ''.join(crop_row(x, pre) for x in use) + '</ul>') if use else \
               '<p>Базове добриво для господарств і великих площ. Лінійку обирають за аналізом ґрунту.</p>'
    S = split_line(p['description']['uk'])
    intro = article_html(S['intro']) + (f'<h3>Призначення</h3>{article_html(S["pryzn"])}' if S.get('pryzn') else '')
    sklad = article_html(S.get('sklad', '')) + (f'<p class="hint">{E(S["tu"])}</p>' if S.get('tu') else '')
    tags = f'<div class="tags"><span class="tg" style="background:{COLOR[ser]}">{E(SERIES_NAME(ser))}</span><span class="tg l">Лінійка</span><span class="tg l">Organic Standard</span></div>'
    fx = facts([('Призначення', 'Меліорант і рекультивант для ґрунтів'), ('Виробник', 'Україна'),
                ('Сертифікація', 'Organic Standard, Регламент (ЄС) 2018/848'), ('Артикул', E(p.get('sku')))])
    cnt = f'<p class="lb">Рекомендовано для {len(use)} культур</p>' if use else ''
    body = (f'<main id="top"><div class="w">{crumbs(pre, [(pre + "katalog.html", "Каталог"), (pre + "g/liniyka.html", "Лінійка GREENODIN"), (None, SERIES_NAME(ser))])}'
            f'<div class="pg">{gal}<div class="info">{tags}<h1 class="pt">Добриво {E(SERIES_NAME(ser))}</h1><p class="lead">{E(p["lead"]["uk"])}</p>{cnt}{fx}</div></div>'
            + tabs([x for x in [('Опис', intro), ('Культури', use_html), ('Рекомендації', article_html(S.get('rek', ''))), ('Склад', sklad),
                                ('Норми', article_html(S.get('norm', ''))), ('Внесення', article_html(S.get('vnes', ''))),
                                ('Упаковка', article_html(S.get('pack', ''))), ('Переваги', article_html(S.get('perev', ''))), ('Питання', faq_html(p)), ('Документи', docs_tab(p, pre))] if x[1]])
            + f'<div class="rel">{slider("Інші добрива лінійки", [x for x in items_of_group("liniyka") if x["slug"] != p["slug"]], pre, more=pre + "g/liniyka.html")}</div></div></main>' + faq_ld(p))
    doc(path, LINE_TITLE.get(ser, f'Добриво {SERIES_NAME(ser)}'), p['lead']['uk'], body, ld=[product_ld(p, 'Добриво ' + SERIES_NAME(ser))], image=(ims or [None])[0])

LINE_TITLE = {
 'gray': 'GREENODIN GRAY — рекультивант для відновлення родючості ґрунту',
 'brown': 'GREENODIN BROWN — меліорант для підкислення ґрунту',
 'black': 'GREENODIN BLACK — меліорант для деградованих і збіднених ґрунтів',
 'melior': 'GREENODIN MELIOR — меліорант для розкислення кислих ґрунтів',
 'red': 'GREENODIN RED — меліорант для кислих збіднених ґрунтів',
 'white': 'GREENODIN WHITE — вологоутримувальний меліорант для легких ґрунтів',
 'multihumate': 'GREENODIN MULTIHUMATE — універсальний меліорант з бактеріями',
 'microbox': 'GREENODIN MICROBOX — ґрунтовий субстрат для розсади й квітів',
}
# ---------- сторінка польової культури ----------
def field_page(p):
    path = page_of(p); pre = '../'
    g = GRP[p['group']]; gd = p['guide']
    big = re.match(r'(\d+)\s*кг/га', gd['base'])
    fim = (IMGS.get(p['slug']) or [None])[0]
    fst = f' fpi" style="--fim:url({pre}{fim})' if fim else ''
    panel = (f'<div class="gal"><div class="fp{fst}"><small>Для полів · {E(g["name"]["uk"])}</small><b>{E(p["name"]["uk"])}</b>'
             f'<div class="fpn"><span>Базова норма</span><strong>{big.group(1) if big else "250"}<em>кг/га</em></strong></div>'
             f'<div class="fpl">{"".join(f"<span style=background:{COLOR[s]}>{s.upper()}</span>" for s in p["recommended_series"])}</div></div></div>')
    lines = '<p class="lb">Рекомендовані лінійки</p><div class="lks">' + ''.join(line_chip(s, pre) for s in p['recommended_series']) + '</div>'
    if len(p['recommended_series']) > 1:
        lines += '<p class="hint">Лінійку обирають за кислотністю та складом ґрунту; добрива можна поєднувати.</p>'
    fx = facts([('Тип вирощування', E(gd['growing'])), ('Оптимальний pH ґрунту', E(gd['ph_opt']) if gd['ph_opt'] not in ('—', '') else ''),
                ('Попередники', E(gd['predecessors']) if not gd['predecessors'].startswith('Не вказано') else '')])
    # вибір лінійки
    if p.get('ph_rules'):
        rows = ''.join(f'<tr><th>{E(r["text"])}</th><td>{line_chip(r["series"].lower(), pre)}</td></tr>' for r in p['ph_rules'] if r['series'] != '?')
        choose = f'<table class="tb phr">{rows}</table><p class="hint">Кислотність ґрунту варто визначити лабораторним аналізом. Добрива різних лінійок можна поєднувати.</p>'
    else:
        choose = '<div class="lks">' + ''.join(line_chip(s, pre) for s in p['recommended_series']) + '</div>'
    # норми
    tiles = [('Основне внесення', gd['base'])]
    if gd['stubble'] not in ('—', ''): tiles.append(('По стерні / рештках', gd['stubble']))
    if gd['minimum'] not in ('—', ''): tiles.append(('Мінімальна норма', gd['minimum']))
    def split_rate(t):
        m = re.match(r'(до\s*)?(\d+(?:–\d+)?\s*кг/га)\s*(.*)', t)
        return (m.group(2), (m.group(1) or '') + m.group(3)) if m else (t, '')
    dz = '<div class="dz">' + ''.join(f'<div><small>{E(a)}</small><b>{E(split_rate(b)[0])}</b><span>{E(split_rate(b)[1].strip(" ;,"))}</span></div>' for a, b in tiles) + '</div>'
    dz += '<p class="hint">Завдяки накопичувальному ефекту норму щороку знижують на 20%.</p>'
    # техкарта
    tm = p.get('techmap') or []
    if tm:
        rows, last = '', None
        for r in tm:
            st = '' if r['stage'] == last else f'<tr class="st"><td colspan="3">{E(r["stage"])}</td></tr>'
            last = r['stage']
            rows += st + f'<tr><td>{E(r["product"])}</td><td class="n">{E(r["rate"])}</td><td class="n mu">{E(r["solution"] or "")}</td></tr>'
        tmh = f'<div class="tw"><table class="tm"><thead><tr><th>Препарат</th><th>Норма</th><th>Робочий розчин</th></tr></thead><tbody>{rows}</tbody></table></div>'
        tmh += '<p class="hint">Перед застосуванням допоміжних препаратів перевірте їхні чинні етикетки та сумісність.</p>'
    else:
        tmh = ''
    art = article_html(p['description']['uk'])
    panels = [('Лінійки', choose), ('Норми', dz)]
    if tmh: panels.append(('Техкарта', tmh))
    panels.append(('Вирощування', grow_blocks_html(GB[p['slug']], pre) if p['slug'] in GB else grow_html(p['description']['uk'])))
    panels.append(('Питання', faq_html(p)))
    panels.append(('Документи', docs_tab(p, pre)))
    h1 = p['h1']['uk']
    body = (f'<main id="top"><div class="w">{crumbs(pre, [(pre + "katalog.html", "Каталог"), (pre + "g/" + g["id"] + ".html", g["name"]["uk"]), (None, p["name"]["uk"])])}'
            f'<div class="pg">{panel}<div class="info"><div class="tags"><span class="tg">Для полів</span><span class="tg l">{E(g["name"]["uk"])}</span></div>'
            f'<h1 class="pt">{E(h1)}</h1><p class="lead">{E(p["lead"]["uk"])}</p>{lines}{fx}</div></div>'
            + tabs(panels))
    rel = [x for x in FIELDS if x['slug'] != p['slug']]
    body += f'<div class="rel">{slider("Інші польові культури", rel, pre)}</div></div></main>' + faq_ld(p)
    doc(path, p['seo']['uk']['title'], p['seo']['uk']['meta'], body, image=(IMGS.get(p['slug']) or [None])[0])

# ---------- сторінка групи ----------
def group_intro_html(bl, pre):
    """Структурований опис категорії: лід, блоки «заголовок + текст», кроки, таблиця, картки-слайдер"""
    def tbl(b):
        th = ''.join(f'<th>{E(c)}</th>' for c in b['rows'][0]); tr = ''.join('<tr>' + ''.join(f'<td>{E(c)}</td>' for c in r) + '</tr>' for r in b['rows'][1:])
        return f'<div class="tw"><table class="tm gt"><caption>{E(b["cap"])}</caption><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
    def one(b):
        t = b['t']
        if t == 'p': return f'<p>{E(b["x"])}</p>'
        if t == 'h3': return f'<h3>{E(b["x"])}</h3>'
        if t == 'ul': return '<ul class="al">' + ''.join(f'<li>{E(x)}</li>' for x in b['items']) + '</ul>'
        if t == 'note': return f'<aside class="note">{svg("shield")}<p>{E(b["x"])}</p></aside>'
        if t == 'table': return tbl(b)
        if t == 'steps':
            li = ''.join(f'<li><b>{E(i["t"])}</b><span>{E(i["x"])}</span>' + (('<ul class="al">' + ''.join(f'<li>{E(x)}</li>' for x in i['sub']) + '</ul>') if i.get('sub') else '') + '</li>' for i in b['items'])
            return (f'<h3>{E(b["title"])}</h3>' if b.get('title') else '') + f'<ol class="stp">{li}</ol>'
        return ''
    def cards(b):
        cs = ''.join(f'<article class="wc"><span class="ic">{svg(i["i"])}</span><b>{E(i["t"])}</b><p>{E(i["x"])}</p></article>' for i in b['items'])
        return f'<div class="gcs"><div class="gh shd"><h2>{E(b["title"])}</h2>{ARROWS}</div><div class="sl wsl">{cs}</div></div>'
    out = ''; lead = []; i = 0
    while i < len(bl) and bl[i]['t'] == 'p': lead.append(bl[i]); i += 1
    if lead: out += '<div class="glead">' + ''.join(one(b) for b in lead) + '</div>'
    cur = None; body = ''
    def flush():
        nonlocal out, cur, body
        if cur is not None: out += f'<section class="gb"><h2>{E(cur)}</h2><div class="gbt">{body}</div></section>'
        cur = None; body = ''
    for b in bl[i:]:
        if b['t'] == 'part': flush(); out += f'<h2 class="gpart">{E(b["x"])}</h2>'
        elif b['t'] == 'cards': flush(); out += cards(b)
        elif b['t'] == 'h2': flush(); cur = b['x']
        else:
            if cur is None: cur = ''; 
            body += one(b)
    flush()
    return out.replace('<section class="gb"><h2></h2>', '<section class="gb"><span></span>')

def group_page(g):
    path = f'g/{g["id"]}.html'; pre = '../'
    its = items_of_group(g['id'])
    intro = group_intro_html(GI[g['id']], pre) if g['id'] in GI else article_html((g.get('intro') or {}).get('uk', ''))
    body = (f'<main id="top"><div class="w">{crumbs(pre, [(pre + "katalog.html", "Каталог"), (None, g["name"]["uk"])])}'
            f'<div class="gtop"><p class="eb">{E(SEC[g["section"]]["name"]["uk"])}</p><h1 class="pt">{E(g["name"]["uk"])}</h1>'
            f'<p class="lead">{E(g["lead"]["uk"])}</p></div>'
            f'<div class="gsl">{slider("Добрива цієї категорії", its, pre)}</div>'
            f'<div class="gintro">{intro}</div></div></main>')
    doc(path, f'{g["name"]["uk"]} — добрива GREENODIN', g['lead']['uk'], body, ld=[itemlist_ld(g['name']['uk'], its)])

# ---------- головна ----------
def index_page():
    pre = ''
    first_group = {s['id']: next(g['id'] for g in GROUPS if g['section'] == s['id']) for s in SECTIONS}
    tiles = ''.join(f'<a class="t" href="#g-{first_group[s["id"]]}"><span class="ti">{svg(SEC_ICON[s["id"]])}</span><b>{E(s["name"]["uk"])}</b><span>{E(SEC_SUB[s["id"]])}</span></a>' for s in SECTIONS)
    chips = ''.join(f'<a class="c" draggable="false" href="#g-{g["id"]}">{E(g["name"]["uk"])}</a>' for g in GROUPS)
    cat = ''.join(slider(g['name']['uk'], items_of_group(g['id']), pre, SEC[g['section']]['name']['uk'], g['id'], f'g/{g["id"]}.html') for g in GROUPS)
    S = CAT['site']['uk']; DOCS = S['docs']
    about_main = ('<div class="two"><p class="abl">GREENODIN — органо-мінеральне добриво української розробки. Його створив Інститут нанотехнологій та органічних продуктів «Авелайф» із Вінниці. Основа складу — природні компоненти, серед них глауконіт і леонардит. Без синтетичної хімії.</p>'
                  '<ul class="ls" style="margin:0"><li>Підходить для різних ґрунтів і культур</li><li>Окремий продукт під кожну культуру</li><li>Звіти випробувань НААН: пшениця, соняшник, суниця, часник, картопля, соя, кукурудза</li><li>Розробки підтверджено чотирма патентами України</li></ul></div>')
    about_diff = '<div class="abt">' + ''.join(f'<p>{E(x)}</p>' for x in S['about_diff']) + '</div>'
    about_tasks = '<ul class="bi">' + ''.join(f'<li>{svg("check")}<span>{E(x)}</span></li>' for x in S['about_tasks']) + '</ul>'
    pat_cards = ''.join(f'<a class="dc" href="patents.html#p{p["no"]}"><span class="dci"><img src="img/docs/patent-{p["no"]}-t.webp" alt="Патент України № {p["no"]}" loading="lazy" draggable="false"></span>'
                        f'<small>Патент № {p["no"]}</small><b>{E(p["title"])}</b></a>' for p in DOCS['patents'])
    pat_cards += ''.join(f'<a class="dc" href="patents.html#{c["id"]}"><span class="dci"><img src="img/docs/{c["pages"][0][0]}-t.webp" alt="{E(c["title"])}" loading="lazy" draggable="false"></span>'
                         f'<small>{E(c["sub"])}</small><b>{E(c["title"])}</b></a>' for c in DOCS['certs'])
    about_docs = (f'<div class="gh dgh"><span>Патенти та сертифікати</span><a class="more" href="patents.html">Усі документи</a>{ARROWS}</div><div class="sl">{pat_cards}</div>')
    about_tabs = tabs([('Про нас', about_main), (S['about_diff_title'], about_diff), (S['about_tasks_title'], about_tasks), ('Патенти та сертифікати', about_docs)])
    why_html = ''.join(f'<article class="wc"><span class="ic">{svg(w["icon"])}</span><span class="fig">{E(w["figure"])}</span><b>{E(w["title"])}</b><p>{E(w["text"])}</p></article>' for w in S['why'])
    body = f'''<main id="top">
<div class="hero"><img class="hbg" src="img/hero.jpg" alt="" draggable="false"><div class="w"><h1>Органічні добрива для кожної культури</h1>
<p>Від пшениці й картоплі до орхідей і газону. Оберіть культуру й дізнайтеся, як і скільки вносити.</p>
<div class="r"><a class="btn" href="#catalog">Дивитися каталог</a><a class="btn o" href="#partners">Стати партнером</a></div></div></div>
<section style="padding:28px 0 4px"><div class="w"><div class="tl">{tiles}</div></div></section>
<section id="catalog"><div class="w"><div class="hrow"><h2>Продукція</h2><a class="more" href="katalog.html">Весь каталог списком →</a></div>
<label class="vh" for="q">Пошук у каталозі</label><input class="sr" id="q" type="search" placeholder="Знайти культуру: наприклад, помідори" autocomplete="off"></div>
<div class="tools"><div class="w"><div class="ch" id="fg">{chips}</div></div></div>
<div class="w"><p class="ct" id="ct" aria-live="polite"></p><div id="cat">{cat}</div></div></section>
<section id="about"><div class="w"><h2>Про GREENODIN</h2>{about_tabs}</div></section>
<section id="why"><div class="w"><div class="gh shd"><h2>{E(S["why_title"])}</h2>{ARROWS}</div><div class="sl wsl">{why_html}</div></div></section>
<section id="partners" class="dk"><div class="w"><h2>Партнерам</h2><div class="two">
<div><h3>Оптом</h3><p>Поставки для господарств і магазинів. Залиште контакти, і ми зв’яжемося з вами.</p><button class="btn" type="button" data-o="Оптові поставки">Запросити умови</button></div>
<div><h3>Стати партнером</h3><p>Для дистриб’юторів і представників у регіонах.</p><button class="btn" type="button" data-o="Партнерство">Залишити заявку</button></div></div></div></section>
<section id="contacts"><div class="w"><h2>Контакти</h2>
<ul class="ls"><li>Телефон<a href="tel:{PHONE}">{PHONE_T}</a></li><li>Пошта<a href="mailto:{EMAIL}">{EMAIL}</a></li><li>Адреса<span style="text-align:right">{ADDR}</span></li></ul>
<p class="r" style="margin:20px 0 0;display:flex;gap:10px;flex-wrap:wrap"><button class="btn k" type="button" data-o="Консультація">Залишити заявку</button><a class="btn o2" href="kontakty.html">Карта й усі контакти</a></p></div></section>
</main>
<dialog id="d" aria-labelledby="dt"><button class="x" id="dx" type="button" aria-label="Закрити">×</button>
<form id="fm" data-send novalidate><div class="hpf" aria-hidden="true"><label>Компанія<input name="company" tabindex="-1" autocomplete="off"></label></div><h3 id="dt">Заявка</h3><p id="dp"></p>
<label for="n">Ім’я</label><input class="f" id="n" autocomplete="name">
<label for="t">Телефон</label><input class="f" id="t" type="tel" autocomplete="tel" inputmode="tel" placeholder="+380 __ ___ __ __">
<div class="er" id="er" role="alert"></div><button class="btn" style="width:100%;border:0">Надіслати заявку</button></form>
<div id="ok" hidden><h3>Заявку прийнято</h3><p id="okp"></p><button class="btn k" id="oc" type="button" style="width:100%;border:0">Закрити</button></div></dialog>'''
    doc('index.html', 'Органічні добрива GREENODIN', 'Каталог органічних добрив GREENODIN для полів, саду, городу та квітів.', body, main=True,
        extra_js='<script src="assets/form.js"></script><script src="assets/home.js"></script>', ld=[{'@context': 'https://schema.org', **ORG}, {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'GREENODIN', 'url': SITE_URL, 'inLanguage': 'uk'}])

# ---------- патенти та сертифікати ----------
def patents_page():
    DOCS = CAT['site']['uk']['docs']; pre = ''
    def gal(pages, label):
        data = E(json.dumps([[f'img/docs/{f}.webp', t] for f, t in pages], ensure_ascii=False))
        thumbs = ''.join(f'<button type="button" class="pgb" data-i="{i}" aria-label="Відкрити: {E(label)}, {E(t)}"><img src="img/docs/{f}-t.webp" alt="" loading="lazy"><span>{E(t)}</span></button>' for i, (f, t) in enumerate(pages))
        return f'<div class="pgs" data-g="{data}" data-l="{E(label)}">{thumbs}</div>'
    certs = ''.join(f'<article class="dk2" id="{c["id"]}"><div class="dkh"><small>{E(c["sub"])}</small><h3>{E(c["title"])}</h3><p>{E(c["meta"])}</p></div>{gal(c["pages"], c["title"])}</article>' for c in DOCS['certs'])
    def pat(p):
        return (f'<article class="dk2" id="p{p["no"]}"><div class="dkh"><small>Патент України на корисну модель № {p["no"]} · {p["date"]}</small><h3>{E(p["title"])}</h3><p>{E(p["who"])}</p></div>'
                f'{gal(p["pages"], "Патент № " + p["no"])}</article>')
    pats = tabs([(f'{p["short"]} · {p["date"][-4:]}', pat(p)) for p in DOCS['patents']], 'pt')
    order = ['Пшениця озима', 'Соняшник', 'Суниця', 'Часник озимий', 'Картопля, соя, кукурудза', 'Рекультиванти']
    rs = sorted(DOCS['reports'], key=lambda r: order.index(r['crop']))
    def rep(r):
        res = f'<p class="res">{E(r["result"])}</p>' if r.get('result') else ''
        return (f'<article class="dk2" id="{r["id"]}"><div class="dkh"><small>Звіт про науково-дослідну роботу · {r["year"]}</small><h3>{E(r["title"])}</h3>'
                f'<p>{E(r["meta"])}</p>{res}</div>{gal(r["pages"], "Звіт " + r["year"] + " · " + r["crop"])}</article>')
    reps = tabs([(f'{r["crop"]} · {r["year"]}', rep(r)) for r in rs], 'rp')
    body = (f'<main id="top"><div class="w">{crumbs("", [(None, DOCS["title"])])}<div class="gtop"><h1 class="pt">{E(DOCS["title"])}</h1><p class="lead">{E(DOCS["lead"])}</p></div>'
            f'<nav class="dnav" aria-label="Розділи сторінки"><div class="ch"><a class="c" href="#certs">Сертифікати</a><a class="c" href="#pats">Патенти</a><a class="c" href="#reps">Звіти випробувань</a></div></nav>'
            f'<section id="certs"><h2>Сертифікати та членство</h2><div class="dks">{certs}</div></section>'
            f'<section id="pats"><h2>Патенти України</h2>{pats}</section>'
            f'<section id="reps"><h2>Звіти випробувань</h2>{reps}</section></div></main>'
            '<dialog id="lb" class="lb" aria-label="Перегляд документа"><div class="lbt"><span id="lbc"></span><button type="button" class="x" id="lbx" aria-label="Закрити">×</button></div>'
            '<div class="lbi"><img id="lbimg" alt=""></div><div class="lbn"><button type="button" class="ar" id="lbp" aria-label="Попередня сторінка">‹</button><span id="lbk"></span><button type="button" class="ar" id="lbn" aria-label="Наступна сторінка">›</button></div></dialog>')
    doc('patents.html', 'Патенти та сертифікати GREENODIN', DOCS['lead'], body, extra_js='<script src="assets/docs.js"></script>')


# ---------- сторінка каталогу ----------
def catalog_page():
    pre = ''
    allp = []
    secs = ''
    for s in SECTIONS:
        grs = ''
        for gr in [x for x in GROUPS if x['section'] == s['id']]:
            its = items_of_group(gr['id']); allp += its
            rows = ''
            for p in its:
                sers = p.get('recommended_series') if p['kind'] == 'crop_guide' else [p['series']] + [a['series'] for a in p.get('also_suitable', [])]
                ims = IMGS.get(p['slug'], [])
                im = f'<img src="{ims[0]}" alt="{E(img_alt(p))}" loading="lazy">' if ims else '<span class="noim"></span>'
                tags = ''.join(f'<i class="tgs" style="background:{COLOR[x]}">{x.upper()}</i>' for x in sers)
                ds = first_sentence(p['lead']['uk'], 140)
                rows += (f'<li data-s="{" ".join(sers)}"><a href="{page_of(p)}">{im}<span class="ci"><b>{E(p["name"]["uk"])}</b>'
                         f'<small>{E(ds)}</small></span><span class="ct2">{tags}</span>{svg("arrow")}</a></li>')
            grs += (f'<div class="kg"><h3><a href="g/{gr["id"]}.html">{E(gr["name"]["uk"])}</a> <small>{len(its)}</small></h3>'
                    f'<ul class="klist">{rows}</ul></div>')
        secs += f'<section class="ks" id="s-{s["id"]}"><h2>{E(s["name"]["uk"])}</h2><p class="hint">{E(s["lead"]["uk"])}</p>{grs}</section>'
    chips = '<button class="c on" type="button" data-f="">Усі лінійки</button>' + ''.join(f'<button class="c" type="button" data-f="{x}"><i class="dot" style="background:{COLOR[x]}"></i>{x.upper()}</button>' for x in LINE_ORDER)
    secnav = ''.join(f'<a class="c" href="#s-{s["id"]}">{E(s["name"]["uk"])}</a>' for s in SECTIONS)
    body = (f'<main id="top"><div class="w">{crumbs("", [(None, "Каталог")])}<div class="gtop"><h1 class="pt">Каталог органічних добрив GREENODIN</h1>'
            f'<p class="lead">Органо-мінеральні гранульовані добрива для полів, саду, городу, квітів і газону: {len(allp)} позицій. Оберіть розділ або лінійку, щоб швидко знайти потрібне добриво.</p></div>'
            f'<div class="kbar"><nav class="ch" aria-label="Розділи каталогу">{secnav}</nav><div class="ch" id="kf" role="group" aria-label="Фільтр за лінійкою">{chips}</div></div>'
            f'<p class="ct" id="kct" aria-live="polite"></p>{secs}</div></main>')
    js = """<script>(function(){var f=document.getElementById('kf'),ct=document.getElementById('kct');
f.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
[].forEach.call(f.children,function(x){x.classList.toggle('on',x===b)});var v=b.dataset.f,n=0;
[].forEach.call(document.querySelectorAll('.klist li'),function(li){var ok=!v||(' '+li.dataset.s+' ').indexOf(' '+v+' ')>-1;li.hidden=!ok;if(ok)n++});
[].forEach.call(document.querySelectorAll('.kg'),function(k){k.hidden=!k.querySelector('li:not([hidden])')});
[].forEach.call(document.querySelectorAll('.ks'),function(k){k.hidden=!k.querySelector('.kg:not([hidden])')});
ct.textContent=v?('Лінійка '+v.toUpperCase()+': '+n+' позицій'):'';});})();</script>"""
    doc('katalog.html', 'Каталог органічних добрив GREENODIN', f'Каталог органо-мінеральних гранульованих добрив GREENODIN: {len(allp)} позицій для полів, саду, городу, квітів і газону.',
        body, extra_js=js, ld=[itemlist_ld('Каталог органічних добрив GREENODIN', allp)])

def sitemap_xml():
    from datetime import date
    today = date.today().isoformat()
    urls = sorted(set(PAGES))
    pri = lambda p: '1.0' if p == 'index.html' else '0.9' if p == 'katalog.html' else '0.8' if p.startswith(('p/', 'k/')) else '0.7' if p.startswith('blog/') else '0.6'
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{SITE_URL}{"" if u == "index.html" else u}</loc><lastmod>{today}</lastmod><priority>{pri(u)}</priority></url>\n' for u in urls) + '</urlset>\n'
    open(OUT + '/sitemap.xml', 'w', encoding='utf-8').write(xml)
    open(OUT + '/robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n')


# ---------- контакти ----------
def contacts_page():
    q = urllib.parse.quote(MAP_Q)
    gmap = f'https://www.google.com/maps/search/?api=1&query={q}'
    embed = f'https://maps.google.com/maps?q={q}&z=16&hl=uk&output=embed'
    body = f'''<main id="top"><div class="w">{crumbs("", [(None, "Контакти")])}<h1 class="pt">Контакти</h1>
<p class="lead">Офіс GREENODIN у Вінниці. Телефонуйте, пишіть або залиште заявку: підберемо лінійку під культуру й ґрунт, розрахуємо норму та обсяг.</p>
<div class="cgrid">
<div class="cinfo">
<a class="cit" href="tel:{PHONE}">{svg("phone")}<span><small>Телефон</small><b>{PHONE_T}</b></span></a>
<a class="cit" href="mailto:{EMAIL}">{svg("mail")}<span><small>Пошта</small><b>{EMAIL}</b></span></a>
<a class="cit" href="{gmap}" target="_blank" rel="noopener">{svg("pin")}<span><small>Адреса офісу</small><b>{ADDR}</b></span></a>
<form class="cform" id="cf" data-send novalidate><div class="hpf" aria-hidden="true"><label>Компанія<input name="company" tabindex="-1" autocomplete="off"></label></div><h2>Написати нам</h2>
<label for="cn">Ім’я</label><input class="f" id="cn" autocomplete="name">
<label for="ct">Телефон</label><input class="f" id="ct" type="tel" autocomplete="tel" inputmode="tel" placeholder="+380 __ ___ __ __">
<label for="ce">Пошта <small>(необов’язково)</small></label><input class="f" id="ce" type="email" autocomplete="email">
<label for="cm">Повідомлення</label><textarea class="f" id="cm" rows="4" placeholder="Культура, площа, питання"></textarea>
<div class="er" id="cer" role="alert"></div><button class="btn" style="width:100%;border:0">Надіслати</button>
<p class="cok" id="cok" hidden></p></form>
</div>
<div class="cmap" id="cmap" data-src="{E(embed)}"><div class="cmph">{svg("pin")}<b>{ADDR}</b><a class="btn" href="{gmap}" target="_blank" rel="noopener">Відкрити в Google Maps</a></div></div>
</div></div></main>'''
    js = """<script>(function(){var m=document.getElementById('cmap');
if(!/claude|anthropic|usercontent/.test(location.hostname)){var f=document.createElement('iframe');f.src=m.dataset.src;f.title='Офіс GREENODIN на карті';f.loading='lazy';f.referrerPolicy='no-referrer-when-downgrade';f.allowFullscreen=true;m.appendChild(f);}
var F=document.getElementById('cf'),er=document.getElementById('cer'),ok=document.getElementById('cok'),bt=F.querySelector('button');
F.onsubmit=function(e){e.preventDefault();var n=F.cn.value.trim(),t=F.ct.value,d=t.replace(/\\D/g,'');
if(!n){er.textContent='Вкажіть ім’я';return}if(d.length<10){er.textContent='Введіть телефон повністю, не менше 10 цифр';return}
er.textContent='';bt.disabled=true;bt.textContent='Надсилаємо…';
gSend({topic:'Повідомлення зі сторінки «Контакти»',name:n,phone:t,email:F.ce.value.trim(),message:F.cm.value.trim(),company:F.company.value,ts:F.dataset.ts}).then(function(j){
bt.disabled=false;bt.textContent='Надіслати';if(!j.ok){er.textContent=j.error;return}
ok.textContent=n+', дякуємо! Ми зв’яжемося з вами найближчим часом.'+(j.demo?' (Демоверсія: у превʼю лист не надсилається.)':'');ok.hidden=false;F.reset();});};})();</script>"""
    ld = {'@context': 'https://schema.org', '@type': 'ContactPage', 'name': 'Контакти GREENODIN', 'url': SITE_URL + 'kontakty.html',
          'mainEntity': {'@type': 'LocalBusiness', 'name': 'GREENODIN', 'url': SITE_URL, 'telephone': PHONE, 'email': EMAIL, 'image': SITE_URL + 'img/logo.png',
                         'address': {'@type': 'PostalAddress', 'streetAddress': 'вул. Миколи Оводова, 51, корп. 1, 5 поверх', 'addressLocality': 'Вінниця', 'addressCountry': 'UA'},
                         'hasMap': gmap}}
    doc('kontakty.html', 'Контакти GREENODIN — офіс у Вінниці', f'Телефон {PHONE_T}, пошта {EMAIL}, адреса офісу GREENODIN: {ADDR}. Карта проїзду та форма зв’язку.', body, extra_js='<script src="assets/form.js"></script>'+js, ld=[ld])

# ---------- карта сайту ----------
def sitemap():
    pre = ''
    secs = ''
    for s in SECTIONS:
        gs = ''.join(f'<li><a href="g/{g["id"]}.html"><b>{E(g["name"]["uk"])}</b></a><ul>' + ''.join(f'<li><a href="{page_of(p)}">{E(p["name"]["uk"])}</a></li>' for p in items_of_group(g['id'])) + '</ul></li>' for g in GROUPS if g['section'] == s['id'])
        secs += f'<div><h2>{E(s["name"]["uk"])}</h2><ul class="smap">{gs}</ul></div>'
    secs = '<div><h2>Каталог</h2><ul class="smap"><li><a href="katalog.html"><b>Каталог органічних добрив</b></a></li></ul></div>' + secs
    secs += '<div><h2>Про компанію</h2><ul class="smap"><li><a href="patents.html"><b>Патенти та сертифікати</b></a></li><li><a href="./#about"><b>Про GREENODIN</b></a></li><li><a href="kontakty.html"><b>Контакти</b></a></li></ul></div>'
    body = f'<main id="top"><div class="w">{crumbs("", [(None, "Карта сайту")])}<h1 class="pt">Карта сайту</h1><div class="smg">{secs}</div></div></main>'
    doc('sitemap.html', 'Карта сайту GREENODIN — усі сторінки каталогу', 'Усі сторінки сайту GREENODIN: розділи й групи каталогу, сторінки добрив для кожної культури, лінійки, патенти, сертифікати та контакти.', body)

for p in PRODUCTS:
    (line_page if p['kind'] == 'line' else product_page)(p)
for p in FIELDS: field_page(p)
for g in GROUPS: group_page(g)
index_page(); sitemap(); patents_page(); catalog_page(); contacts_page()
import blog; BLOG = blog.run(globals())
sitemap_xml()

# ---------- vercel.json: заголовки + 301 зі старого сайту ----------
def vercel_json():
    src = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'redirects_src.json'), encoding='utf-8'))
    by_slug = {p['slug']: page_of(p) for p in PRODUCTS + FIELDS}
    reds, seen = [], set()
    for old, new, kind in src:
        path = urllib.parse.urlparse(old).path.rstrip('/') or '/'
        if new.startswith('група '): dst = '/g/' + new.split()[1] + '.html'
        elif new.endswith('.html'): dst = new
        else:
            slug = new.strip('/')
            if slug not in by_slug: print('redirect: нема сторінки для', new); continue
            dst = '/' + by_slug[slug]
        for sp in {path, path + '/'} - {'//'}:
            if sp in seen: continue
            seen.add(sp); reds.append({'source': sp, 'destination': dst, 'permanent': True})
    OLDBLOG = {'viznachennya-kislotnosti-gruntu': '/blog/ph-gruntu.html'}
    for sl in ['sivozmina', 'yak-ekonomiti-na-mineralnih-dobrivah', 'viroshchuvannya-chasniku', 'leonardit-organchna-skladova-dobriv-greenodin',
               'gidrogeli-i-prirodni-silikati-u-silskomu-gospodarstvi', 'ekonomiya-vodi-z-dobrivami-greenodin', 'skorochennya-zastosuvannya-mineralnih-dobriv',
               'priskorennya-zrostannya-kultur', 'zbilshennya-vrozhaynosti', 'zbilshennya-cinnost-vrozhayu-za-rahunok-organichnosti',
               'tendentsiji-ta-investytsijni-mozhlyvosti-dovgostrokovyh-perspektyv-organichnogo-zemlerobstva', 'suchasn-pidhodi-zabezpechennya-stalogo-silgospvirobnictva',
               'ekologizacya-silskogo-gospodarstva-ta-ekologchne-pidpriemnictvo', 'rodyuchi-grunti-movchazna-zhertva-konfliktiv',
               'podolannja-vplyvu-bojeprypasiv-na-rodjuchi-grunty', 'ekocid-ukraines-naslidki-boyovih-dy-strateg-vidnovlennya',
               'dorozhne-gospodarstvo-ta-blagoustrij-mista', 'blog/page-2']:
        OLDBLOG.setdefault(sl, '/blog/')   # тимчасово на індекс, поки статтю не перенесено
    OLDBLOG['viroshchuvannya-chasniku'] = '/blog/'
    for sl, dst in OLDBLOG.items():
        for sp in ('/' + sl, '/' + sl + '/'):
            if sp not in seen: seen.add(sp); reds.append({'source': sp, 'destination': dst, 'permanent': True})
    cfg = {'outputDirectory': 'public', 'redirects': reds, 'headers': [
        {'source': '/assets/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=604800'}]},
        {'source': '/ru/assets/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=604800'}]},
        {'source': '/en/assets/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=604800'}]},
        {'source': '/img/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=2592000, immutable'}]},
        {'source': '/(.*)', 'headers': [{'key': 'X-Content-Type-Options', 'value': 'nosniff'}, {'key': 'Referrer-Policy', 'value': 'strict-origin-when-cross-origin'}]}]}
    json.dump(cfg, open(os.path.join(REPO, 'vercel.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('redirects:', len(reds))
vercel_json()
print('pages:', len(glob.glob(OUT + '/**/*.html', recursive=True)))
