/* Insider Events: countdowns, "days left to register" and view counts.
   Loaded by insider-events.html and events/*.html only. */
(function () {
  'use strict';

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function split(ms) {
    var s = Math.max(0, Math.floor(ms / 1000));
    return { d: Math.floor(s / 86400), h: Math.floor((s % 86400) / 3600), m: Math.floor((s % 3600) / 60), s: s % 60 };
  }
  function time(attr) { var v = attr && Date.parse(attr); return v && !isNaN(v) ? v : null; }

  /* ---------- countdowns ----------
     [data-countdown][data-start="2026-12-10T18:00:00+01:00"]
     Without a data-start the element keeps its text ("Date to be announced"). */
  var counters = Array.prototype.slice.call(document.querySelectorAll('[data-countdown]'));
  var regs = Array.prototype.slice.call(document.querySelectorAll('[data-regleft]'));

  function renderCounter(el, now) {
    var start = time(el.getAttribute('data-start'));
    if (!start) return;
    var end = time(el.getAttribute('data-end')) || start + 3 * 3600 * 1000;
    var t = start - now;
    var out = el.querySelector('[data-out]') || el;
    if (t <= 0) {
      out.textContent = now < end ? 'Happening now' : 'This event has ended';
      if (el.hasAttribute('data-full')) el.classList.add('is-over');
      return;
    }
    var p = split(t);
    if (el.hasAttribute('data-full')) {
      ['d', 'h', 'm', 's'].forEach(function (k) {
        var b = el.querySelector('[data-' + k + ']');
        if (b) b.textContent = k === 'd' ? String(p.d) : pad(p[k]);
      });
    } else {
      out.textContent = p.d + 'd ' + pad(p.h) + 'h ' + pad(p.m) + 'm ' + pad(p.s) + 's';
    }
  }

  function renderReg(el, now) {
    var close = time(el.getAttribute('data-close')) || time(el.getAttribute('data-start'));
    if (!close) return; // keeps "Registration open"
    var out = el.querySelector('[data-out]') || el;
    var ms = close - now;
    if (ms <= 0) { out.textContent = 'Registration closed'; return; }
    var days = Math.ceil(ms / 86400000);
    if (ms < 86400000) {
      var hours = Math.max(1, Math.ceil(ms / 3600000));
      out.textContent = hours + (hours === 1 ? ' hour' : ' hours') + ' left to register';
    } else {
      out.textContent = days + (days === 1 ? ' day' : ' days') + ' left to register';
    }
  }

  function tick() {
    var now = Date.now();
    counters.forEach(function (el) { renderCounter(el, now); });
    regs.forEach(function (el) { renderReg(el, now); });
  }
  if (counters.length || regs.length) {
    tick();
    setInterval(tick, 1000);
  }

  /* ---------- view counts ----------
     [data-views][data-key][data-seed][data-mode="hit"|"get"]
     Shows the starting number plus real views counted by a free counter
     (abacus.jasoncameron.dev). If the counter can't be reached, the starting
     number stays. Event pages count a view ("hit"); the index only reads ("get"). */
  var NS = 'alexandrastudio.se';
  Array.prototype.forEach.call(document.querySelectorAll('[data-views]'), function (el) {
    var key = el.getAttribute('data-key');
    var seed = parseInt(el.getAttribute('data-seed'), 10) || 0;
    var mode = el.getAttribute('data-mode') === 'hit' ? 'hit' : 'get';
    var out = el.querySelector('b') || el;
    if (!key || !window.fetch) return;
    fetch('https://abacus.jasoncameron.dev/' + mode + '/' + NS + '/event-' + key, { mode: 'cors' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        var n = j && Number(j.value);
        if (n && !isNaN(n)) out.textContent = (seed + n).toLocaleString('en-US');
      })
      .catch(function () {});
  });
})();
