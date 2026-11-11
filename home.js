/* Alexandra Studio — landing page behaviour (index.html only). */
(function () {
  'use strict';

  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;

  /* ---------- mobile menu ---------- */
  (function () {
    var btn = document.querySelector('.hd-toggle');
    var nav = document.getElementById('nav');
    if (!btn || !nav) return;
    function setOpen(open) {
      nav.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }
    btn.addEventListener('click', function () { setOpen(!nav.classList.contains('open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { setOpen(false); btn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (nav.classList.contains('open') && !nav.contains(e.target) && !btn.contains(e.target)) setOpen(false);
    });
  })();

  /* ---------- hero people: rise once the cutouts are decoded ----------
     The hidden start state only applies when <html> has .js (set in <head>),
     so without JS the people are simply there. */
  (function () {
    var wrap = document.getElementById('heroPeople');
    if (!wrap) return;
    var started = false;
    function go() {
      if (started) return;
      started = true;
      requestAnimationFrame(function () { wrap.classList.add('is-in'); });
    }
    if (still) { go(); return; }
    var imgs = Array.prototype.slice.call(wrap.querySelectorAll('img'));
    var waits = imgs.map(function (img) {
      if (img.decode) return img.decode().catch(function () {});
      return new Promise(function (res) {
        if (img.complete) return res();
        img.addEventListener('load', res); img.addEventListener('error', res);
      });
    });
    if (window.Promise) Promise.all(waits).then(go); else go();
    setTimeout(go, 2500); // never leave them hidden on a slow connection
  })();

  /* ---------- odometer counters (59 / 40 / 12) ----------
     Each digit is a vertical strip that rolls like a mechanical counter.
     The ones column rolls through every value from 0 up to the target, the
     tens column rolls 0 → target tens, so it reads as counting up. */
  (function () {
    var stats = Array.prototype.slice.call(document.querySelectorAll('.stat, .odo-scope'));
    if (!stats.length || still || !hasIO) return;
    document.documentElement.classList.add('js-odo');

    var DURATION = 2200; // ms
    var EASE = 'cubic-bezier(.16,1,.3,1)';

    stats.forEach(function (stat) {
      var odo = stat.querySelector('.odo');
      if (!odo) return;
      var target = parseInt(odo.getAttribute('data-to'), 10);
      if (isNaN(target)) return;
      var str = String(target);
      odo.textContent = '';
      odo.setAttribute('aria-hidden', 'true');

      str.split('').forEach(function (ch, i) {
        // how many cells this column has to travel
        var place = Math.pow(10, str.length - 1 - i);
        var steps = Math.floor(target / place); // e.g. 59 → tens: 5, ones: 59
        // Big numbers (4246) would make strips thousands of cells tall, which
        // phones refuse to draw. Cap it: spin a couple of full turns, then land.
        if (steps > 29) steps = 20 + Number(ch);
        var col = document.createElement('span');
        col.className = 'odo-col';
        var strip = document.createElement('span');
        strip.className = 'odo-strip';
        for (var n = 0; n <= steps; n++) {
          var cell = document.createElement('span');
          cell.textContent = String(n % 10);
          strip.appendChild(cell);
        }
        strip.dataset.steps = steps;
        strip.style.transition = 'transform ' + DURATION + 'ms ' + EASE + ' ' + (i * 60) + 'ms';
        col.appendChild(strip);
        odo.appendChild(col);
      });
    });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var stat = entry.target;
        io.unobserve(stat);
        var delay = stats.indexOf(stat) * 160;
        setTimeout(function () {
          stat.classList.add('is-in');
          Array.prototype.forEach.call(stat.querySelectorAll('.odo-strip'), function (strip) {
            strip.style.transform = 'translate3d(0,' + (-1.1 * Number(strip.dataset.steps)) + 'em,0)';
          });
        }, delay);
      });
    }, { threshold: 0.45 });

    stats.forEach(function (s) { io.observe(s); });
  })();

  /* ---------- YouTube background video ----------
     Injected only when the box is near the viewport, muted and looping.
     With reduced motion the still thumbnail stays instead. */
  (function () {
    var box = document.querySelector('.growth-video[data-yt]');
    if (!box || still) return;
    var id = box.getAttribute('data-yt');
    var start = box.getAttribute('data-start') || '0';

    function inject() {
      if (box.querySelector('iframe')) return;
      var src = 'https://www.youtube-nocookie.com/embed/' + id +
        '?autoplay=1&mute=1&controls=0&loop=1&playlist=' + id +
        '&start=' + start + '&playsinline=1&rel=0&modestbranding=1&iv_load_policy=3&disablekb=1&fs=0';
      var f = document.createElement('iframe');
      f.src = src;
      f.title = 'Background video';
      f.setAttribute('tabindex', '-1');
      f.setAttribute('aria-hidden', 'true');
      f.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
      f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      f.addEventListener('load', function () {
        // give the player a moment to start so the fade never shows a black frame
        setTimeout(function () { f.classList.add('is-ready'); }, 900);
      });
      box.appendChild(f);
    }

    if (!hasIO) { inject(); return; }
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { inject(); io.disconnect(); }
    }, { rootMargin: '400px 0px' });
    io.observe(box);
  })();
})();
