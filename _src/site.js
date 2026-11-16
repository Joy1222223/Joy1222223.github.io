(function () {
  var touch = matchMedia('(hover:none)').matches;
  // mobile menu
  var burger = document.getElementById('burger');
  if (burger) burger.addEventListener('click', function () { document.body.classList.toggle('menu'); });

  // ripple + press on anything .ripple
  document.addEventListener('pointerdown', function (e) {
    var el = e.target.closest('.ripple');
    if (el) {
      el.classList.add('pressed');
    }
    if (document.body.classList.contains('home') && e.target.closest('.hero')) {
      if (window.__boom) window.__boom(e.clientX, e.clientY);
    }
  });
  ['pointerup', 'pointerleave', 'pointercancel'].forEach(function (ev) {
    document.addEventListener(ev, function () { document.querySelectorAll('.pressed').forEach(function (x) { x.classList.remove('pressed'); }); }, true);
  });

  // reveal on scroll
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: .08, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.reveal').forEach(function (el, i) { el.style.transitionDelay = (i % 3) * 80 + 'ms'; io.observe(el); });

  // tilt + glare + hover video on cards
  document.querySelectorAll('.tilt').forEach(function (c) {
    var v = c.querySelector('video.hv');
    c.addEventListener('pointermove', function (e) {
      var r = c.getBoundingClientRect(), px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
      c.style.setProperty('--gx', px * 100 + '%'); c.style.setProperty('--gy', py * 100 + '%');
      if (!touch && !c.classList.contains('pressed')) c.style.transform = 'perspective(1000px) rotateY(' + ((px - .5) * 10) + 'deg) rotateX(' + ((.5 - py) * 8) + 'deg) translateZ(6px)';
    });
    c.addEventListener('pointerenter', function () {
      if (v && !touch) { if (!v.src) { v.src = v.dataset.src; v.addEventListener('playing', function () { v.classList.add('ready'); }, { once: true }); } v.play().catch(function () {}); }
    });
    c.addEventListener('pointerleave', function () { c.style.transform = ''; if (v) v.pause(); });
  });

  // magnetic buttons
  if (!touch) document.querySelectorAll('.mag').forEach(function (b) {
    b.addEventListener('pointermove', function (e) {
      var r = b.getBoundingClientRect(); b.style.transform = 'translate(' + (e.clientX - r.left - r.width / 2) * .22 + 'px,' + (e.clientY - r.top - r.height / 2) * .3 + 'px)';
    });
    b.addEventListener('pointerleave', function () { b.style.transform = ''; });
  });

  // lightbox
  var lb = document.getElementById('lb'), lbi = lb && lb.querySelector('img');
  document.addEventListener('click', function (e) {
    var im = e.target.closest('img.zoomable, .g-item img');
    if (im && lb) { lbi.src = im.currentSrc || im.src; lb.classList.add('on'); }
  });
  if (lb) lb.addEventListener('click', function () { lb.classList.remove('on'); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && lb) lb.classList.remove('on'); });

  // only one playing video at a time
  document.addEventListener('play', function (e) {
    if (!e.target.controls) return;
    document.querySelectorAll('video[controls]').forEach(function (v) { if (v !== e.target) v.pause(); });
  }, true);

  // before / after compare sliders
  document.querySelectorAll('.cmp-box').forEach(function (b) {
    var r = b.querySelector('.cmp-rng'), la = b.querySelector('.cmp-lab.l'), lr = b.querySelector('.cmp-lab.r');
    function set(v) {
      b.style.setProperty('--p', v + '%');
      if (la) la.style.opacity = v < 12 ? 0 : 1;
      if (lr) lr.style.opacity = v > 88 ? 0 : 1;
    }
    r.addEventListener('input', function () { b.dataset.used = 1; set(+r.value); });
    r.addEventListener('pointerdown', function () { b.classList.add('drag'); });
    ['pointerup', 'pointercancel', 'blur'].forEach(function (ev) { r.addEventListener(ev, function () { b.classList.remove('drag'); }); });
    // first time it scrolls into view: a little wiggle so people know it can be dragged
    if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion:reduce)').matches) return;
    var io = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      io.disconnect();
      var t0 = performance.now();
      (function step(t) {
        if (b.dataset.used) return;
        var k = Math.min((t - t0) / 1800, 1);
        set(50 + 22 * Math.sin(k * Math.PI * 2) * (1 - k));
        if (k < 1) requestAnimationFrame(step);
      })(t0);
    }, { threshold: .6 });
    io.observe(b);
  });

  // Apple-style switch stages
  document.querySelectorAll('.sw').forEach(function (sw) {
    var tabs = [].slice.call(sw.querySelectorAll('.sw-tab')), items = [].slice.call(sw.querySelectorAll('.sw-item'));
    var ind = sw.querySelector('.sw-ind'), stage = sw.querySelector('.sw-stage'), cur = 0, visible = false;
    function place() { var t = tabs[cur]; if (t && ind) { ind.style.width = t.offsetWidth + 'px'; ind.style.transform = 'translateX(' + t.offsetLeft + 'px)'; } }
    function vid(i) { return items[i] && items[i].querySelector('video'); }
    function playCur() { var v = vid(cur); if (!v) return; if (v.preload !== 'auto') v.preload = 'auto'; if (visible) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } }
    function go(i) {
      i = (i + items.length) % items.length; if (i === cur) return;
      var old = vid(cur); if (old) old.pause();
      items[cur].classList.remove('on'); tabs[cur].classList.remove('on'); tabs[cur].setAttribute('aria-selected', 'false');
      cur = i; items[cur].classList.add('on'); tabs[cur].classList.add('on'); tabs[cur].setAttribute('aria-selected', 'true');
      var v = vid(cur); if (v) { try { v.currentTime = 0; } catch (e) {} }
      place(); playCur();
      tabs[cur].scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' });
    }
    tabs.forEach(function (t, i) { t.addEventListener('click', function () { go(i); }); });
    sw.querySelector('.sw-tabs').addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { go(cur + 1); tabs[cur].focus(); } else if (e.key === 'ArrowLeft') { go(cur - 1); tabs[cur].focus(); }
    });
    // swipe on the stage
    var sx = null;
    stage.addEventListener('pointerdown', function (e) { sx = e.target.closest('.cmp-box') ? null : e.clientX; });
    stage.addEventListener('pointerup', function (e) { if (sx === null) return; var dx = e.clientX - sx; sx = null; if (Math.abs(dx) > 50) go(cur + (dx < 0 ? 1 : -1)); });
    // progress bars
    items.forEach(function (it) {
      var v = it.querySelector('video'), bar = it.querySelector('.sw-prog i'); if (!v || !bar) return;
      v.addEventListener('timeupdate', function () { if (v.duration) bar.style.width = (v.currentTime / v.duration * 100) + '%'; });
    });
    // play only while on screen
    new IntersectionObserver(function (es) {
      visible = es[0].isIntersecting;
      if (visible) playCur(); else items.forEach(function (_, i) { var v = vid(i); if (v) v.pause(); });
    }, { threshold: .35 }).observe(stage);
    window.addEventListener('resize', place); setTimeout(place, 60); place();
  });
  // scroll-driven grow (stage scales up as it reaches the middle of the screen)
  var grow = [].slice.call(document.querySelectorAll('.sw'));
  if (grow.length && !matchMedia('(prefers-reduced-motion:reduce)').matches) {
    var tick = false;
    function upd() {
      tick = false; var vh = innerHeight;
      grow.forEach(function (el) { var r = el.getBoundingClientRect(); var k = Math.max(0, Math.min(1, (vh - r.top) / (vh * .55))); el.style.setProperty('--k', k.toFixed(3)); });
    }
    addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive: true }); upd();
  }
  // count-up stats
  document.querySelectorAll('.st b[data-n]').forEach(function (b) {
    var n = parseFloat(b.dataset.n), dec = (b.dataset.n.split('.')[1] || '').length, done = false;
    if (isNaN(n)) return; b.textContent = (0).toFixed(dec);
    new IntersectionObserver(function (es, o) {
      if (!es[0].isIntersecting || done) return; done = true; o.disconnect();
      var t0 = performance.now();
      (function step(t) { var k = Math.min((t - t0) / 1400, 1); k = 1 - Math.pow(1 - k, 3); b.textContent = (n * k).toFixed(dec); if (k < 1) requestAnimationFrame(step); })(t0);
    }, { threshold: .6 }).observe(b);
  });

  // drag-a-slider parameter explorer
  document.querySelectorAll('.pm').forEach(function (pm) {
    var tabs = [].slice.call(pm.querySelectorAll('.pm-tabs .sw-tab')), mats = [].slice.call(pm.querySelectorAll('.pm-mat'));
    var ind = pm.querySelector('.pm-tabs .sw-ind'), cur = 0, cache = {};
    var bc = document.body.classList, hint = bc.contains('lang-zh-hant') ? '拖動滑桿試試看' : bc.contains('lang-zh-hans') ? '拖动滑块试试看' : 'Drag the slider';
    pm.querySelectorAll('.pm-hint').forEach(function (h) { h.textContent = hint; });
    function place() { var t = tabs[cur]; if (t && ind) { ind.style.width = t.offsetWidth + 'px'; ind.style.transform = 'translateX(' + t.offsetLeft + 'px)'; } }
    function preload(src, n) { if (cache[src]) return; cache[src] = []; for (var i = 0; i < n; i++) { var im = new Image(); im.src = src + (i < 10 ? '0' : '') + i + '.webp'; cache[src].push(im); } }
    mats.forEach(function (m) {
      var img = m.querySelector('.pm-img'), range = m.querySelector('.pm-range'), val = m.querySelector('.pm-val'),
          name = m.querySelector('.pm-name'), ends = m.querySelectorAll('.pm-ends span'), chips = [].slice.call(m.querySelectorAll('.pm-chip'));
      var chip = chips[0];
      function vals() { return JSON.parse(chip.dataset.vals); }
      function show(i) {
        var v = vals(); i = Math.max(0, Math.min(v.length - 1, i | 0));
        img.src = chip.dataset.src + (i < 10 ? '0' : '') + i + '.webp';
        val.textContent = v[i];
        range.style.setProperty('--p', (i / (v.length - 1) * 100) + '%');
      }
      function pick(c) {
        chip = c; chips.forEach(function (x) { x.classList.toggle('on', x === c); });
        var v = vals(); range.max = v.length - 1; range.value = c.dataset.def;
        name.textContent = c.textContent; range.setAttribute('aria-label', c.textContent);
        ends[0].textContent = v[0]; ends[1].textContent = v[v.length - 1];
        preload(c.dataset.src, v.length); show(+range.value);
      }
      chips.forEach(function (c) { c.addEventListener('click', function () { pick(c); pm.classList.add('used'); }); });
      range.addEventListener('input', function () { show(+range.value); pm.classList.add('used'); });
      m._pick = function () { pick(chip); };
      pick(chip);
    });
    function go(i) {
      if (i === cur) return;
      mats[cur].classList.remove('on'); tabs[cur].classList.remove('on'); tabs[cur].setAttribute('aria-selected', 'false');
      cur = i; mats[cur].classList.add('on'); tabs[cur].classList.add('on'); tabs[cur].setAttribute('aria-selected', 'true');
      place();
    }
    tabs.forEach(function (t, i) { t.addEventListener('click', function () { go(i); }); });
    // first time it scrolls into view: sweep the slider once so people see it is alive
    new IntersectionObserver(function (es, o) {
      if (!es[0].isIntersecting) return; o.disconnect();
      if (matchMedia('(prefers-reduced-motion:reduce)').matches) return;
      var m = mats[cur], r = m.querySelector('.pm-range'), d = +r.value, max = +r.max, t0 = performance.now();
      (function step(t) {
        if (pm.classList.contains('used')) return;
        var k = Math.min((t - t0) / 2600, 1), x = k < .5 ? d + (max - d) * Math.sin(k * Math.PI) : d - d * Math.sin((k - .5) * Math.PI * 2) * .9;
        r.value = Math.round(x); r.dispatchEvent(new Event('input')); pm.classList.remove('used');
        if (k < 1) requestAnimationFrame(step); else { r.value = d; r.dispatchEvent(new Event('input')); pm.classList.remove('used'); }
      })(t0);
    }, { threshold: .5 }).observe(pm.querySelector('.pm-stage'));
    addEventListener('resize', place); setTimeout(place, 60); place();
  });

  // ---- home hero ----
  var hero = document.getElementById('hero');
  if (!hero) return;
  var d = 0;
  document.querySelectorAll('#name .w').forEach(function (w) {
    var t = w.textContent; w.textContent = '';
    t.split('').forEach(function (ch) { var s = document.createElement('span'); s.className = 'l'; s.textContent = ch; s.style.animationDelay = (.35 + d * .05) + 's'; d++; w.appendChild(s); });
  });
  var card = document.getElementById('hcard'), bg = hero.querySelector('.hv-bg');
  hero.addEventListener('pointermove', function (e) {
    var r = card.getBoundingClientRect(); card.style.setProperty('--mx', (e.clientX - r.left) + 'px'); card.style.setProperty('--my', (e.clientY - r.top) + 'px');
    if (touch) return;
    var cx = e.clientX / innerWidth - .5, cy = e.clientY / innerHeight - .5;
    card.style.transform = 'perspective(1200px) rotateY(' + cx * 5 + 'deg) rotateX(' + (-cy * 5) + 'deg)';
    bg.style.transform = 'scale(1.08) translate(' + (-cx * 14) + 'px,' + (-cy * 10) + 'px)';
  });
  // particles
  var c = document.getElementById('particles'), x = c.getContext('2d'), W, H, dpr = Math.min(devicePixelRatio || 1, 2), P = [], m = { x: -9999, y: -9999 }, last = 0;
  var COL = '46,230,201', LINK = 130, REP = 120;
  function size() { W = c.clientWidth; H = c.clientHeight; c.width = W * dpr; c.height = H * dpr; x.setTransform(dpr, 0, 0, dpr, 0, 0); var n = Math.round(Math.min(120, W * H / 10000)); P = []; for (var i = 0; i < n; i++) P.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35, r: Math.random() * 1.6 + .6, t: Math.random() * 6.28 }); }
  window.__boom = function (px, py) { var r = hero.getBoundingClientRect(); px -= r.left; py -= r.top; P.forEach(function (p) { var dx = p.x - px, dy = p.y - py, dd = Math.hypot(dx, dy) || 1; if (dd < 260) { var k = (260 - dd) / 260 * 6; p.vx += dx / dd * k; p.vy += dy / dd * k; } }); };
  addEventListener('resize', size);
  hero.addEventListener('pointermove', function (e) { var r = hero.getBoundingClientRect(); m.x = e.clientX - r.left; m.y = e.clientY - r.top; last = Date.now(); });
  var visible = true;
  new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(hero);
  function f(ts) {
    requestAnimationFrame(f);
    if (!visible) return;
    x.clearRect(0, 0, W, H);
    if (Date.now() - last > 2000) { m.x = W * (.62 + .28 * Math.sin(ts * .00023)); m.y = H * (.5 + .32 * Math.sin(ts * .00037)); }
    for (var i = 0; i < P.length; i++) {
      var p = P[i], dx = p.x - m.x, dy = p.y - m.y, dd = Math.sqrt(dx * dx + dy * dy);
      if (dd < REP && dd > 0) { var k = (REP - dd) / REP * 1.2; p.x += dx / dd * k; p.y += dy / dd * k; }
      p.vx *= .96; p.vy *= .96; if (Math.abs(p.vx) < .15) p.vx += (Math.random() - .5) * .05; if (Math.abs(p.vy) < .15) p.vy += (Math.random() - .5) * .05;
      p.x += p.vx; p.y += p.vy; p.t += .02;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0; if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      var q2 = p.r * 1.5; x.fillStyle = 'rgba(' + COL + ',' + (.45 + .35 * Math.sin(p.t)) + ')'; x.shadowColor = 'rgba(' + COL + ',.9)'; x.shadowBlur = 8; x.fillRect(p.x - q2 / 2, p.y - q2 / 2, q2, q2); x.shadowBlur = 0;
      for (var j = i + 1; j < P.length; j++) { var q = P[j], ex = p.x - q.x, ey = p.y - q.y, e = ex * ex + ey * ey; if (e < LINK * LINK) { x.strokeStyle = 'rgba(' + COL + ',' + (.18 * (1 - Math.sqrt(e) / LINK)) + ')'; x.lineWidth = .6; x.beginPath(); x.moveTo(p.x, p.y); x.lineTo(q.x, q.y); x.stroke(); } }
      if (dd < LINK * 1.4) { x.strokeStyle = 'rgba(' + COL + ',' + (.35 * (1 - dd / (LINK * 1.4))) + ')'; x.lineWidth = .8; x.beginPath(); x.moveTo(p.x, p.y); x.lineTo(m.x, m.y); x.stroke(); }
    }
  }
  size(); requestAnimationFrame(f);
})();
