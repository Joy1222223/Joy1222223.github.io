// Live 3D view for the drag-a-slider parameter explorer (loaded on demand by site.js).
// Same rounded cylinder as the offline renders: height-map displacement, normal + roughness maps, HDRI light.
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js';

const R = 1, HH = 1.15, FR = 0.16, TU = 3, NF = 24;
const ENV = new URL('pm3d-env.jpg', import.meta.url).href;

function cylinder(NA, NS) {
  const prof = [];
  for (let i = 0; i < NF; i++) { const a = -Math.PI / 2 + (Math.PI / 2) * i / NF; prof.push([R - FR + FR * Math.cos(a), -HH + FR + FR * Math.sin(a), Math.cos(a), Math.sin(a)]); }
  for (let i = 0; i <= NS; i++) prof.push([R, -HH + FR + 2 * (HH - FR) * i / NS, 1, 0]);
  for (let i = 1; i <= NF; i++) { const a = (Math.PI / 2) * i / NF; prof.push([R - FR + FR * Math.cos(a), HH - FR + FR * Math.sin(a), Math.cos(a), Math.sin(a)]); }
  const rows = prof.length, cols = NA + 1, tile = 2 * Math.PI * R / TU;
  const seg = [0]; for (let i = 1; i < rows; i++) seg.push(seg[i - 1] + Math.hypot(prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1]));
  const CR = 25, nv = rows * cols + 2 * CR * cols;
  const pos = new Float32Array(nv * 3), nrm = new Float32Array(nv * 3), uv = new Float32Array(nv * 2), dw = new Float32Array(nv), idx = [];
  let v = 0;
  const put = (x, y, z, nx, ny, nz, u, t, w) => { pos.set([x, y, z], v * 3); nrm.set([nx, ny, nz], v * 3); uv.set([u, t], v * 2); dw[v] = w; v++; };
  for (let i = 0; i < rows; i++) {
    const [r, y, nr, ny] = prof[i];
    let w = 1; if (i < NF || i >= rows - NF) { const k = Math.min(1, 2 * (i < NF ? i : rows - 1 - i) / NF); w = k * k * (3 - 2 * k); }
    for (let j = 0; j < cols; j++) {
      const th = 2 * Math.PI * j / NA, s = Math.sin(th), c = Math.cos(th);
      put(r * s, y, r * c, nr * s, ny, nr * c, th / (2 * Math.PI) * TU, (seg[i] - seg[NF]) / tile, w);
    }
  }
  for (let i = 0; i < rows - 1; i++) for (let j = 0; j < NA; j++) {
    const a = i * cols + j, b = a + 1, c = a + cols + 1, d = a + cols; idx.push(a, b, c, a, c, d);
  }
  for (const [y, ns] of [[HH, 1], [-HH, -1]]) {
    const base = v;
    for (let i = 0; i < CR; i++) {
      const r = Math.max(1e-4, (R - FR) * i / (CR - 1));
      for (let j = 0; j < cols; j++) {
        const th = 2 * Math.PI * j / NA, x = r * Math.sin(th), z = r * Math.cos(th);
        put(x, y, z, 0, ns, 0, x / tile, z * -ns / tile, 0);
      }
    }
    for (let i = 0; i < CR - 1; i++) for (let j = 0; j < NA; j++) {
      const a = base + i * cols + j, b = a + 1, c = a + cols + 1, d = a + cols;
      if (ns > 0) idx.push(a, c, b, a, d, c); else idx.push(a, b, c, a, c, d);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.BufferAttribute(nrm, 3));
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  g.setAttribute('dw', new THREE.BufferAttribute(dw, 1));
  g.setIndex(nv > 65535 ? new THREE.Uint32BufferAttribute(idx, 1) : new THREE.Uint16BufferAttribute(idx, 1));
  g.computeBoundingSphere(); g.boundingSphere.radius += 0.2;
  return g;
}

