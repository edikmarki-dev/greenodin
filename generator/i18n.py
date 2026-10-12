"""Мовні версії GREENODIN (ru, en) з українського сайту.
1) python3 gen.py   — будує uk у public/
2) python3 i18n.py extract — збирає всі українські фрагменти → tr/segments.json (+ tr/missing_<lang>.json)
3) python3 i18n.py build   — створює /ru/ і /en/, hreflang, перемикач мови, sitemap
Переклади: tr/ru.json, tr/en.json — словник {український фрагмент: переклад}."""
import os, re, sys, json, glob, shutil, html as H
from bs4 import BeautifulSoup, NavigableString, Comment

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('GREENODIN_OUT', os.path.join(os.path.dirname(HERE), 'public'))
FULL_INDEX = os.path.join(HERE, 'build', 'site_index_full.html')
TR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tr')
LANGS = ['ru', 'en']
UK_ONLY = ('blog/',)   # сторінки без перекладу: лише українська, без hreflang
CYR = re.compile(r'[А-Яа-яІіЇїЄєҐґ’]')
ATTRS = ('alt', 'title', 'aria-label', 'placeholder', 'data-o', 'data-n', 'data-l')
META_NAMES = {'description', 'og:title', 'og:description', 'twitter:title', 'twitter:description'}
JS_LIT = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"")

def pages():
    out = []
    for f in sorted(glob.glob(SITE + '/**/*.html', recursive=True)):
        rel = os.path.relpath(f, SITE)
        if rel.split('/')[0] in LANGS or rel.startswith(UK_ONLY): continue
        src = FULL_INDEX if rel == 'index.html' else f
        out.append((rel, open(src, encoding='utf-8').read()))
    return out

def js_strings(code):
    for m in JS_LIT.finditer(code):
        s = m.group(1) if m.group(1) is not None else m.group(2)
        if s and CYR.search(s): yield s

def ld_strings(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ('@type', '@context', 'url', 'item', 'image', 'sku', 'telephone', 'email', '@id', 'hasMap', 'logo', 'inLanguage'): continue
            yield from ld_strings(v)
    elif isinstance(o, list):
        for v in o: yield from ld_strings(v)
    elif isinstance(o, str) and CYR.search(o): yield o

def segments_of(doc):
    """yield українські фрагменти сторінки у порядку появи"""
    soup = BeautifulSoup(doc, 'html.parser')
    for el in soup.descendants:
        if isinstance(el, Comment): continue
        if isinstance(el, NavigableString):
            p = el.parent.name if el.parent else ''
            if p == 'style': continue
            if p == 'script':
                t = el.parent.get('type', '')
                if t == 'application/ld+json':
                    try: yield from ld_strings(json.loads(str(el)))
                    except Exception: pass
                else: yield from js_strings(str(el))
                continue
            s = str(el).strip()
            if s and CYR.search(s): yield s
        elif el.name:
            for a in ATTRS:
                v = el.get(a)
                if v and CYR.search(v):
                    if a == 'data-g':
                        continue
                    yield v.strip()
            if el.name == 'meta':
                k = el.get('name') or el.get('property')
                if k in META_NAMES and el.get('content') and CYR.search(el['content']): yield el['content'].strip()
            dg = el.get('data-g')
            if dg:
                try:
                    for _, cap in json.loads(dg):
                        if CYR.search(cap): yield cap
                except Exception: pass

def load(lang):
    p = f'{TR}/{lang}.json'
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}

