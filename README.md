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

## Блог і поточний стан (для нового сеансу)

- Блог: `generator/blog.py`, статті `generator/data/blog/*.md` (front matter + markdown), стилі `generator/static/assets/blog.css`, картинки `generator/static/img/blog/`. Збірка `sh generator/build.sh`. Автор усіх статей Тимур Лєвда, фото `img/blog/author-levda.webp`.
- Блог лише українською (`UK_ONLY` в `i18n.py`); ru/en переклад блогу ще не зроблено.
- План переносу статей зі старого блогу: `generator/data/blog_src/` (INDEX.md, PLAN.md, GROW.md; тексти 01–18.md). Редиректи старих slug лежать у `vercel_json()` в `gen.py` (нерозібрані ведуть на `/blog/`).
- Промпти для картинок: `generator/data/blog_src/IMG_PROMPTS.md`.
- `SITE_URL` у `gen.py` тимчасово `https://greenodin.vercel.app/`; після підключення домену змінити на `https://greenodin.site/` і зібрати знову.
- Правило для текстів: дані виробника подаємо як власні, без приміток «за даними виробника».
- Далі: калькулятор добрив для лінійки (`/kalkulyator.html`, uk/ru/en, норми в одному JSON), підключення домену, перенесення решти статей.
