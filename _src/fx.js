/* Extra interactions: cursor, click sparks, scramble text, progress bar,
   page transitions, playful pills, easter egg. Loaded after site.js. */
(function () {
  var fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
  var calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var TEAL = [46, 230, 201], VIOLET = [140, 110, 255];
  var root = document.documentElement;

  /* ---- scroll progress bar ---- */
  var bar = document.createElement('div'); bar.className = 'progress'; document.body.appendChild(bar);
  function prog() { var h = root.scrollHeight - innerHeight; bar.style.transform = 'scaleX(' + (h > 0 ? scrollY / h : 0) + ')'; }
  addEventListener('scroll', prog, { passive: true }); addEventListener('resize', prog); prog();

  /* ---- background spotlight that follows the pointer ---- */
  addEventListener('pointermove', function (e) {
    root.style.setProperty('--sx', e.clientX + 'px'); root.style.setProperty('--sy', e.clientY + 'px');
  }, { passive: true });

  /* ---- full-screen FX canvas: click sparks, cursor trail, easter egg ---- */
  var fx = document.createElement('canvas'); fx.className = 'fx'; document.body.appendChild(fx);
  var g = fx.getContext('2d'), FW, FH, dpr = Math.min(devicePixelRatio || 1, 2), S = [], running = false;
  function fsize() { FW = innerWidth; FH = innerHeight; fx.width = FW * dpr; fx.height = FH * dpr; g.setTransform(dpr, 0, 0, dpr, 0, 0); }
  fsize(); addEventListener('resize', fsize);
  function spark(x, y, n, speed, col, life, grav) {
    for (var i = 0; i < n; i++) {
      var a = Math.random() * 6.283, v = speed * (0.35 + Math.random() * 0.65);
      S.push({ x: x, y: y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, l: life * (0.6 + Math.random() * 0.4), m: life,
               r: 1 + Math.random() * 2.2, c: col || (Math.random() < 0.75 ? TEAL : VIOLET), g: grav || 0 });
    }
    if (!running) { running = true; requestAnimationFrame(tick); }
  }
  function tick() {
    g.clearRect(0, 0, FW, FH);
    for (var i = S.length - 1; i >= 0; i--) {
      var s = S[i]; s.l--;
      if (s.l <= 0) { S.splice(i, 1); continue; }
      s.vx *= 0.94; s.vy = s.vy * 0.94 + s.g; s.x += s.vx; s.y += s.vy;
      var a = s.l / s.m;
      var col = 'rgba(' + s.c[0] + ',' + s.c[1] + ',' + s.c[2] + ',' + a + ')';
      g.shadowColor = col; g.shadowBlur = 10;
      if (Math.abs(s.vx) + Math.abs(s.vy) > 0.6) {   // fast: a light streak
        g.strokeStyle = col; g.lineWidth = s.r * a + 0.4; g.lineCap = 'butt';
        g.beginPath(); g.moveTo(s.x, s.y); g.lineTo(s.x - s.vx * 3, s.y - s.vy * 3); g.stroke();
      } else {                                         // slow: a small square
        var q = s.r * a * 1.6 + 0.6; g.fillStyle = col; g.fillRect(s.x - q / 2, s.y - q / 2, q, q);
      }
    }
    g.shadowBlur = 0;
    if (S.length) requestAnimationFrame(tick); else running = false;
  }
  window.__spark = spark;
  /* ---- soft light halo that trails the cursor (system cursor stays) ---- */
  if (fine && !calm) {
    var halo = document.createElement('div'); halo.className = 'halo'; document.body.appendChild(halo);
    var hx = -200, hy = -200, tx = -200, ty = -200, moving = false;
    addEventListener('pointermove', function (e) {
      tx = e.clientX; ty = e.clientY; halo.classList.add('on');
      if (!moving) { moving = true; requestAnimationFrame(follow); }
    }, { passive: true });
    function follow() {
      hx += (tx - hx) * 0.2; hy += (ty - hy) * 0.2;
      halo.style.transform = 'translate(' + hx + 'px,' + hy + 'px)';
      if (Math.abs(tx - hx) + Math.abs(ty - hy) > 0.3) requestAnimationFrame(follow); else moving = false;
    }
    document.addEventListener('pointerover', function (e) {
      halo.classList.toggle('hot', !!e.target.closest('a, button, .ripple, .pill, img.zoomable, .g-item, video'));
    });
    document.documentElement.addEventListener('pointerleave', function () { halo.classList.remove('on'); });
    document.addEventListener('pointerdown', function () { halo.classList.add('press'); });
    document.addEventListener('pointerup', function () { halo.classList.remove('press'); });
  }

  /* ---- click: a soft light pulse ---- */
  if (!calm) document.addEventListener('pointerdown', function (e) {
    ['pulse', 'pulse-ring', 'pulse-ring r2'].forEach(function (c) {
      var p = document.createElement('div'); p.className = c;
      p.style.left = e.clientX + 'px'; p.style.top = e.clientY + 'px';
      document.body.appendChild(p); setTimeout(function () { p.remove(); }, 900);
    });
    // the clicked control flashes with light
    var el = e.target.closest('a, button, .ripple, .pill, .pcard');
    if (el) { el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash'); setTimeout(function () { el.classList.remove('flash'); }, 600); }
  });

  /* ---- Apple-style hover (mouse only) ---- */
  if (fine && !calm) {
    // 1. soft light that follows the pointer inside buttons / pills / links (visionOS-like sheen)
    document.querySelectorAll('.btn, .nl, .lg, .pill, .crumb, .sub a, .logo').forEach(function (el) {
      el.classList.add('has-sheen');
      var sh = document.createElement('span'); sh.className = 'sheen'; el.appendChild(sh);
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--hx', (e.clientX - r.left) + 'px'); el.style.setProperty('--hy', (e.clientY - r.top) + 'px');
      });
    });
    // 2. iPadOS-style highlight that glides between nav items
    var nav = document.getElementById('nav');
    if (nav && matchMedia('(min-width: 981px)').matches) {
      var hl = document.createElement('div'); hl.className = 'nav-hl'; nav.appendChild(hl);
      var shown = false;
      nav.querySelectorAll('.nl').forEach(function (a) {
        a.addEventListener('pointerenter', function () {
          var nr = nav.getBoundingClientRect(), r = a.getBoundingClientRect();
          if (!shown) hl.style.transition = 'none';
          hl.style.width = r.width + 'px'; hl.style.height = r.height + 'px';
          hl.style.transform = 'translate(' + (r.left - nr.left) + 'px,' + (r.top - nr.top) + 'px)';
          void hl.offsetWidth; hl.style.transition = ''; hl.classList.add('on'); shown = true;
        });
      });
      nav.addEventListener('pointerleave', function () { hl.classList.remove('on'); shown = false; });
    }
  }

  /* ---- page transitions for links inside the site ---- */
  var veil = document.createElement('div'); veil.className = 'veil'; document.body.appendChild(veil);
  setTimeout(function () { document.body.classList.add('loaded'); }, 30);
  addEventListener('pageshow', function (e) { if (e.persisted) { document.body.classList.remove('leaving'); document.body.classList.add('loaded'); } });
  if (!calm) document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || a.target === '_blank') return;
    if (/^(mailto|tel|javascript):/i.test(a.getAttribute('href'))) return;
    var u = new URL(a.href, location.href);
    if (u.origin !== location.origin) return;
    if (u.pathname === location.pathname && u.search === location.search) return; // same-page anchors
    e.preventDefault(); document.body.classList.add('leaving');
    setTimeout(function () { location.href = u.href; }, 380);
  });

  /* ---- easter egg: type "joy" anywhere ---- */
  var buf = '';
  addEventListener('keydown', function (e) {
    if (/input|textarea|select/i.test(e.target.tagName || '')) return;
    buf = (buf + (e.key || '').toLowerCase()).slice(-3);
    if (buf !== 'joy') return;
    for (var i = 0; i < 14; i++) setTimeout(function () { spark(Math.random() * FW, Math.random() * FH * 0.6, 30, 10, null, 60, 0.12); }, i * 90);
    var t = document.createElement('div'); t.className = 'egg glass'; t.textContent = '✦ Hi, I’m Joy ✦';
    document.body.appendChild(t); setTimeout(function () { t.remove(); }, 2600);
  });
})();
