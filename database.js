/* Fintech database: filters for trending.html, quick filter for the
   fintech-companies/* pages. */
(function () {
  'use strict';

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function norm(s) {
    return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }
  function fmt(n) { return n.toLocaleString('en-US'); }

  /* ---------- copy protection ----------
     Stops normal visitors selecting, copying, dragging, right-clicking and
     printing the company lists. Search fields still work as usual. */
  (function () {
    var scope = document.querySelector('main.db-page, main.db-hub');
    if (!scope) return;
    var toast, hideT;
    function isField(el) { return el && el.closest && el.closest('input, textarea, select'); }
    function say() {
      if (!toast) {
        toast = document.createElement('div');
        toast.className = 'db-toast';
        toast.setAttribute('role', 'status');
        toast.innerHTML = 'Copying is turned off for the database. <a href="/icp-list.html">Get a list of 100 of your ICP</a>';
        document.body.appendChild(toast);
      }
      toast.classList.add('is-on');
      clearTimeout(hideT);
      hideT = setTimeout(function () { toast.classList.remove('is-on'); }, 3200);
    }
    ['copy', 'cut'].forEach(function (type) {
      document.addEventListener(type, function (e) {
        if (isField(e.target)) return;
        e.preventDefault();
        if (e.clipboardData) e.clipboardData.setData('text/plain', '');
        say();
      });
    });
    scope.addEventListener('selectstart', function (e) { if (!isField(e.target)) e.preventDefault(); });
    scope.addEventListener('dragstart', function (e) { if (!isField(e.target)) e.preventDefault(); });
    scope.addEventListener('contextmenu', function (e) {
      if (e.target.closest && e.target.closest('.db-table-wrap')) { e.preventDefault(); say(); }
    });
    window.addEventListener('beforeprint', say);
  })();

  /* ---------- trending: the gated table ---------- */
  var tbody = document.getElementById('dbRows');
  if (!tbody || !window.fetch) return;

  var SHORT = { 'Wealth Management': 'Wealth', 'Crypto and DeFi': 'Crypto & DeFi',
                'Financial Management': 'Finance software', 'Spend Management': 'Spend' };
  var search = document.getElementById('dbSearch');
  var country = document.getElementById('dbCountry');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.db-chip[data-sector]'));
  var countEl = document.getElementById('dbCount');
  var gate = document.getElementById('dbGate');
  var moreEl = document.getElementById('dbMore');

  var state = { q: '', sector: '', country: '' };
  var data = null, names = null;

  // restore filters from the URL (?q=&sector=&country=)
  var params = new URLSearchParams(location.search);
  state.q = params.get('q') || '';
  state.country = params.get('country') || '';
  state.sector = params.get('sector') || '';
  if (search) search.value = state.q;

  function sectorsOf(mask) {
    var out = [];
    data.sectors.forEach(function (s, i) { if (mask & (1 << i)) out.push(SHORT[s] || s); });
    return out.join(', ') || 'Other fintech';
  }

  function rowHtml(r, blur) {
    var name = esc(r[0]), url = r[5], host = '';
    if (url) {
      host = url.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];
    }
    var prof = r[7] || '';
    var link = blur ? name
      : prof ? '<a href="' + esc(prof) + '">' + name + '</a>'
      : url ? '<a href="' + esc(url) + '" target="_blank" rel="nofollow noopener">' + name + '</a>' : name;
    var city = r[3] ? esc(r[3]) + ', ' : '';
    var pts = r[6] || 0;
    var trend = pts ? '<span class="db-trend"><span class="db-pts" title="Fintech Award Points">+' + fmt(pts) + '</span>' +
      (pts === data.top ? '<span class="db-top">#1 Fintech Award</span>' : '') + '</span>' : '';
    return '<tr' + (blur ? ' class="db-locked is-blur b' + blur + '" aria-hidden="true"' : '') + '>' +
      '<td class="db-name"><span class="db-co">' + link + '</span>' + trend + (host ? '<span class="db-host">' + esc(host) + '</span>' : '') + '</td>' +
      '<td class="db-sec">' + esc(sectorsOf(r[1])) + '</td>' +
      '<td class="db-loc">' + city + esc(data.countries[r[2]]) + '</td>' +
      '<td class="db-year">' + (r[4] || '–') + '</td></tr>';
  }

  function render() {
    var q = norm(state.q.trim());
    var sectorBit = state.sector === '' ? 0 : (1 << Number(state.sector));
    var cset = null;
    if (state.country === 'Nordics') {
      cset = data.nordics.map(function (c) { return data.countries.indexOf(c); });
    } else if (state.country) {
      cset = [data.countries.indexOf(state.country)];
    }
    var hits = [];
    for (var i = 0; i < data.rows.length; i++) {
      var r = data.rows[i];
      if (sectorBit && !(r[1] & sectorBit)) continue;
      if (cset && cset.indexOf(r[2]) === -1) continue;
      if (q && names[i].indexOf(q) === -1) continue;
      hits.push(r);
    }
    var shown = hits.slice(0, 10);
    tbody.innerHTML = shown.length
      ? shown.map(function (r, k) { return rowHtml(r, k >= 5 ? k - 4 : 0); }).join('')
      : '<tr class="db-empty"><td colspan="4">No fintechs match. Try another sector or country.</td></tr>';

    var where = state.country ? (state.country === 'Nordics' ? ' in the Nordics' : ' in ' + state.country) : '';
    var sec = state.sector !== '' ? ' · ' + (SHORT[data.sectors[state.sector]] || data.sectors[state.sector]) : '';
    var srch = state.q.trim() ? ' matching “' + esc(state.q.trim()) + '”' : '';
    var order = hits.length > 1 && hits[0][6] ? ', highest Fintech Award Points first' : '';
    countEl.innerHTML = 'Showing <b>' + shown.length + '</b> of <b>' + fmt(hits.length) + '</b> fintechs' + where + srch + sec + order;

    var more = hits.length - shown.length;
    gate.hidden = hits.length <= 5;
    if (more > 0) {
      moreEl.parentNode.innerHTML = '<b id="dbMore">' + fmt(more) + '</b> more fintechs' + where + ' in the database.';
    } else {
      moreEl.parentNode.innerHTML = '<b id="dbMore"></b>Get the full list, with the people to talk to.';
    }
    moreEl = document.getElementById('dbMore');

    // keep the URL shareable
    var p = new URLSearchParams();
    if (state.q.trim()) p.set('q', state.q.trim());
    if (state.sector !== '') p.set('sector', state.sector);
    if (state.country) p.set('country', state.country);
    var qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }

  function syncControls() {
    chips.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-sector') === state.sector)); });
    if (country) country.value = state.country;
  }

  fetch('/data/fintechs.json')
    .then(function (r) { return r.json(); })
    .then(function (j) {
      data = j;
      names = data.rows.map(function (r) { return norm(r[0] + ' ' + r[3]); });
      if (state.country && state.country !== 'Nordics' && data.countries.indexOf(state.country) === -1) state.country = '';
      syncControls();
      if (state.q || state.sector !== '' || state.country) render();

      var t;
      if (search) search.addEventListener('input', function () {
        clearTimeout(t);
        t = setTimeout(function () { state.q = search.value; render(); }, 140);
      });
      if (country) country.addEventListener('change', function () { state.country = country.value; render(); });
      chips.forEach(function (b) {
        b.addEventListener('click', function () {
          state.sector = b.getAttribute('data-sector');
          syncControls();
          render();
        });
      });
    })
    .catch(function () { /* the server-rendered first ten rows stay */ });
})();
