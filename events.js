/* Insider Events: countdowns to the registration deadline, "days left to
   register" and live view counts. Loaded by insider-events.html and
   events/*.html only. */
(function () {
  'use strict';

  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function split(ms) {
    var s = Math.max(0, Math.floor(ms / 1000));
    return { d: Math.floor(s / 86400), h: Math.floor((s % 86400) / 3600), m: Math.floor((s % 3600) / 60), s: s % 60 };
  }
  function time(attr) { var v = attr && Date.parse(attr); return v && !isNaN(v) ? v : null; }
  function deadline(el) { return time(el.getAttribute('data-close')) || time(el.getAttribute('data-start')); }

  /* ---------- countdowns ----------
     Count down to data-close (registration deadline), falling back to
     data-start. Without either, the element keeps its text. */
  var counters = Array.prototype.slice.call(document.querySelectorAll('[data-countdown]'));
  var regs = Array.prototype.slice.call(document.querySelectorAll('[data-regleft]'));

  function renderCounter(el, now) {
    var target = deadline(el);
    if (!target) return;
    var t = target - now;
    var out = el.querySelector('[data-out]') || el;
    if (t <= 0) {
      el.classList.add('is-closed');
      if (el.hasAttribute('data-full')) {
        el.innerHTML = '<p class="ep-tba">Registration closed</p>';
        counters.splice(counters.indexOf(el), 1);
      } else {
        var label = el.querySelector('.ev-pill-label');
        if (label) label.remove();
        out.textContent = 'Registration closed';
      }
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
    var close = deadline(el);
    if (!close) return; // keeps "Registration open"
    var out = el.querySelector('[data-out]') || el;
    var ms = close - now;
    if (ms <= 0) { out.textContent = 'Registration closed'; return; }
    if (ms < 86400000) {
      var hours = Math.max(1, Math.ceil(ms / 3600000));
      out.textContent = hours + (hours === 1 ? ' hour' : ' hours') + ' left to register';
    } else {
      var days = Math.floor(ms / 86400000);
      out.textContent = days + (days === 1 ? ' day' : ' days') + ' left to register';
    }
  }

  function tick() {
    var now = Date.now();
    counters.slice().forEach(function (el) { renderCounter(el, now); });
    regs.forEach(function (el) { renderReg(el, now); });
  }
  if (counters.length || regs.length) {
    tick();
    setInterval(tick, 1000);
  }

  /* ---------- live view counts ----------
     [data-views][data-key][data-seed][data-mode="hit"|"get"]
     Number shown = starting number + real views counted by a free counter
     (abacus.jasoncameron.dev). Event pages count a view ("hit"); the index
     only reads ("get"). The number ticks up on load and is re-checked every
     20 seconds, so new visits show up live. If the counter can't be reached,
     the starting number stays. */
  var NS = 'alexandrastudio.se';
  var API = 'https://abacus.jasoncameron.dev/';
  var fmt = function (n) { return n.toLocaleString('en-US'); };

  function animateTo(el, from, to, ms) {
    if (still || from >= to) { el.textContent = fmt(to); return; }
    var t0 = null;
    function step(t) {
      if (!t0) t0 = t;
      var k = Math.min(1, (t - t0) / ms);
      var e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(Math.round(from + (to - from) * e));
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function bump(wrap) {
    if (still) return;
    wrap.classList.remove('is-bump');
    void wrap.offsetWidth;
    wrap.classList.add('is-bump');
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-views]'), function (wrap) {
    var key = wrap.getAttribute('data-key');
    var seed = parseInt(wrap.getAttribute('data-seed'), 10) || 0;
    var mode = wrap.getAttribute('data-mode') === 'hit' ? 'hit' : 'get';
    var out = wrap.querySelector('b') || wrap;
    var shown = seed;
    if (!key || !window.fetch) return;

    function read(m, first) {
      return fetch(API + m + '/' + NS + '/event-' + key, { mode: 'cors' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          var n = j && Number(j.value);
          if (!n || isNaN(n)) return;
          var total = seed + n;
          if (first) {
            // tick up into the real number on first load
            animateTo(out, Math.max(seed, total - Math.min(14, Math.ceil(total * 0.06))), total, 1200);
          } else if (total > shown) {
            animateTo(out, shown, total, 600);
            bump(wrap);
          }
          shown = total;
        })
        .catch(function () {});
    }

    read(mode, true);
    setInterval(function () { if (!document.hidden) read('get', false); }, 20000);
  });
})();
