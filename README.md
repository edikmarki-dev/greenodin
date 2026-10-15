# GREENODIN — каталог органічних добрив

Статичний сайт (uk у корені, `/ru/`, `/en/`) + одна serverless-функція `api/contact.js` для форми.

## Структура
- `public/` — готовий сайт. У git його немає: Vercel збирає його сам при кожному push (`buildCommand` у `vercel.json`), локально він з'являється після `sh generator/build.sh`.
- `generator/` — генератор: `gen.py`, `i18n.py`, `textclean.py`, словники `tr/`, дані `data/`, статика `static/`.
- `api/contact.js` — відправка форми у Telegram.
- `vercel.json` — редіректи зі старого сайту та заголовки (генерується `gen.py`, руками не правити).

## Збірка
    sh generator/build.sh

Порядок усередині: `gen.py` → `i18n.py extract` (покаже непереведені фрагменти) → `i18n.py build` (/ru, /en, hreflang, sitemap, посилання на телефони/пошту/сторінки).

Деплой: commit і push змін у `generator/` (тексти, статті, картинки) — Vercel сам поставить залежності з `generator/requirements.txt`, запустить `build.sh` і викладе `public/`. Збирати локально треба лише для перегляду. Якщо збірка змінила `vercel.json` (нові редіректи) — його теж комітимо: Vercel читає `vercel.json` з репозиторію ДО збірки.

Нову статтю блогу можна додати й без локальної збірки: файл `generator/data/blog/<slug>.md` + картинки в `generator/static/img/blog/` → push. Так публікує програма «Автопостинг».

## Де що правити
- Тексти товарів: `generator/data/catalog.json` (+ чистка у `textclean.py`), вкладки «Вирощування» — `generator/grow_blocks.json`.
- Макет і стилі: `generator/gen.py`, `generator/static/assets/style.css` (ручний CSS — ДО маркера `/* i18n-switcher */`).
- Переклади: `generator/tr/*.json`.

## Змінні середовища Vercel
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (кілька id через кому). Заявки з форм приходять у Telegram.
Framework Preset: Other. Команди збірки задані у `vercel.json` (генерується `gen.py`), у налаштуваннях проєкту їх не чіпаємо.

## Блог і поточний стан (для нового сеансу)

- Блог: `generator/blog.py`, статті `generator/data/blog/*.md` (front matter + markdown), стилі `generator/static/assets/blog.css`, картинки `generator/static/img/blog/`. Збірка `sh generator/build.sh`. Автор усіх статей Тимур Лєвда, фото `img/blog/author-levda.webp`.
- Блог лише українською (`UK_ONLY` в `i18n.py`); ru/en переклад блогу ще не зроблено.
- План переносу статей зі старого блогу: `generator/data/blog_src/` (INDEX.md, PLAN.md, GROW.md; тексти 01–18.md). Редиректи старих slug лежать у `vercel_json()` в `gen.py` (нерозібрані ведуть на `/blog/`).
- Промпти для картинок: `generator/data/blog_src/IMG_PROMPTS.md`.
- `SITE_URL` у `gen.py` тимчасово `https://greenodin.vercel.app/`; після підключення домену змінити на `https://greenodin.site/` і зібрати знову.
- Правило для текстів: дані виробника подаємо як власні, без приміток «за даними виробника».
- Готові кластери: кислотність ґрунту (4 статті), картопля (2), сівозміна (6: `sivozmina-posibnyk` як опорна, далі `shcho-take-sivozmina`, `poperedniky-polovykh-kultur`, `poperedniky-ovochevykh-kultur`, `chornyi-rannii-zainiatyi-par`, `yak-skladaty-sivozminu`). Картинки сівозміни підключено (промпти в `IMG_PROMPTS.md`, рядки 12–23): обкладинки 1024×434 і внутрішні 1024×572 у `static/img/blog/`. Обкладинки, що прийшли в 16:9, кадруємо до 21:9 по центру.
- Нормативи сівозмін беремо з постанови КМУ № 164 від 11.02.2010. Сторінка zakon.rada.gov.ua недоступна для автоматичного читання, тому цифри звірені за дзеркалом тексту й за іншими джерелами; перед публікацією звірити з чинною редакцією.
- Далі: решта кластерів із `blog_src/PLAN.md`, калькулятор добрив для лінійки (`/kalkulyator.html`, uk/ru/en, норми в одному JSON), підключення домену.

### Правила для нових статей блогу

1. Шаблон: відповідь на запит у першому абзаці, блок «Коротко» (3–5 тез), H2 з явними `{#id}`, таблиці markdown, FAQ (3–5 питань), автор Тимур Лєвда, дати, джерела. Поля front matter дивись у `generator/blog.py` і в готових `data/blog/*.md`.
2. Джерела тільки реальні та перевірені (відкривати сторінку й звіряти цифри). Заглушок у квадратних дужках не лишати. Дані GREENODIN подаємо як власні.
3. Не називати сторонні препарати чи бренди без згоди власника.
4. Картинки: обкладинка 21:9 + 1–2 внутрішні 16:9. Промпти пишемо в `IMG_PROMPTS.md`, файли стискаємо в webp у `static/img/blog/`, alt обов'язковий.
5. Старий slug статті додаємо в `OLDBLOG` у `vercel_json()` (`gen.py`), щоб працював 301.
6. Порядок перенесення: кластери з `blog_src/PLAN.md`, тексти-джерела `blog_src/NN.md`, гайди «Вирощування» з `blog_src/GROW.md`.
