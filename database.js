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

  /* ---------- hub pages: filter the full list in place ---------- */
  var hubInput = document.querySelector('[data-hub-filter]');
  if (hubInput) {
    var hubRows = Array.prototype.slice.call(document.querySelectorAll('[data-hub-rows] tr'));
    var idx = hubRows.map(function (tr) { return norm(tr.textContent); });
    var t;
    hubInput.addEventListener('input', function () {
      clearTimeout(t);
      t = setTimeout(function () {
        var q = norm(hubInput.value.trim());
        hubRows.forEach(function (tr, i) { tr.hidden = q && idx[i].indexOf(q) === -1; });
      }, 120);
    });
  }

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
    var link = url && !blur ? '<a href="' + esc(url) + '" target="_blank" rel="nofollow noopener">' + name + '</a>' : name;
    var city = r[3] ? esc(r[3]) + ', ' : '';
    return '<tr' + (blur ? ' class="is-blur b' + blur + '" aria-hidden="true"' : '') + '>' +
      '<td class="db-name"><span class="db-co">' + link + '</span>' + (host ? '<span class="db-host">' + esc(host) + '</span>' : '') + '</td>' +
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
    countEl.innerHTML = 'Showing <b>' + shown.length + '</b> of <b>' + fmt(hits.length) + '</b> fintechs' + where + srch + sec;

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
