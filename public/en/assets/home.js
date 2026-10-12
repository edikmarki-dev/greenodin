/* GREENODIN: головна — пошук, чипи груп, форма заявки */
(function () {
  var $ = function (s) { return document.querySelector(s); };
  var q = $('#q'), ct = $('#ct'), fg = $('#fg');
  var heads = [].slice.call(document.querySelectorAll('#cat .gh'));
  function filter() {
    var s = q.value.trim().toLowerCase(), n = 0;
    heads.forEach(function (h) {
      var sl = h.nextElementSibling, k = 0;
      sl.querySelectorAll('.cd').forEach(function (c) { var ok = !s || c.dataset.n.indexOf(s) > -1; c.hidden = !ok; if (ok) k++; });
      h.hidden = sl.hidden = !k; n += k;
    });
    ct.textContent = s ? (n ? 'Found: ' + n : 'Nothing found. Try a different query.') : '';
    act = null; spy();
  }
  q.addEventListener('input', filter);
  // підсвітка групи під час прокручування
  var chips = [].slice.call(fg.querySelectorAll('a')), act = null, tk = 0;
  function spy() {
    var k = null;
    heads.forEach(function (h) { if (!h.hidden && h.getBoundingClientRect().top <= 150) k = h.id; });
    if ($('#cat').getBoundingClientRect().bottom < 150) k = null;
    if (k === act) return; act = k;
    chips.forEach(function (c) {
      var on = c.getAttribute('href') === '#' + k; c.classList.toggle('on', on);
      if (on) fg.scrollTo({ left: c.offsetLeft - fg.clientWidth / 2 + c.offsetWidth / 2, behavior: 'smooth' });
    });
  }
  addEventListener('scroll', function () { if (tk) return; tk = requestAnimationFrame(function () { tk = 0; spy(); }); }, { passive: true });
  fg.addEventListener('wheel', function (e) {
    var mx = fg.scrollWidth - fg.clientWidth;
    if (mx > 0 && Math.abs(e.deltaY) > Math.abs(e.deltaX) && ((e.deltaY > 0 && fg.scrollLeft < mx) || (e.deltaY < 0 && fg.scrollLeft > 0))) { e.preventDefault(); fg.scrollLeft += e.deltaY; }
  }, { passive: false });
  spy();
  // заявка
  var d = $('#d');
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-o]'); if (!b) return;
    $('#dt').textContent = b.textContent.trim(); $('#dp').textContent = b.dataset.o;
    $('#fm').hidden = false; $('#ok').hidden = true; $('#er').textContent = '';
    d.showModal(); $('#n').focus();
  });
  $('#dx').onclick = $('#oc').onclick = function () { d.close(); };
  d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
  $('#fm').onsubmit = function (e) {
    e.preventDefault();
    var f = $('#fm'), bt = f.querySelector('button:not(.x)'), n = $('#n').value.trim(), t = $('#t').value, digits = t.replace(/\D/g, '');
    if (!n) { $('#er').textContent = 'Please enter your name'; return; }
    if (digits.length < 10) { $('#er').textContent = 'Please enter the full phone number, at least 10 digits'; return; }
    $('#er').textContent = ''; bt.disabled = true;
    gSend({ topic: $('#dp').textContent || $('#dt').textContent, name: n, phone: t, company: f.company.value, ts: f.dataset.ts }).then(function (j) {
      bt.disabled = false;
      if (!j.ok) { $('#er').textContent = j.error; return; }
      $('#okp').textContent = n + ', we will call you back at ' + t + '.' + (j.demo ? ' (Demo: the request is not sent in preview.)' : '');
      f.hidden = true; $('#ok').hidden = false; f.reset();
    });
  };
})();
