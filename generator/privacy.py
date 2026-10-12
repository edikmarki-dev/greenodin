"""Сторінка «Політика конфіденційності» (privacy.html). Тексти: (uk, ru, en).
Українські рядки йдуть у сторінку, переклади ru/en додаються до tr/ru.json і tr/en.json під час збірки."""
import os, json, html as H

DATE = ('12 жовтня 2026', '12 октября 2026', 'October 12, 2026')
TITLE = ('Політика конфіденційності', 'Политика конфиденциальности', 'Privacy Policy')
LEAD = ('Ця політика пояснює, які дані ми збираємо на сайті GREENODIN, навіщо це робимо і як ви можете ними керувати.',
        'Эта политика объясняет, какие данные мы собираем на сайте GREENODIN, зачем это делаем и как вы можете ими управлять.',
        'This policy explains what data we collect on the GREENODIN website, why we collect it, and how you can control it.')
UPD = ('Редакція від', 'Редакция от', 'Last updated:')
META_TITLE = ('Політика конфіденційності сайту GREENODIN', 'Политика конфиденциальности сайта GREENODIN', 'GREENODIN website privacy policy')
META_DESC = ('Які персональні дані збирає сайт GREENODIN, для чого їх використовують, кому передають, скільки зберігають і як їх видалити.',
             'Какие персональные данные собирает сайт GREENODIN, для чего их используют, кому передают, сколько хранят и как их удалить.',
             'What personal data the GREENODIN website collects, how it is used, who receives it, how long it is kept and how to have it deleted.')

