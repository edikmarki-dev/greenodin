// Vercel Serverless Function: приймає заявки з форм сайту й надсилає їх у Telegram.
// Змінні середовища (Vercel → Project → Settings → Environment Variables):
//   TELEGRAM_BOT_TOKEN — токен бота від @BotFather
//   TELEGRAM_CHAT_ID   — id чату/групи/каналу, куди слати заявки (кілька id через кому)

const hits = new Map(); // простий ліміт: не більше 5 заявок з однієї IP за 10 хвилин (у межах «теплого» інстансу)
const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const cut = (s, n) => String(s || '').trim().slice(0, n);

module.exports = async (req, res) => {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ ok: false }); }
  let b = req.body || {};
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }

  // антиспам: приховане поле має бути порожнім, форму не можуть заповнити швидше ніж за 3 с
  if (b.company || (b.ts && Date.now() - Number(b.ts) < 3000)) return res.status(200).json({ ok: true });

  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'x';
  const now = Date.now(), list = (hits.get(ip) || []).filter(t => now - t < 600000);
  if (list.length >= 5) return res.status(429).json({ ok: false, error: 'Забагато заявок. Спробуйте пізніше або зателефонуйте.' });
  list.push(now); hits.set(ip, list);

  const name = cut(b.name, 100), phone = cut(b.phone, 30), email = cut(b.email, 120),
        message = cut(b.message, 3000), topic = cut(b.topic, 120) || 'Заявка з сайту', page = cut(b.page, 300);
  if (!name || phone.replace(/\D/g, '').length < 10)
    return res.status(400).json({ ok: false, error: 'Вкажіть ім’я та телефон повністю.' });
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    return res.status(400).json({ ok: false, error: 'Перевірте адресу пошти.' });

  const token = process.env.TELEGRAM_BOT_TOKEN, chats = String(process.env.TELEGRAM_CHAT_ID || '').split(',').map(x => x.trim()).filter(Boolean);
  if (!token || !chats.length) {
    console.error('telegram env is not set');
    return res.status(500).json({ ok: false, error: 'Не вдалося надіслати. Зателефонуйте нам: +38 043 250 90 90.' });
  }
  const rows = [['Тема', topic], ['Ім’я', name], ['Телефон', phone], ['Пошта', email], ['Повідомлення', message], ['Сторінка', page]]
    .filter(r => r[1]);
  const text = '<b>🌱 ' + esc(topic) + '</b>\n' + rows.slice(1).map(r => `<b>${esc(r[0])}:</b> ${esc(r[1])}`).join('\n');
  try {
    const results = await Promise.all(chats.map(chat_id =>
      fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id, text, parse_mode: 'HTML', disable_web_page_preview: true }),
      }).then(r => r.json())));
    if (!results.some(r => r && r.ok)) throw new Error(JSON.stringify(results[0]));
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error('telegram error', e && e.message);
    return res.status(500).json({ ok: false, error: 'Не вдалося надіслати. Зателефонуйте нам: +38 043 250 90 90.' });
  }
};