export function create(host) {
  const small = Math.min(screen.width, screen.height) < 700;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.2;
  const canvas = renderer.domElement; canvas.className = 'pm-gl';
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(27, 4 / 3, 0.1, 50);
  const pmrem = new THREE.PMREMGenerator(renderer);
  new THREE.TextureLoader().load(ENV, (t) => {
    t.mapping = THREE.EquirectangularReflectionMapping; t.colorSpace = THREE.SRGBColorSpace;
    scene.environment = pmrem.fromEquirectangular(t).texture; t.dispose(); dirty = true;
  });
  scene.environmentRotation = new THREE.Euler(0, THREE.MathUtils.degToRad(140), 0);
  scene.environmentIntensity = 1.25;
  const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(0.76, 0.375, 0.53); scene.add(key);

  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, metalness: 0 });
  mat.onBeforeCompile = (sh) => {
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nattribute float dw;')
      .replace('#include <displacementmap_vertex>',
        '#ifdef USE_DISPLACEMENTMAP\ntransformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias ) * dw;\n#endif');
  };
  const spin = new THREE.Group(); spin.rotation.y = THREE.MathUtils.degToRad(-18); scene.add(spin);
  spin.add(new THREE.Mesh(cylinder(small ? 448 : 704, small ? 240 : 380), mat));

  let el = 14, auto = true, dirty = true, live = false, raf = 0, last = 0;
  const loader = new THREE.TextureLoader(), cache = new Map(), meta = new Map();
  const aniso = renderer.capabilities.getMaxAnisotropy();
  function tex(url, srgb) {
    let p = cache.get(url);
    if (!p) {
      p = loader.loadAsync(url).then((t) => {
        t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = Math.min(8, aniso);
        if (srgb) t.colorSpace = THREE.SRGBColorSpace;
        return t;
      }).catch((e) => { cache.delete(url); throw e; });
      cache.set(url, p);
    }
    return p;
  }
  function info(src) {
    let p = meta.get(src);
    if (!p) { p = fetch(src + 't/t.json').then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); }).catch((e) => { meta.delete(src); throw e; }); meta.set(src, p); }
    return p;
  }
  let want = '';
  async function show(src, i) {
    const tag = src + '#' + i; want = tag;
    const m = await info(src);
    const [b, n, h] = await Promise.all([tex(src + 't/b' + m.b[i] + '.webp', true), tex(src + 't/n' + m.n[i] + '.webp'), tex(src + 't/h' + m.h[i] + '.webp')]);
    if (want !== tag) return false;
    const first = !mat.map;
    mat.map = b; mat.normalMap = n; mat.roughnessMap = h; mat.displacementMap = h;
    mat.displacementScale = m.amp; mat.displacementBias = m.bias;
    if (first) mat.needsUpdate = true;
    dirty = true;
    return true;
  }
  function preload(src) {
    info(src).then((m) => {
      const s = (k, srgb) => [...new Set(m[k])].forEach((j) => tex(src + 't/' + k + j + '.webp', srgb));
      s('b', true); s('n'); s('h');
    });
  }

  function size() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    if (canvas.width !== Math.round(w * renderer.getPixelRatio()) || canvas.height !== Math.round(h * renderer.getPixelRatio())) {
      renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); dirty = true;
    }
  }
  function frame(t) {
    raf = live ? requestAnimationFrame(frame) : 0;
    const dt = Math.min(0.05, (t - (last || t)) / 1000); last = t;
    if (auto) { spin.rotation.y += dt * 0.35; dirty = true; }
    size();
    if (!dirty) return;
    const d = 7.1, e = THREE.MathUtils.degToRad(el);
    camera.position.set(0, d * Math.sin(e) + 0.15, d * Math.cos(e)); camera.lookAt(0, 0.15, 0);
    renderer.render(scene, camera); dirty = false;
  }

  // drag to turn (touch: sideways only, so the page still scrolls)
  let px = null, py = 0, mouse = false;
  canvas.addEventListener('pointerdown', (e) => { px = e.clientX; py = e.clientY; mouse = e.pointerType === 'mouse'; auto = false; host.classList.add('pm-turned'); if (mouse) canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', (e) => {
    if (px === null) return;
    spin.rotation.y += (e.clientX - px) * 0.01;
    if (mouse) el = Math.max(-5, Math.min(45, el + (e.clientY - py) * 0.25));
    px = e.clientX; py = e.clientY; dirty = true;
  });
  const up = () => { px = null; };
  canvas.addEventListener('pointerup', up); canvas.addEventListener('pointercancel', up);

  return {
    canvas, show, preload,
    start() { if (!live) { live = true; last = 0; dirty = true; raf = requestAnimationFrame(frame); } },
    stop() { live = false; if (raf) cancelAnimationFrame(raf); raf = 0; },
  };
}