# ('h', текст) заголовок H2; ('p', текст) абзац; ('ul', [елементи])
BLOCKS = [
 ('h', ('1. Хто ми', '1. Кто мы', '1. Who we are')),
 ('p', ('Сайт належить НВ ТОВ «СІНТА», розробнику та виробнику органічних добрив ТМ GREENODIN. Ми є володільцем персональних даних, які ви залишаєте на сайті. Обробка відбувається відповідно до Закону України «Про захист персональних даних».',
        'Сайт принадлежит НВ ООО «СИНТА», разработчику и производителю органических удобрений ТМ GREENODIN. Мы являемся владельцем персональных данных, которые вы оставляете на сайте. Обработка осуществляется в соответствии с Законом Украины «О защите персональных данных».',
        'The website belongs to NV TOV “SINTA”, the developer and manufacturer of GREENODIN organic fertilizers. We are the controller of the personal data you leave on the site. Data is processed in accordance with the Law of Ukraine “On Personal Data Protection”.')),
 ('h', ('2. Які дані ми збираємо', '2. Какие данные мы собираем', '2. What data we collect')),
 ('p', ('Ми збираємо лише те, що ви самі повідомляєте через форму зворотного зв’язку, та мінімум технічних даних.',
        'Мы собираем только то, что вы сами сообщаете через форму обратной связи, и минимум технических данных.',
        'We collect only what you provide through the contact form, plus a minimum of technical data.')),
 ('ul', [('Ім’я, номер телефону, адреса електронної пошти (за бажанням) та текст повідомлення.',
          'Имя, номер телефона, адрес электронной почты (по желанию) и текст сообщения.',
          'Your name, phone number, email address (optional) and message text.'),
         ('Адреса сторінки сайту, з якої ви надіслали форму.',
          'Адрес страницы сайта, с которой вы отправили форму.',
          'The address of the site page from which you sent the form.'),
         ('Технічні дані, які автоматично фіксує хостинг: IP-адреса, тип браузера, час і адреса запиту.',
          'Технические данные, которые автоматически фиксирует хостинг: IP-адрес, тип браузера, время и адрес запроса.',
          'Technical data automatically recorded by the hosting: IP address, browser type, time and address of the request.')]),
 ('h', ('3. Для чого ми використовуємо дані', '3. Для чего мы используем данные', '3. How we use the data')),
 ('ul', [('Щоб відповісти на ваш запит і зв’язатися з вами.',
          'Чтобы ответить на ваш запрос и связаться с вами.',
          'To answer your request and contact you.'),
         ('Щоб підібрати добриво, розрахувати норму та обсяг, підготувати пропозицію.',
          'Чтобы подобрать удобрение, рассчитать норму и объём, подготовить предложение.',
          'To select a fertilizer, calculate the rate and volume, and prepare an offer.'),
         ('Щоб захистити сайт від спаму та зловживань.',
          'Чтобы защитить сайт от спама и злоупотреблений.',
          'To protect the site from spam and abuse.')]),
 ('p', ('Ми не використовуємо ваші дані для розсилок без вашої окремої згоди й не продаємо їх третім особам.',
        'Мы не используем ваши данные для рассылок без вашего отдельного согласия и не продаём их третьим лицам.',
        'We do not use your data for mailings without your separate consent and we do not sell it to third parties.')),
 ('h', ('4. Підстава для обробки', '4. Основание для обработки', '4. Legal basis')),
 ('p', ('Підставою є ваша згода. Надсилаючи форму, ви погоджуєтеся на обробку даних для мети, вказаної в цій політиці. Згоду можна відкликати в будь-який момент.',
        'Основанием является ваше согласие. Отправляя форму, вы соглашаетесь на обработку данных для цели, указанной в этой политике. Согласие можно отозвать в любой момент.',
        'The basis is your consent. By submitting the form, you agree to the processing of your data for the purpose stated in this policy. You can withdraw your consent at any time.')),
 ('h', ('5. Кому ми передаємо дані', '5. Кому мы передаём данные', '5. Who receives the data')),
 ('p', ('Заявки з форми надходять працівникам компанії через сервіс обміну повідомленнями Telegram. Сайт розміщено на хостингу Vercel. Шрифти завантажуються із сервісу Google Fonts, а на сторінці «Контакти» показано карту Google Maps. Ці сервіси можуть отримувати вашу IP-адресу та технічні дані браузера й обробляють їх за власними політиками конфіденційності.',
        'Заявки из формы поступают сотрудникам компании через сервис обмена сообщениями Telegram. Сайт размещён на хостинге Vercel. Шрифты загружаются из сервиса Google Fonts, а на странице «Контакты» показана карта Google Maps. Эти сервисы могут получать ваш IP-адрес и технические данные браузера и обрабатывают их по собственным политикам конфиденциальности.',
        'Form requests are delivered to company employees through the Telegram messaging service. The site is hosted on Vercel. Fonts are loaded from Google Fonts, and the Contacts page shows a Google Maps map. These services may receive your IP address and browser technical data and process it under their own privacy policies.')),
 ('p', ('Крім цього, ми передаємо дані лише за вимогою закону або за рішенням суду.',
        'Кроме этого, мы передаём данные только по требованию закона или по решению суда.',
        'Otherwise, we disclose data only when required by law or by a court decision.')),
 ('h', ('6. Файли cookie та аналітика', '6. Файлы cookie и аналитика', '6. Cookies and analytics')),
 ('p', ('Сайт не використовує рекламні й аналітичні cookie та не веде відстеження відвідувачів. Сторонні сервіси, згадані вище, можуть застосовувати власні технічні механізми.',
        'Сайт не использует рекламные и аналитические cookie и не ведёт отслеживание посетителей. Сторонние сервисы, упомянутые выше, могут применять собственные технические механизмы.',
        'The site does not use advertising or analytics cookies and does not track visitors. The third-party services mentioned above may use their own technical mechanisms.')),
 ('h', ('7. Скільки ми зберігаємо дані', '7. Сколько мы храним данные', '7. How long we keep data')),
 ('p', ('Ми зберігаємо дані стільки, скільки потрібно для опрацювання запиту та подальшої співпраці, а також у межах строків, які вимагає закон. Після цього дані видаляються. Ви також можете попросити видалити їх раніше.',
        'Мы храним данные столько, сколько нужно для обработки запроса и дальнейшего сотрудничества, а также в пределах сроков, которых требует закон. После этого данные удаляются. Вы также можете попросить удалить их раньше.',
        'We keep data for as long as needed to process your request and for any further cooperation, and within the periods required by law. After that, the data is deleted. You can also ask us to delete it earlier.')),
 ('h', ('8. Захист даних', '8. Защита данных', '8. Data protection')),
 ('p', ('Ми вживаємо розумних організаційних і технічних заходів, щоб захистити дані від втрати, неправомірного доступу та розголошення. Передача даних з сайту відбувається через захищене з’єднання.',
        'Мы принимаем разумные организационные и технические меры, чтобы защитить данные от потери, неправомерного доступа и разглашения. Передача данных с сайта происходит через защищённое соединение.',
        'We take reasonable organizational and technical measures to protect data from loss, unauthorized access and disclosure. Data from the site is transmitted over a secure connection.')),
 ('h', ('9. Ваші права', '9. Ваши права', '9. Your rights')),
 ('ul', [('Дізнатися, які ваші дані ми обробляємо, і отримати їх копію.',
          'Узнать, какие ваши данные мы обрабатываем, и получить их копию.',
          'Find out what data of yours we process and receive a copy.'),
         ('Вимагати виправити неточні дані.',
          'Потребовать исправить неточные данные.',
          'Ask us to correct inaccurate data.'),
         ('Вимагати видалити дані або обмежити їх обробку.',
          'Потребовать удалить данные или ограничить их обработку.',
          'Ask us to delete data or restrict its processing.'),
         ('Відкликати згоду на обробку.',
          'Отозвать согласие на обработку.',
          'Withdraw your consent to processing.'),
         ('Звернутися зі скаргою до Уповноваженого Верховної Ради України з прав людини.',
          'Обратиться с жалобой к Уполномоченному Верховной Рады Украины по правам человека.',
          'Lodge a complaint with the Ukrainian Parliament Commissioner for Human Rights.')]),
 ('p', ('Щоб скористатися правами, напишіть нам на пошту або зателефонуйте. Ми відповімо протягом розумного строку, не пізніше ніж протягом 30 днів.',
        'Чтобы воспользоваться правами, напишите нам на почту или позвоните. Мы ответим в разумный срок, не позднее чем в течение 30 дней.',
        'To exercise your rights, email or call us. We will reply within a reasonable time and no later than 30 days.')),
 ('h', ('10. Діти', '10. Дети', '10. Children')),
 ('p', ('Сайт не призначений для дітей. Ми свідомо не збираємо персональні дані осіб, молодших за 16 років. Якщо ви вважаєте, що дитина залишила дані на сайті, напишіть нам, і ми їх видалимо.',
        'Сайт не предназначен для детей. Мы сознательно не собираем персональные данные лиц младше 16 лет. Если вы считаете, что ребёнок оставил данные на сайте, напишите нам, и мы их удалим.',
        'The site is not intended for children. We do not knowingly collect personal data of people under 16. If you believe a child has left data on the site, write to us and we will delete it.')),
 ('h', ('11. Зміни політики', '11. Изменения политики', '11. Changes to this policy')),
 ('p', ('Ми можемо оновлювати цю політику. Актуальна редакція завжди доступна на цій сторінці, а дата останнього оновлення вказана вгорі.',
        'Мы можем обновлять эту политику. Актуальная редакция всегда доступна на этой странице, а дата последнего обновления указана вверху.',
        'We may update this policy. The current version is always available on this page, and the date of the latest update is shown at the top.')),
 ('h', ('12. Контакти', '12. Контакты', '12. Contacts')),
 ('p', ('З питань персональних даних звертайтеся:',
        'По вопросам персональных данных обращайтесь:',
        'For questions about personal data, contact us:')),
]

