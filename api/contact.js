// Vercel Serverless Function: приймає заявки з форм сайту й надсилає їх на пошту через SMTP.
// Змінні середовища (Vercel → Project → Settings → Environment Variables):
//   SMTP_HOST, SMTP_PORT (465 або 587), SMTP_USER, SMTP_PASS — поштова скринька, з якої йдуть листи
//   MAIL_TO   — куди надсилати заявки (office@avelife.pro; кілька адрес через кому)
//   MAIL_FROM — від кого (за замовчуванням SMTP_USER)
const nodemailer = require('nodemailer');

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

  const port = Number(process.env.SMTP_PORT || 465);
  const tr = nodemailer.createTransport({
    host: process.env.SMTP_HOST, port, secure: port === 465,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });
  const rows = [['Тема', topic], ['Ім’я', name], ['Телефон', phone], ['Пошта', email], ['Повідомлення', message], ['Сторінка', page]]
    .filter(r => r[1]);
  try {
    await tr.sendMail({
      from: `"Сайт GREENODIN" <${process.env.MAIL_FROM || process.env.SMTP_USER}>`,
      to: process.env.MAIL_TO || 'office@avelife.pro',
      replyTo: email || undefined,
      subject: `${topic}: ${name}, ${phone}`,
      text: rows.map(r => `${r[0]}: ${r[1]}`).join('\n'),
      html: '<table cellpadding="6" style="font:15px/1.4 Arial,sans-serif;border-collapse:collapse">' +
        rows.map(r => `<tr><td style="color:#667;vertical-align:top">${esc(r[0])}</td><td>${esc(r[1]).replace(/\n/g, '<br>')}</td></tr>`).join('') + '</table>',
    });
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error('mail error', e && e.message);
    return res.status(500).json({ ok: false, error: 'Не вдалося надіслати. Зателефонуйте нам: +38 043 250 90 90.' });
  }
};