def extract():
    order, seen = [], set()
    for rel, doc in pages():
        for s in segments_of(doc):
            if s not in seen: seen.add(s); order.append(s)
    for f in sorted(glob.glob(SITE + '/assets/*.js')):
        for s in js_strings(open(f, encoding='utf-8').read()):
            if s not in seen: seen.add(s); order.append(s)
    json.dump(order, open(f'{TR}/segments.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for L in LANGS:
        d = load(L); miss = [s for s in order if s not in d]
        json.dump(miss, open(f'{TR}/missing_{L}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(L, 'segments', len(order), 'missing', len(miss), 'chars', sum(map(len, miss)))


# ---------------------------------------------------------------- build
SITE_URL = None
def site_url():
    global SITE_URL
    if SITE_URL is None:
        m = re.search(r"^SITE_URL\s*=\s*'([^']+)'", open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen.py'), encoding='utf-8').read(), re.M)
        SITE_URL = m.group(1)
    return SITE_URL

ALL = ['uk'] + LANGS
LOCALE = {'uk': 'uk_UA', 'ru': 'ru_RU', 'en': 'en_US'}
LABEL = {'uk': 'UA', 'ru': 'RU', 'en': 'EN'}
SW_ARIA = {'uk': 'Мова сайту', 'ru': 'Язык сайта', 'en': 'Site language'}
LANG_NAME = {'uk': 'Українська', 'ru': 'Русский', 'en': 'English'}
MISSING = {}

class Tr:
    def __init__(self, lang):
        self.lang = lang; self.d = load(lang)
        self.s = {}
        for k, v in self.d.items():
            self.s.setdefault(k.strip(), v.strip())
    def __call__(self, text):
        """text -> переклад із збереженням крайових пробілів"""
        if text in self.d: return self.d[text]
        st = text.strip()
        if st in self.s:
            lead = text[:len(text) - len(text.lstrip())]; trail = text[len(text.rstrip()):]
            return lead + self.s[st] + trail
        if CYR.search(text): MISSING.setdefault(self.lang, set()).add(text)
        return text

def tr_js(code, T):
    def rep(m):
        s, q = (m.group(1), "'") if m.group(1) is not None else (m.group(2), '"')
        if not s or not CYR.search(s): return m.group(0)
        t = T(s)
        t = re.sub(r'(?<!\\)' + q, '\\\\' + q, t)
        return q + t + q
    return JS_LIT.sub(rep, code)

def tr_ld(o, T, lang):
    S = site_url()
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k in ('@type', '@context', 'sku', 'telephone', 'email', '@id', 'hasMap', 'logo', 'image'): out[k] = v
            elif k == 'inLanguage': out[k] = lang
            else: out[k] = tr_ld(v, T, lang)
        return out
    if isinstance(o, list): return [tr_ld(v, T, lang) for v in o]
    if isinstance(o, str):
        if o.startswith(S):
            return o if o.startswith(S + 'img/') else S + lang + '/' + o[len(S):]
        return T(o) if CYR.search(o) else o
    return o

SHARED = re.compile(r'^(img/|favicon\.ico$|site\.webmanifest$|assets/style\.css$)')
def fix_url(u):
    """відносне посилання на спільний ресурс у кореневій теці → додаємо ../"""
    if re.match(r'^(https?:|mailto:|tel:|#|/|data:|javascript:)', u) or not u: return u
    core = re.sub(r'^(\.\./)+', '', u)
    if SHARED.match(core): return '../' + u
    return u

def lang_url(rel, lang, S=None):
    """абсолютний URL сторінки rel у мові lang"""
    S = S or site_url()
    out = '' if rel == 'index.html' else rel
    return S + ('' if lang == 'uk' else lang + '/') + out

def switch_href(rel, cur, to):
    depth = rel.count('/') + (0 if cur == 'uk' else 1)
    return '../' * depth + ('' if to == 'uk' else to + '/') + rel

GLOBE = '<svg aria-hidden="true" class="lsg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 4 5.7 4 9s-1.4 6.4-4 9c-2.6-2.6-4-5.7-4-9s1.4-6.4 4-9z"/></svg>'
CHEV = '<svg aria-hidden="true" class="chev" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>'
def make_switcher(soup, rel, cur, cls):
    html = [f'<div class="lsd {cls}" id="lsd" data-lsw><button class="lsb" type="button" aria-haspopup="true" aria-expanded="false" aria-controls="lsm" aria-label="{SW_ARIA[cur]}">{GLOBE}<span>{LABEL[cur]}</span>{CHEV}</button><ul class="lsm" id="lsm">']
    for L in ALL:
        on = ' class="on" aria-current="true"' if L == cur else ''
        html.append(f'<li><a{on} data-lang="{L}" href="{switch_href(rel, cur, L)}" hreflang="{L}" lang="{L}"><b>{LABEL[L]}</b>{LANG_NAME[L]}</a></li>')
    html.append('</ul></div>')
    return BeautifulSoup(''.join(html), 'html.parser').div

def add_alt_links(soup, rel):
    for l in soup.find_all('link', rel='alternate'):
        if l.get('hreflang'): l.decompose()
    can = soup.find('link', rel='canonical')
    if not can: return
    prev = can
    for L in ALL + ['x-default']:
        href = lang_url(rel, 'uk' if L == 'x-default' else L)
        t = soup.new_tag('link', rel='alternate', hreflang=L, href=href)
        prev.insert_after(t); prev = t
    # og:locale:alternate
    cur = soup.find('meta', property='og:locale')
    for m in soup.find_all('meta', property='og:locale:alternate'): m.decompose()
    if cur:
        prev = cur
        for L in ALL:
            if LOCALE[L] != cur.get('content'):
                t = soup.new_tag('meta', property='og:locale:alternate', content=LOCALE[L]); prev.insert_after(t); prev = t

def process(doc, rel, lang):
    """doc — українська сторінка; повертає html для мови lang (uk — лише hreflang і перемикач)"""
    S = site_url()
    soup = BeautifulSoup(doc, 'html.parser')
    T = Tr(lang) if lang != 'uk' else None
    for x in soup.select('.lsw, .lsd'): x.decompose()
    if lang != 'uk':
        for el in list(soup.descendants):
            if isinstance(el, Comment): continue
            if isinstance(el, NavigableString):
                p = el.parent.name if el.parent else ''
                if p == 'style': continue
                if p == 'script':
                    t = el.parent.get('type', '')
                    if t == 'application/ld+json':
                        try:
                            new = json.dumps(tr_ld(json.loads(str(el)), T, lang), ensure_ascii=False).replace('</', '<\\/')
                            el.replace_with(el.__class__(new))
                        except Exception as e: print('ld err', rel, e)
                    else:
                        new = tr_js(str(el), T)
                        if new != str(el): el.replace_with(el.__class__(new))
                    continue
                s = str(el)
                if CYR.search(s): el.replace_with(NavigableString(T(s)))
            elif getattr(el, 'name', None):
                for a in ATTRS:
                    v = el.get(a)
                    if v and CYR.search(v): el[a] = T(v)
                if el.name == 'meta':
                    k = el.get('name') or el.get('property')
                    if k in META_NAMES and el.get('content') and CYR.search(el['content']): el['content'] = T(el['content'])
                    if k == 'og:locale': el['content'] = LOCALE[lang]
                    if k in ('og:url',): el['content'] = lang_url(rel, lang)
                if el.name == 'link' and el.get('rel') == ['canonical']: el['href'] = lang_url(rel, lang)
                dg = el.get('data-g')
                if dg:
                    try:
                        el['data-g'] = json.dumps([[fix_url(p), T(c) if CYR.search(c) else c] for p, c in json.loads(dg)], ensure_ascii=False)
                    except Exception as e: print('data-g err', rel, e)
                for a in ('href', 'src', 'srcset', 'poster'):
                    v = el.get(a)
                    if v:
                        if a == 'srcset': el[a] = ', '.join(fix_url(x.strip().split(' ')[0]) + (' ' + x.strip().split(' ', 1)[1] if ' ' in x.strip() else '') for x in v.split(','))
                        else: el[a] = fix_url(v)
                ds = el.get('data-src')
                if ds and 'maps.google' in ds: el['data-src'] = ds.replace('hl=uk', 'hl=' + lang)
        h = soup.find('html')
        if h: h['lang'] = lang
    # перемикач і hreflang
    for x in soup.select('.lsw, .lsd'): x.decompose()
    hb = soup.select_one('header .hb')
    if hb:
        bg = hb.select_one('.bg')
        sw = make_switcher(soup, rel, lang, 'lh')
        (bg.insert_before(sw) if bg else hb.append(sw))
    m = soup.select_one('header #m')
    add_alt_links(soup, rel)
    out = str(soup)
    if lang != 'uk':
        out = out.replace('<html lang="uk"', f'<html lang="{lang}"')
    return out

CSS_MARK = '/* i18n-switcher */'
CSS = CSS_MARK + """
.lsd{position:relative;flex:none;margin-right:10px}
.lsb{display:inline-flex;align-items:center;gap:6px;background:none;border:1px solid #ffffff55;color:#fff;border-radius:8px;padding:6px 10px;font:inherit;font-size:13px;font-weight:700;letter-spacing:.04em;cursor:pointer;line-height:1.2}
.lsb:hover,.lsd.o .lsb{background:#ffffff22}
.lsg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;flex:none}
.lsb .chev{width:14px;height:14px;transition:transform .15s}
.lsd.o .chev{transform:rotate(180deg)}
.lsm{display:none;position:absolute;right:0;top:calc(100% + 8px);z-index:30;min-width:176px;margin:0;padding:6px;list-style:none;background:var(--bg);color:var(--tx);border:1px solid var(--ln);border-radius:12px;box-shadow:0 14px 34px rgba(0,0,0,.18)}
.lsd.o .lsm{display:block}
.lsm a{display:flex;align-items:center;gap:10px;padding:9px 10px;border-radius:8px;color:var(--tx);text-decoration:none;font-size:15px;font-weight:500;margin:0}
.lsm a b{width:26px;font-size:12px;letter-spacing:.05em;color:var(--mu)}
.lsm a:hover{background:var(--card)}
.lsm a.on{color:var(--g);font-weight:700}.lsm a.on b{color:var(--g)}
header nav .lsm a{margin:0}
/* шапка: до 1099px — телефон, мова, гамбургер; від 1100px — меню і мова скраю справа */
.bg{display:inline-grid;place-items:center;width:42px;height:40px;padding:0;border:1px solid #ffffff55;border-radius:8px;cursor:pointer}
.bgl{position:relative;display:block;width:20px;height:14px}
.bgl i{position:absolute;left:0;width:100%;height:2px;border-radius:2px;background:#fff;transition:transform .28s cubic-bezier(.2,.7,.2,1),opacity .18s,top .28s cubic-bezier(.2,.7,.2,1)}
.bgl i:nth-child(1){top:0}.bgl i:nth-child(2){top:6px}.bgl i:nth-child(3){top:12px}
.bg[aria-expanded="true"] .bgl i:nth-child(1){top:6px;transform:rotate(45deg)}
.bg[aria-expanded="true"] .bgl i:nth-child(2){opacity:0;transform:scaleX(.2)}
.bg[aria-expanded="true"] .bgl i:nth-child(3){top:6px;transform:rotate(-45deg)}
.hph{display:inline-flex;margin-left:auto}
header nav{display:none}
#m:not(.o){display:none!important}#m.o{display:block!important}
@media(min-width:1100px){header nav{display:block;margin-left:auto}.hph,.bg{display:none}.lsd{margin:0 0 0 22px}#m,#m.o{display:none!important}}
@media(prefers-reduced-motion:reduce){.bgl i{transition:none}}
"""

# ---------- посилання у тексті: телефон, пошта, назви сторінок ----------
PHONE_RE = re.compile(r'\+38\s?043\s?250\s?90\s?90')
MAIL_RE = re.compile(r'office@avelife\.pro')
PAGE_LINKS = {
    'uk': [('Патенти та сертифікати', 'patents.html'), ('Контакти', 'kontakty.html')],
    'ru': [('Патенты и сертификаты', 'patents.html'), ('Контакты', 'kontakty.html')],
    'en': [('Patents and certificates', 'patents.html'), ('Contacts', 'kontakty.html')],
}
PAGE_CTX = {  # слово «сторінка» поруч — ознака згадки саме сторінки сайту
    'uk': r'(?:сторінці|сторінка|сторінки|сторінку)\s+«{n}»', 'ru': r'(?:странице|страница|страницы|страницу)\s+«{n}»',
    'en': r'{n}\s+page'}
def linkify_html(doc, rel, lang):
    soup = BeautifulSoup(doc, 'html.parser')
    pre = '../' * rel.count('/')
    ch = False
    for el in list(soup.descendants):
        if not isinstance(el, NavigableString) or isinstance(el, Comment): continue
        if el.find_parent(['a', 'script', 'style', 'title', 'button', 'textarea', 'option', 'head']): continue
        s = str(el)
        pats = [(PHONE_RE, lambda m: ('tel:+380508243279', m.group(0))), (MAIL_RE, lambda m: ('mailto:office@avelife.pro', m.group(0)))]
        for name, href in PAGE_LINKS[lang]:
            pats.append((re.compile(PAGE_CTX[lang].format(n=re.escape(name))), (lambda nm, hf: lambda m: (pre + hf, nm, m))(name, href)))
        hits = []
        for rx, fn in pats:
            for m in rx.finditer(s):
                r = fn(m)
                if len(r) == 2: hits.append((m.start(), m.end(), r[0], r[1]))
                else:
                    a = m.group(0).find(r[1]); hits.append((m.start() + a, m.start() + a + len(r[1]), r[0], r[1]))
        if not hits: continue
        hits.sort()
        parts, pos = [], 0
        for a, b, href, text in hits:
            if a < pos: continue
            parts.append(NavigableString(s[pos:a]))
            t = soup.new_tag('a', href=href); t.string = text; parts.append(t); pos = b
        parts.append(NavigableString(s[pos:]))
        for p in reversed(parts): el.insert_after(p)
        el.extract(); ch = True
    return str(soup) if ch else doc

def linkify_all():
    for f in sorted(glob.glob(SITE + '/**/*.html', recursive=True)):
        rel = os.path.relpath(f, SITE)
        lang = rel.split('/')[0] if rel.split('/')[0] in LANGS else 'uk'
        if lang != 'uk': rel = rel.split('/', 1)[1]
        doc = open(f, encoding='utf-8').read()
        new = linkify_html(doc, rel, lang)
        if new != doc: open(f, 'w', encoding='utf-8').write(new)
    f = FULL_INDEX
    doc = open(f, encoding='utf-8').read(); new = linkify_html(doc, 'index.html', 'uk')
    if new != doc: open(f, 'w', encoding='utf-8').write(new)

def build():
    S = site_url()
    # CSS перемикача (один раз)
    cp = SITE + '/assets/style.css'
    css = open(cp, encoding='utf-8').read()
    css = css.split(CSS_MARK)[0].rstrip()
    open(cp, 'w', encoding='utf-8').write(css + '\n' + CSS)
    for L in LANGS: shutil.rmtree(f'{SITE}/{L}', ignore_errors=True)
    urls = []
    # українські сторінки: hreflang + перемикач на місці
    for f in sorted(glob.glob(SITE + '/**/*.html', recursive=True)):
        rel = os.path.relpath(f, SITE)
        if rel.split('/')[0] in LANGS or rel.startswith(UK_ONLY): continue
        doc = open(f, encoding='utf-8').read()
        open(f, 'w', encoding='utf-8').write(process(doc, rel, 'uk'))
        urls.append(rel)
    full = open(FULL_INDEX, encoding='utf-8').read()
    open(FULL_INDEX, 'w', encoding='utf-8').write(process(full, 'index.html', 'uk'))
    # переклади
    for L in LANGS:
        for rel in urls:
            src = FULL_INDEX if rel == 'index.html' else f'{SITE}/{rel}'
            out = process(open(src, encoding='utf-8').read(), rel, L)
            dst = f'{SITE}/{L}/{rel}'; os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'w', encoding='utf-8').write(out)
        # скрипти
        os.makedirs(f'{SITE}/{L}/assets', exist_ok=True)
        T = Tr(L)
        for f in sorted(glob.glob(SITE + '/assets/*.js')):
            open(f'{SITE}/{L}/assets/' + os.path.basename(f), 'w', encoding='utf-8').write(tr_js(open(f, encoding='utf-8').read(), T))
    linkify_all()
    # sitemap з alternates
    from datetime import date
    today = date.today().isoformat()
    pri = lambda p: '1.0' if p == 'index.html' else '0.9' if p == 'katalog.html' else '0.8' if p.startswith(('p/', 'k/')) else '0.6'
    rows = []
    for rel in sorted(set(urls)):
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{L}" href="{lang_url(rel, L)}"/>' for L in ALL) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{lang_url(rel, "uk")}"/>'
        for L in ALL:
            rows.append(f'  <url><loc>{lang_url(rel, L)}</loc><lastmod>{today}</lastmod><priority>{pri(rel)}</priority>{alts}</url>\n')
    for f in sorted(glob.glob(SITE + '/blog/*.html')):
        rel = os.path.relpath(f, SITE)
        rows.append(f'  <url><loc>{lang_url(rel, "uk")}</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>\n')
    open(SITE + '/sitemap.xml', 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + ''.join(rows) + '</urlset>\n')
    n = sum(len(v) for v in MISSING.values())
    print('pages', len(urls), 'x', len(ALL), '| untranslated:', {k: len(v) for k, v in MISSING.items()})
    for k, v in MISSING.items():
        for s in sorted(v)[:15]: print(' ', k, repr(s[:100]))

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'extract'
    {'extract': extract, 'build': build}[cmd]()