def tr_merge(G):
    """додає переклади у tr/ru.json і tr/en.json"""
    HERE = G['HERE']
    segs = [TITLE, LEAD, UPD, DATE, META_TITLE, META_DESC,
            (UPD[0]+' '+DATE[0], UPD[1]+' '+DATE[1], UPD[2]+' '+DATE[2])]
    for b in BLOCKS:
        if b[0] == 'ul': segs += b[1]
        else: segs.append(b[1])
    for i, L in ((1, 'ru'), (2, 'en')):
        p = os.path.join(HERE, 'tr', f'{L}.json')
        d = json.load(open(p, encoding='utf-8'))
        for s in segs: d[s[0]] = s[i]
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

def run(G):
    doc, crumbs, E = G['doc'], G['crumbs'], G['E']
    PHONE, PHONE_T, EMAIL, ADDR = G['PHONE'], G['PHONE_T'], G['EMAIL'], G['ADDR']
    parts = []
    for b in BLOCKS:
        if b[0] == 'h': parts.append(f'<h2>{E(b[1][0])}</h2>')
        elif b[0] == 'p': parts.append(f'<p>{E(b[1][0])}</p>')
        else: parts.append('<ul>' + ''.join(f'<li>{E(x[0])}</li>' for x in b[1]) + '</ul>')
    contacts = (f'<ul class="pv-c"><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="tel:{PHONE}">{PHONE_T}</a></li><li>{E(ADDR)}</li></ul>')
    body = (f'<main id="top"><div class="w pv">{crumbs("", [(None, TITLE[0])])}<h1 class="pt">{E(TITLE[0])}</h1>'
            f'<p class="pv-lead">{E(LEAD[0])}</p><p class="pv-d">{E(UPD[0])} {E(DATE[0])}</p>'
            f'<div class="pv-b">{"".join(parts)}{contacts}</div></div></main>')
    doc('privacy.html', META_TITLE[0], META_DESC[0], body, head_extra='<link rel="stylesheet" href="assets/privacy.css">')
    tr_merge(G)
