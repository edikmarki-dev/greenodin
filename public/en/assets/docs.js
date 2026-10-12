/* GREENODIN: перегляд сканів документів */
(function () {
  var lb = document.getElementById('lb'); if (!lb) return;
  var img = document.getElementById('lbimg'), cap = document.getElementById('lbc'), cnt = document.getElementById('lbk');
  var pages = [], label = '', i = 0;
  function show() {
    img.src = pages[i][0]; img.alt = label + ', ' + pages[i][1];
    cap.textContent = label + ' · ' + pages[i][1];
    cnt.textContent = pages.length > 1 ? (i + 1) + ' of ' + pages.length : '';
    document.getElementById('lbp').hidden = document.getElementById('lbn').hidden = pages.length < 2;
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.pgb'); if (!b) return;
    var g = b.closest('.pgs'); pages = JSON.parse(g.dataset.g); label = g.dataset.l; i = +b.dataset.i;
    show(); lb.showModal();
  });
  function go(d) { i = (i + d + pages.length) % pages.length; show(); }
  document.getElementById('lbp').onclick = function () { go(-1); };
  document.getElementById('lbn').onclick = function () { go(1); };
  document.getElementById('lbx').onclick = function () { lb.close(); };
  lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
  lb.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') go(1); if (e.key === 'ArrowLeft') go(-1); });
})();
