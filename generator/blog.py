"""Блог GREENODIN: статті з generator/data/blog/*.md → public/blog/*.html.
Викликається з gen.py: blog.run(globals()).

Формат статті: YAML front matter + markdown. Заголовки H2 з явними id: `## Текст {#id}`.
Обов'язкові поля: slug, title, desc, section, cluster, published, updated, minutes, short, faq.
Необов'язкові: seo_title, cover (файл у static/img/blog/), cover_alt, related, product, sources, old, series_order.
"""
import os, re, json, glob, html as H
import yaml, markdown

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'data', 'blog')
AUTHOR = {'name': 'Тимур Лєвда', 'initials': 'ТЛ', 'photo': 'img/blog/author-levda.webp',
          'job': 'Директор НВ ТОВ «СІНТА», розробник органічних добрив ТМ GREENODIN'}
SECTIONS = ['Практика агронома', 'Вирощування культур']
E = lambda s: H.escape(str(s or ''), quote=True)
MONTHS = ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']

ICONS = {  # прості лінійні іконки для обкладинок-заглушок
    'ph': '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M8 15h8"/>',
    'potato': '<ellipse cx="12" cy="13" rx="8" ry="6"/><path d="M8 11h.01M13 10h.01M15 14h.01M10 15h.01"/><path d="M12 7c0-2 1-3 3-4"/>',
    'leaf': '<path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15"/><path d="M5 19c3-5 6-8 11-10"/>',
    'rotation': '<path d="M20 12a8 8 0 0 0-14-5.3L4 9"/><path d="M4 4v5h5"/><path d="M4 12a8 8 0 0 0 14 5.3L20 15"/><path d="M20 20v-5h-5"/>',
}

def human_date(iso):
    y, m, d = map(int, iso.split('-'))
    return f'{d} {MONTHS[m - 1]} {y}'

