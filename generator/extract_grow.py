"""Одноразово: структурні блоки розділу «Вирощування» зі збережених сторінок старого сайту → grow_blocks.json + grow_img/.
Запуск: python3 extract_grow.py <тека зі сторінками> ; результат лежить поруч із gen.py."""
import sys, os, re, json, glob, unicodedata
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/old/добрива'
NFC = lambda s: unicodedata.normalize('NFC', s)
SLUG = {'Цукрових буряків': 'dobryva-dlya-tsukrovykh-buriakiv-greenodin', 'баклажанів': 'dobrivo-dlya-baklazhaniv-greenodin-gray',
        'гострого перцю': 'dobrivo-dlya-gostrogo-percyu-greenodin-gray', 'капусти': 'dobrivo-dlya-kapusti-greenodin-gray-granuli',
        'картоплі': 'dobrivo-dlya-kartopl-greenodin-gray-granuli', 'редису': 'dobrivo-dlya-redysu-greenodin-gray',
        'соняшнику': 'dobryva-dlya-sonyashnyku-greenodin', 'кукурудзи': 'dobryva-dlya-kukurudzy-greenodin',
        'нуту': 'dobryva-dlya-nutu-greenodin', 'сої': 'dobryva-dlya-soyi-greenodin',
        'часнику': 'dobrivo-dlya-chasniku-greenodin-gray-granuli', 'огірків': 'dobrivo-dlya-ogirkiv-greenodin-gray-granuli', 'цибулі': 'dobrivo-dlya-cibuli-greenodin-gray',
        'помідор': 'dobriva-dlya-pomidoriv-greenodin-gray-granuli', 'моркви': 'dobrivo-dlya-morkvi-greenodin-gray', 'столових буряків': 'dobrivo-dlya-stolovih-buryakv-greenodin-gray'}
SKIP_IMG = re.compile(r'-photo-350x350|image-6-4-350x350|Foto_redys|80x80|200x300|video-review|photo_patent|doc-\d|logo|лого', re.I)
SENT_DROP = re.compile(r'(?i)garden\s*soil|купити|купіть|грн|інтернет-магазин|читайте статтю|прочитайте статтю|спираючись на відгуки|задати питання|написати відгук')
FIX = [(r'Organic Standart', 'Organic Standard'), (r'(європейським стандартам|стандартам Європейського союзу)\s*№\s*834/2007[^.]*?№\s*889/2008', 'вимогам Регламенту (ЄС) 2018/848'),
       (r'\s+([,.;:!?])', r'\1')]
def clean(t):
    t = re.sub(r'\s+', ' ', t.replace('\xa0', ' ')).strip()
    for a, b in FIX: t = re.sub(a, b, t)
    sents = [s for s in re.split(r'(?<=[.!?])\s+', t) if s.strip() and not SENT_DROP.search(s)]
    return ' '.join(sents).strip()
def junk_p(t):
    return (re.search(r'^Дивитися звіти|(інтегроване та органічне|органічне вирощування (буряку цукрового|кукурудзи))$|^Вибір та норма внесення органічних|^Таблиця \d+ [–-]', t) or t.strip() in ('Стадії', 'Стадії Рішення') or re.search(r'(технологічній карті:?|технологічна карта вирощування[^.]*:)\s*$', t)
            or t.count('л/') >= 3 or t.count('+') >= 3)
TYPO = {'Єтап': 'Етап', 'или': 'або', 'Густота стану': 'Густота стояння', 'Больше 125': 'Понад 125'}
def cell(t):
    t = re.sub(r'\s+', ' ', t.replace('\xa0', ' ')).strip()
    for a, b in TYPO.items(): t = t.replace(a, b)
    return t

def save_img(src_path, name, whiteout=None, crop=None):
    im = Image.open(src_path).convert('RGB')
    if whiteout: ImageDraw.Draw(im).rectangle(whiteout, fill='white')
    if crop: im = im.crop(crop)
    im.save(os.path.join(HERE, 'grow_img', name + '.webp'), quality=84, method=6)
    return f'img/grow/{name}.webp', im.size

