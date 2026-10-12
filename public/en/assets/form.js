/* GREENODIN: відправлення форм на /api/contact (Vercel) */
(function () {
  var preview = /claude|anthropic|usercontent/.test(location.hostname) || location.protocol === 'file:';
  window.gSend = function (data) {
    data.page = location.href; 
    if (preview) return Promise.resolve({ ok: true, demo: true });
    return fetch('/api/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .catch(function () { return { ok: false }; })
      .then(function (j) { if (!j.ok && !j.error) j.error = 'Could not send. Please call us: +38 043 250 90 90.'; return j; });
  };
  // мітка часу для антиспаму
  document.querySelectorAll('form[data-send]').forEach(function (f) { f.dataset.ts = Date.now(); });
})();
