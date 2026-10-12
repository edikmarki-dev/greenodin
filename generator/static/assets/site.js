/* GREENODIN: спільні скрипти сторінок */
(function () {
  var $ = function (s) { return document.querySelector(s); };
  // нова сторінка завжди відкривається зверху (крім переходу за якорем)
  try { history.scrollRestoration = 'manual'; } catch (e) {}
  if (!location.hash) { window.scrollTo(0, 0); var t0 = document.getElementById('top') || document.body; if (t0 && t0.scrollIntoView) t0.scrollIntoView({ block: 'start' }); }
  // меню на телефоні
  var bg = $('#bg'), m = $('#m');
  if (bg && m) {
    bg.onclick = function () { var o = m.classList.toggle('o'); bg.setAttribute('aria-expanded', o); };
    m.onclick = function (e) { if (!e.target.closest('a')) return; m.classList.remove('o'); bg.setAttribute('aria-expanded', 'false'); };
  }
  // випадаюче меню «Продукція»: на сенсорних екранах перший дотик відкриває меню
  var dd = $('#dd');
  if (dd) {
    var ddt = dd.querySelector('.ddt');
    var setO = function (o) { dd.classList.toggle('o', o); ddt.setAttribute('aria-expanded', o); };
    ddt.addEventListener('click', function (e) {
      if (matchMedia('(hover: hover)').matches || dd.classList.contains('o')) return;
      e.preventDefault(); setO(true);
    });
    dd.addEventListener('mouseenter', function () { ddt.setAttribute('aria-expanded', 'true'); });
    dd.addEventListener('mouseleave', function () { setO(false); });
    document.addEventListener('click', function (e) { if (!e.target.closest('#dd')) setO(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setO(false); ddt.blur(); } });
  }
  // перехід на іншу сторінку сайту: піднятися до верху ще в момент кліку
  // (переглядач може прокручувати власну сторінку, а не рамку сайту)
  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest('a[href]'); if (!a || a.target === '_blank') return;
    var href = a.getAttribute('href'); if (!href || href.charAt(0) === '#' || /^(mailto|tel):/.test(href)) return;
    var u; try { u = new URL(a.href, location.href); } catch (x) { return; }
    if (u.origin !== location.origin) return;
    if (u.pathname === location.pathname && u.hash) return;
    try { window.scrollTo({ top: 0, behavior: 'instant' }); } catch (x) { window.scrollTo(0, 0); }
    try { document.documentElement.scrollIntoView({ block: 'start', behavior: 'instant' }); } catch (x) {}
  });
  // стрілки слайдерів
  document.addEventListener('click', function (e) {
    var a = e.target.closest('.ar'); if (!a) return;
    var sl = a.closest('.gh').nextElementSibling;
    sl.scrollBy({ left: a.dataset.d * 470, behavior: 'smooth' });
  });
  // перетягування мишею у слайдерах
  var dg = null, lastDrag = false;
  document.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'mouse' || e.button) return;
    var el = e.target.closest('#fg,.sl'); if (el) dg = { el: el, x: e.clientX, l: el.scrollLeft, m: 0 };
  });
  document.addEventListener('pointermove', function (e) {
    if (!dg) return; var dx = e.clientX - dg.x; dg.m = Math.max(dg.m, Math.abs(dx));
    if (dg.m > 5) { dg.el.style.scrollSnapType = 'none'; dg.el.scrollLeft = dg.l - dx; }
  });
  document.addEventListener('pointerup', function () {
    if (!dg) return; dg.el.style.scrollSnapType = ''; lastDrag = dg.m > 5; dg = null;
    setTimeout(function () { lastDrag = false; }, 0);
  });
  document.addEventListener('click', function (e) { if (lastDrag) { e.preventDefault(); e.stopPropagation(); lastDrag = false; } }, true);
  document.querySelectorAll('.sl img, a.cd').forEach(function (x) { x.setAttribute('draggable', 'false'); });
  // вкладки (на сторінці їх може бути кілька)
  [].forEach.call(document.querySelectorAll('.tabs[role=tablist]'), function (tabs) {
    var tb = [].slice.call(tabs.querySelectorAll('button')), tp = [].slice.call(tabs.nextElementSibling.children);
    var sel = function (i, f) {
      tb.forEach(function (b, j) { b.classList.toggle('on', j == i); b.setAttribute('aria-selected', j == i); b.tabIndex = j == i ? 0 : -1; });
      tp.forEach(function (p, j) { p.classList.toggle('on', j == i); });
      tabs.scrollTo({ left: tb[i].offsetLeft - tabs.clientWidth / 2 + tb[i].offsetWidth / 2, behavior: 'smooth' });
      if (f) tb[i].focus();
    };
    tb.forEach(function (b, i) { b.tabIndex = i ? -1 : 0; b.onclick = function () { sel(i); }; });
    tabs.addEventListener('keydown', function (e) {
      var i = tb.findIndex(function (b) { return b.classList.contains('on'); });
      var n = e.key == 'ArrowRight' ? i + 1 : e.key == 'ArrowLeft' ? i - 1 : null;
      if (n !== null && tb[n]) { e.preventDefault(); sel(n, 1); }
    });
    // перехід за якорем на конкретний документ відкриває його вкладку
    var h = location.hash.slice(1);
    if (h) tp.forEach(function (p, j) { if (p.querySelector('[id="' + h + '"]')) { sel(j); p.querySelector('[id="' + h + '"]').scrollIntoView(); } });
  });
  // м'яка поява блоків (лише зсув, вміст видно одразу)
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.classList.add('js');
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    window.reveal = function () {
      document.querySelectorAll('section h2, .t, .bn li, .gh, .sl, .two > *, .grid').forEach(function (el) {
        if (el.dataset.rv) return; el.dataset.rv = '1';
        if (el.getBoundingClientRect().top < innerHeight) return;
        el.style.setProperty('--i', [].indexOf.call(el.parentNode.children, el) % 6);
        el.classList.add('reveal'); io.observe(el);
      });
    };
    window.reveal();
  }
})();

/* перемикач мови (випадаючий список) */
(function () {
  var box = document.getElementById('lsd'); if (!box) return;
  var btn = box.querySelector('.lsb');
  var set = function (o) { box.classList.toggle('o', o); btn.setAttribute('aria-expanded', o); };
  btn.addEventListener('click', function (e) { e.stopPropagation(); set(!box.classList.contains('o')); });
  document.addEventListener('click', function (e) { if (!e.target.closest('#lsd')) set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { set(false); btn.focus(); } });
})();