def tbl(cap, rows, num=True): return {'t': 'table', 'cap': cap, 'rows': rows, 'num': num}
SUN = {
 'sunflower-amount-of-nutrients': tbl('Кількість поживних речовин (макроелементів), кг на 1 т урожаю', [['Елемент', 'Вилучення насінням', 'Вилучення з побічними продуктами', 'Разом'],
        ['Азот (N)', '28', '23', '51'], ['Фосфор (P₂O₅)', '16', '14', '30'], ['Калій (K₂O)', '24', '74', '98'], ['Магній (MgO)', '6,6', '7,4', '14']]),
 'sunflower-extraction-and-consumption-of-trace-elements': tbl('Вилучення і споживання макроелементів соняшником при врожайності 3 т/га, кг/га', [['Елемент', 'Насіння', 'Пожнивні рештки'],
        ['Азот (N)', '84', '69'], ['Фосфор (P₂O₅)', '48', '42'], ['Калій (K₂O)', '72', '222'], ['Магній (MgO)', '19,8', '22,2']]),
 'sunflower-consumption-for-the-removal-of-trace-elements': tbl('Споживання та вилучення мікроелементів', [['Елемент', 'Споживання', 'Вилучення'],
        ['Мідь (Cu)', '17', '7'], ['Бор (B)', '113', '23'], ['Залізо (Fe)', '209', '30'], ['Марганець (Mn)', '118', '12'], ['Цинк (Zn)', '99', '42']]),
}
out = json.load(open(os.path.join(HERE, 'grow_blocks.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'grow_blocks.json')) else {}
for f in sorted(glob.glob(SRC + '/*.html')):
    key = [k for k in SLUG if k in NFC(os.path.basename(f)) and (k!='сої' or 'сої' in NFC(os.path.basename(f)))][0]; slug = SLUG[key]
    fdir = f[:-5] + '_files'
    s = BeautifulSoup(open(f, encoding='utf-8', errors='ignore').read(), 'html.parser')
    for t in s(['script', 'style', 'noscript']): t.decompose()
    root = s.find('h1').parent
    blocks = []; state = {'done': False}
    INLINE = {'b', 'strong', 'i', 'em', 'a', 'span', 'sup', 'sub', 'u', 'font', 'small', 'mark', 'code', 'br'}
    BLOCKS = {'div', 'p', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'table', 'figure', 'section', 'blockquote', 'img', 'center', 'article'}
    def handle_img(el):
        src = el.get('src') or ''
        base = os.path.basename(src)
        if not base or SKIP_IMG.search(base) or src.startswith('data:'): return
        stem = os.path.splitext(base)[0]
        stem_ = re.sub(r'_\d+x\d+$', '', stem)
        if stem_ in SUN: blocks.append(dict(SUN[stem_])); return
        p = os.path.join(fdir, base)
        if not os.path.exists(p): p = os.path.join(fdir, unicodedata.normalize('NFD', base))
        if not os.path.exists(p): print('NO FILE', base); return
        alt = clean(el.get('alt', ''))
        if 'consumption-of-nutrients' in stem:
            path, size = save_img(p, 'sunflower-stages', whiteout=(0, 20, 255, 90), crop=(0, 0, 754, 245))
            blocks.append({'t': 'img', 'src': path, 'w': size[0], 'h': size[1], 'alt': 'Фази розвитку соняшника за шкалою BBCH',
                           'cap': 'Фази розвитку соняшника (шкала BBCH): 00–12 проростання; 18–37 зростання вегетативної маси; 53–79 розвиток генеративних органів і плодоношення, основне споживання поживних речовин; 89–92 дозрівання, прибирання.'})
            return
        name = {'sunflower-symptoms-of-a-nitrogen-deficiency_800x334': 'sunflower-nitrogen-deficiency', 'osnovnye-etapy-vyrashchivaniya-kartofelya': 'potato-growth-stages',
                'Kukuruza-Dekalb-5-6-listkov-Greenodin_500x758': 'corn-5-6-leaves-greenodin'}.get(stem, re.sub(r'\W+', '-', stem).lower())
        path, size = save_img(p, name)
        altt = {'sunflower-nitrogen-deficiency': 'Симптоми дефіциту азоту у соняшника', 'potato-growth-stages': 'Основні етапи вирощування картоплі',
                'corn-5-6-leaves-greenodin': 'Посіви кукурудзи у фазі 5–6 листків після внесення GREENODIN'}.get(name, alt)
        blocks.append({'t': 'img', 'src': path, 'w': size[0], 'h': size[1], 'alt': altt, 'cap': alt if name == 'corn-5-6-leaves-greenodin' else ''})
    def add_text(buf, kind='p'):
        for part in re.split(r'\n+', ''.join(buf)):
            x = clean(part)
            if not x: continue
            if kind == 'p' and junk_p(x): continue
            blocks.append({'t': kind, 'x': x})
    def walk(node):
        buf = []
        def flush():
            if buf: add_text(buf); buf.clear()
        for ch in node.children:
            if state['done']: return
            n = getattr(ch, 'name', None)
            if n is None:
                if hasattr(ch, 'output_ready') and type(ch).__name__ == 'NavigableString': buf.append(str(ch))
                continue
            if n == 'br': buf.append('\n'); continue
            if n in INLINE and not ch.find(list(BLOCKS)):
                buf.append(ch.get_text('')); continue
            flush()
            if n in ('h2', 'h3', 'h4', 'h5'):
                x = clean(ch.get_text(' ', strip=True))
                if re.search(r'Унікальні властивості|Чому клієнти', x): state['done'] = True; return
                if x: blocks.append({'t': 'h', 'l': 2 if n == 'h2' else 3, 'x': x})
            elif n == 'li':
                if ch.find(['li', 'ul', 'ol']): walk(ch)
                else:
                    x = clean(ch.get_text(' ', strip=True))
                    if x: blocks.append({'t': 'li', 'x': x})
            elif n == 'table':
                rows = [[cell(c.get_text(' ', strip=True)) for c in r.find_all(['td', 'th'])] for r in ch.find_all('tr')]
                rows = [r for r in rows if any(r)]
                if len(rows) >= 2 and rows[0][0] != 'Рішення': blocks.append(tbl('', rows))
            elif n == 'img': handle_img(ch)
            elif n in ('script', 'style', 'form', 'button', 'input', 'select', 'noscript'): pass
            else: walk(ch)
        flush()
    for sel in ('category-description', 'content-top'):
        node = root.find('div', class_=sel)
        if node and not state['done']: walk(node)
    # дублі підряд
    blocks = [b for i, b in enumerate(blocks) if not (i and b == blocks[i - 1])]
    # прибрати заголовки без вмісту
    res = []
    for i, b in enumerate(blocks):
        if b['t'] == 'h' and (i + 1 == len(blocks) or blocks[i + 1]['t'] == 'h'): continue
        res.append(b)
    out[slug] = res
    print(slug, len(res), {t: sum(1 for b in res if b['t'] == t) for t in ('h', 'p', 'li', 'table', 'img')})
json.dump(out, open(os.path.join(HERE, 'grow_blocks.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