def load_articles():
    arts = []
    for f in sorted(glob.glob(os.path.join(SRC, '*.md'))):
        raw = open(f, encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
        if not m: raise SystemExit(f'blog: немає front matter у {f}')
        meta = yaml.safe_load(m.group(1)); body = m.group(2).strip()
        for k in ('slug', 'title', 'desc', 'section', 'cluster', 'published', 'updated', 'minutes', 'short', 'faq'):
            if k not in meta: raise SystemExit(f'blog: у {f} немає поля {k}')
        meta['published'] = str(meta['published']); meta['updated'] = str(meta['updated'])
        md = markdown.Markdown(extensions=['tables', 'attr_list', 'sane_lists'])
        meta['html'] = md.convert(body).replace('<table>', '<div class="bl-tw"><table>').replace('</table>', '</table></div>')
        meta['heads'] = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', meta['html'])
        meta['words'] = len(re.findall(r'\w+', body))
        meta['_file'] = f
        arts.append(meta)
    arts.sort(key=lambda a: (a['cluster'], a.get('series_order', 99)))
    arts.sort(key=lambda a: a['published'], reverse=True)
    return arts

def run(G):
    doc, crumbs, ld_script, SITE_URL, ORG = G['doc'], G['crumbs'], G['ld_script'], G['SITE_URL'], G['ORG']
    PAGES, OUT = G['PAGES'], G['OUT']
    arts = load_articles()
    by = {a['slug']: a for a in arts}
    url_of = lambda a: f'blog/{a["slug"]}.html'

    def cover(a, pre, cls='bl-cv', sizes=''):
        if a.get('cover'):
            return f'<img class="{cls}" src="{pre}img/blog/{a["cover"]}" alt="{E(a.get("cover_alt", a["title"]))}" loading="lazy" decoding="async">'
        ic = ICONS.get(a.get('icon', 'leaf'), ICONS['leaf'])
        return (f'<div class="{cls} bl-ph" role="img" aria-label="{E(a.get("cover_alt", a["title"]))}">'
                f'<svg viewBox="0 0 24 24" aria-hidden="true">{ic}</svg><span>{E(a["section"])}</span></div>')

    def card(a, pre):
        return (f'<a class="bl-card" href="{pre}{url_of(a)}">{cover(a, pre, "bl-cv")}'
                f'<div class="bl-cb"><span class="bl-tag">{E(a["section"])}</span><h3>{E(a["title"])}</h3>'
                f'<p>{E(a["desc"])}</p><span class="bl-meta">{AUTHOR["name"]} · {a["minutes"]} хв читання</span></div></a>')

    def article_ld(a, pre):
        url = SITE_URL + url_of(a)
        d = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['desc'],
             'inLanguage': 'uk', 'datePublished': a['published'], 'dateModified': a['updated'],
             'mainEntityOfPage': {'@type': 'WebPage', '@id': url}, 'url': url,
             'articleSection': a['section'], 'wordCount': a['words'],
             'author': {'@type': 'Person', 'name': AUTHOR['name'], 'jobTitle': 'Директор', 'image': SITE_URL + AUTHOR['photo'],
                        'worksFor': {'@type': 'Organization', 'name': 'НВ ТОВ «СІНТА»'}, 'description': AUTHOR['job']},
             'publisher': ORG}
        if a.get('cover'): d['image'] = [SITE_URL + 'img/blog/' + a['cover']]
        else: d['image'] = [SITE_URL + 'img/hero.jpg']
        faq = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', q['a'])}} for q in a['faq']]}
        return [d, faq]

    def article_page(a):
        pre = '../'
        sib = [x for x in arts if x['cluster'] == a['cluster']]
        sib.sort(key=lambda x: x.get('series_order', 99))
        toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in a['heads'] + [('faq', 'Часті запитання')])
        series = ''
        if len(sib) > 1:
            def li(x):
                t = E(x.get('short_title') or x['title'])
                return f'<li><b>{t}</b></li>' if x is a else f'<li><a href="{pre}{url_of(x)}">{t}</a></li>'
            items = ''.join(li(x) for x in sib)
            series = f'<div class="bl-box"><div class="bl-lab">{E(a.get("series_name", "Серія"))}</div><ol class="bl-ser">{items}</ol></div>'
        short = ''.join(f'<li>{s}</li>' for s in a['short'])
        faq = ''.join(f'<details><summary>{E(q["q"])}<span class="bl-pl" aria-hidden="true">+</span></summary><p>{q["a"]}</p></details>' for q in a['faq'])
        prod = ''
        if a.get('product'):
            p = a['product']
            prod = (f'<aside class="bl-prod"><div><div class="bl-lab bl-lab-l">{E(p.get("label", "Підібрати добриво"))}</div><p>{p["text"]}</p></div>'
                    f'<a class="bl-btn" href="{pre}{p["href"]}">{E(p.get("btn", "До продукту"))}</a></aside>')
        src = ''
        if a.get('sources'):
            src = '<section class="bl-src"><h2 class="bl-lab">Джерела</h2><ol>' + ''.join(f'<li>{s}</li>' for s in a['sources']) + '</ol></section>'
        rel = [by[s] for s in a.get('related', []) if s in by]
        relh = ''
        if rel:
            relh = f'<section class="bl-rel"><h2>Читайте також</h2><div class="bl-grid">{"".join(card(x, pre) for x in rel)}</div></section>'
        body_html = a['html']
        # продуктовий блок після першого H2-розділу, якщо задано after
        if prod and a.get('product', {}).get('after'):
            marker = f'<h2 id="{a["product"]["after"]}"'
            body_html = body_html.replace(marker, prod + marker, 1); prod = ''
        crumb = crumbs(pre, [(pre + 'blog/', 'Блог'), (pre + 'blog/', a['section']), (None, a.get('crumb') or a['title'])])
        sidebar = (f'<aside class="bl-side"><nav class="bl-box" aria-label="Зміст"><div class="bl-lab">У цій статті</div><ol class="bl-toc">{toc}</ol></nav>{series}'
                   f'<div class="bl-help"><b>Потрібна консультація?</b><p>Підкажемо добриво і норму під ваш ґрунт.</p>'
                   f'<a class="bl-btn bl-btn-w" href="{pre}kontakty.html">Зв’яжіться з нами</a></div></aside>')
        body = (f'<main class="bl"><div class="w">{crumb}'
                f'<div class="bl-hd"><span class="bl-tag">{E(a["section"])}</span><h1>{E(a["title"])}</h1><p class="bl-lead">{E(a["desc"])}</p>'
                f'<div class="bl-by"><img class="bl-av" src="{pre}{AUTHOR["photo"]}" alt="" width="44" height="44" decoding="async"><span><b>{AUTHOR["name"]}</b> · {E(AUTHOR["job"].split(",")[0])}</span>'
                f'<span class="bl-dot">·</span><span>Оновлено <time datetime="{a["updated"]}">{human_date(a["updated"])}</time></span><span class="bl-dot">·</span><span>{a["minutes"]} хв читання</span></div></div>'
                f'{cover(a, pre, "bl-hero")}'
                f'<div class="bl-cols"><article class="bl-art">'
                f'<section class="bl-short" aria-labelledby="sh"><h2 id="sh">Коротко</h2><ul>{short}</ul></section>'
                f'{body_html}{prod}'
                f'<section class="bl-faq" aria-labelledby="faq"><h2 id="faq">Часті запитання</h2>{faq}</section>'
                f'<section class="bl-au" aria-label="Автор"><img class="bl-av bl-av-l" src="{pre}{AUTHOR["photo"]}" alt="{AUTHOR["name"]}" width="64" height="64" loading="lazy" decoding="async">'
                f'<div><div class="bl-lab">Автор</div><b>{AUTHOR["name"]}</b><p>{E(AUTHOR["job"])}.</p>'
                f'<p class="bl-dates">Опубліковано {human_date(a["published"])}. Оновлено {human_date(a["updated"])}.</p></div></section>'
                f'{src}</article>{sidebar}</div>{relh}</div></main>')
        js = ('<script>(function(){var l=[].slice.call(document.querySelectorAll(".bl-toc a"));if(!l.length||!("IntersectionObserver"in window))return;'
              'var m={};l.forEach(function(a){m[a.getAttribute("href").slice(1)]=a});var o=new IntersectionObserver(function(es){es.forEach(function(e){'
              'if(e.isIntersecting){l.forEach(function(a){a.classList.remove("on")});var a=m[e.target.id];a&&a.classList.add("on")}})},{rootMargin:"-80px 0px -70% 0px"});'
              'Object.keys(m).forEach(function(i){var h=document.getElementById(i);h&&o.observe(h)})})();</script>')
        title = a.get('seo_title') or a['title']
        doc(url_of(a), f'{title} | GREENODIN', a['desc'], body, extra_js=js, ld=article_ld(a, pre), image=('img/blog/' + a['cover']) if a.get('cover') else None,
            head_extra='<link rel="stylesheet" href="../assets/blog.css">')

    def index_page():
        pre = '../'
        feat = arts[0]
        secs = [s for s in SECTIONS if any(a['section'] == s for a in arts)]
        chips = '<div class="bl-chips" role="group" aria-label="Рубрики"><button type="button" class="bl-chip on" data-s="">Усі статті</button>' + ''.join(
            f'<button type="button" class="bl-chip" data-s="{E(s)}">{E(s)}</button>' for s in secs) + '</div>'
        cards = ''.join(f'<div class="bl-it" data-s="{E(a["section"])}">{card(a, "../")}</div>' for a in arts)
        body = (f'<main class="bl"><section class="bl-top"><div class="w"><h1>Блог про органічні добрива і ґрунт</h1>'
                f'<p>Практика агронома, технології GREENODIN, відновлення ґрунтів. Пише {AUTHOR["name"]}, директор НВ ТОВ «СІНТА».</p></div></section>'
                f'<div class="w">{chips}<div class="bl-grid bl-gl" id="blg">{cards}</div>'
                f'<aside class="bl-prod bl-cta"><div><div class="bl-lab bl-lab-l">Не знайшли відповідь?</div><p>Напишіть або зателефонуйте: підкажемо добриво під ваш ґрунт і культуру.</p></div>'
                f'<a class="bl-btn" href="../kontakty.html">Зв’яжіться з нами</a></aside></div></main>')
        js = ('<script>(function(){var c=document.querySelectorAll(".bl-chip"),it=document.querySelectorAll(".bl-it");c.forEach(function(b){b.addEventListener("click",function(){'
              'c.forEach(function(x){x.classList.remove("on")});b.classList.add("on");var s=b.getAttribute("data-s");it.forEach(function(e){e.hidden=!!s&&e.getAttribute("data-s")!==s})})})})();</script>')
        ld = [{'@context': 'https://schema.org', '@type': 'Blog', 'name': 'Блог GREENODIN', 'url': SITE_URL + 'blog/', 'inLanguage': 'uk',
               'publisher': ORG, 'author': {'@type': 'Person', 'name': AUTHOR['name']},
               'blogPost': [{'@type': 'BlogPosting', 'headline': a['title'], 'url': SITE_URL + url_of(a), 'datePublished': a['published']} for a in arts]}]
        crumbs('../', [(None, 'Блог')])
        # крихти для індексу: тільки у JSON-LD (візуально є заголовок)
        doc('blog/index.html', 'Блог GREENODIN: органічні добрива, ґрунт, вирощування культур',
            'Статті агронома про кислотність ґрунту, норми внесення органічних добрив і вирощування картоплі, овочів та польових культур. Автор Тимур Лєвда.',
            body, extra_js=js, ld=ld, head_extra='<link rel="stylesheet" href="../assets/blog.css">')

    for a in arts: article_page(a)
    index_page()
    print('blog: статей', len(arts), '| слів', sum(a['words'] for a in arts))
    return arts
