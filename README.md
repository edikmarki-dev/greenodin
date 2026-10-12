# GREENODIN — каталог органічних добрив

Статичний сайт (uk у корені, `/ru/`, `/en/`) + одна serverless-функція `api/contact.js` для форми.

## Структура
- `public/` — готовий сайт, його і віддає Vercel (`outputDirectory` у `vercel.json`).
- `generator/` — генератор: `gen.py`, `i18n.py`, `textclean.py`, словники `tr/`, дані `data/`, статика `static/`.
- `api/contact.js` — відправка форми у Telegram.
- `vercel.json` — редіректи зі старого сайту та заголовки (генерується `gen.py`, руками не правити).

## Збірка
    sh generator/build.sh

Порядок усередині: `gen.py` → `i18n.py extract` (покаже непереведені фрагменти) → `i18n.py build` (/ru, /en, hreflang, sitemap, посилання на телефони/пошту/сторінки). Після змін у `public/` робимо commit і push — Vercel задеплоїть сам.

## Де що правити
- Тексти товарів: `generator/data/catalog.json` (+ чистка у `textclean.py`), вкладки «Вирощування» — `generator/grow_blocks.json`.
- Макет і стилі: `generator/gen.py`, `generator/static/assets/style.css` (ручний CSS — ДО маркера `/* i18n-switcher */`).
- Переклади: `generator/tr/*.json`.

## Змінні середовища Vercel
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (кілька id через кому). Заявки з форм приходять у Telegram.
Framework Preset: Other, Build Command порожній.
