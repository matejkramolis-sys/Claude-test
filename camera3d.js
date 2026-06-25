// ============================================================
//  3D camera menu (Three.js). Real geometry, metal, lighting.
//  Controls: hover dials -> spin; click C1 -> record LED;
//  scroll -> power nub ON(top)..OFF(bottom); MENU / INSTAGRAM.
// ============================================================
(function () {
  const mount = document.getElementById('cam3d');
  if (!mount || !window.THREE) return;
  const T = window.THREE;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const IG = 'https://www.instagram.com/t.castvaj';

  const renderer = new T.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputEncoding = T.sRGBEncoding;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.92;
  mount.appendChild(renderer.domElement);

  const scene = new T.Scene();
  const camera = new T.PerspectiveCamera(26, 2.6, 0.1, 100);
  camera.position.set(0, 6.0, 3.9);
  camera.lookAt(0, -0.35, 0);

  // ---- studio environment for metal reflections ----
  function envTexture() {
    const c = document.createElement('canvas'); c.width = 512; c.height = 256;
    const x = c.getContext('2d');
    x.fillStyle = '#050506'; x.fillRect(0, 0, 512, 256);
    const sky = x.createLinearGradient(0, 0, 0, 80);
    sky.addColorStop(0, '#14161b'); sky.addColorStop(1, '#050506');
    x.fillStyle = sky; x.fillRect(0, 0, 512, 80);
    // tight soft highlight streak
    const r = x.createRadialGradient(256, 24, 5, 256, 36, 130);
    r.addColorStop(0, 'rgba(255,255,255,0.75)'); r.addColorStop(0.4, 'rgba(210,220,245,0.14)'); r.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = r; x.fillRect(0, 0, 512, 95);
    const t = new T.CanvasTexture(c); t.mapping = T.EquirectangularReflectionMapping; return t;
  }
  const pmrem = new T.PMREMGenerator(renderer);
  scene.environment = pmrem.fromEquirectangular(envTexture()).texture;

  // ---- lights ----
  const key = new T.DirectionalLight(0xffffff, 0.6); key.position.set(4, 9, 5); scene.add(key);
  const fill = new T.DirectionalLight(0xc7d6ff, 0.25); fill.position.set(-6, 3, 3); scene.add(fill);
  const rim = new T.DirectionalLight(0xffffff, 1.0); rim.position.set(-3, 5, -6); scene.add(rim);
  scene.add(new T.AmbientLight(0xffffff, 0.12));

  // ---- materials ----
  const bodyMat = new T.MeshStandardMaterial({ color: 0x0a0b0d, metalness: 0.35, roughness: 0.58 });
  const darkMat = new T.MeshStandardMaterial({ color: 0x0b0b0d, metalness: 0.4, roughness: 0.6 });
  const plasticMat = new T.MeshStandardMaterial({ color: 0x202228, metalness: 0.25, roughness: 0.68 });
  const dialTop = new T.MeshStandardMaterial({ color: 0x191a1f, metalness: 0.34, roughness: 0.56 });
  const metal = () => new T.MeshStandardMaterial({ color: 0x1b1c21, metalness: 0.45, roughness: 0.5 });

  // knurl bump for dial sides
  function knurlTex() {
    const c = document.createElement('canvas'); c.width = 256; c.height = 8;
    const x = c.getContext('2d');
    for (let i = 0; i < 256; i++) { const v = i % 4 < 2 ? 235 : 55; x.fillStyle = 'rgb(' + v + ',' + v + ',' + v + ')'; x.fillRect(i, 0, 1, 8); }
    const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; return t;
  }

  const cam = new T.Group(); scene.add(cam);

  function roundedRect(w, h, r) {
    const s = new T.Shape();
    s.absarc(-w / 2 + r, -h / 2 + r, r, Math.PI, 1.5 * Math.PI);
    s.absarc(w / 2 - r, -h / 2 + r, r, 1.5 * Math.PI, 2 * Math.PI);
    s.absarc(w / 2 - r, h / 2 - r, r, 0, 0.5 * Math.PI);
    s.absarc(-w / 2 + r, h / 2 - r, r, 0.5 * Math.PI, Math.PI);
    return s;
  }
  function slab(w, h, r, depth, mat, bevel) {
    bevel = bevel || 0.12;
    const geo = new T.ExtrudeGeometry(roundedRect(w, h, r),
      { depth: depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 4, curveSegments: 24 });
    geo.center();
    const m = new T.Mesh(geo, mat); m.rotation.x = -Math.PI / 2;
    return m;
  }

  // ---- body ----
  const BW = 6.6, BD = 2.5, BH = 1.0, bevel = 0.12;
  const body = slab(BW, BD, 0.42, BH, bodyMat, bevel); cam.add(body);
  const TOP = BH / 2 + bevel;             // top surface Y

  // ---- flash hump (left) + hot shoe ----
  const hump = slab(1.5, 1.5, 0.28, 0.55, bodyMat, 0.12);
  hump.position.set(-BW / 2 + 1.15, TOP - 0.18, -0.1); cam.add(hump);
  const shoe = new T.Mesh(new T.BoxGeometry(0.7, 0.16, 0.5), darkMat);
  shoe.position.set(-BW / 2 + 1.15, TOP + 0.42, -0.1); cam.add(shoe);

  // ---- dials ----
  const dials = [];
  function dial(radius, height, x, z) {
    const g = new T.Group();
    const side = metal(); const k = knurlTex(); k.repeat.set(Math.round(radius * 52), 1);
    side.bumpMap = k; side.bumpScale = 0.02;
    const cyl = new T.Mesh(new T.CylinderGeometry(radius, radius, height, 72, 1, false), [side, dialTop, darkMat]);
    g.add(cyl);
    const notch = new T.Mesh(new T.BoxGeometry(0.07, 0.02, radius * 0.62),
      new T.MeshStandardMaterial({ color: 0xf2f2f4, metalness: 0.1, roughness: 0.5 }));
    notch.position.set(0, height / 2 + 0.011, radius * 0.34); g.add(notch);
    g.position.set(x, TOP + height / 2 - 0.04, z);
    cam.add(g); dials.push(g); return g;
  }
  const modeDial = dial(0.72, 0.5, -0.1, -0.05);
  const expoDial = dial(0.52, 0.42, 1.25, -0.05);

  // ---- C1 + record LED ----
  const c1 = new T.Group();
  const c1btn = new T.Mesh(new T.CylinderGeometry(0.27, 0.27, 0.18, 40), plasticMat);
  c1btn.position.y = 0.09; c1.add(c1btn);
  const ledMat = new T.MeshStandardMaterial({ color: 0x320d0a, emissive: 0xff2d22, emissiveIntensity: 0, roughness: 0.5 });
  const led = new T.Mesh(new T.TorusGeometry(0.36, 0.07, 20, 60), ledMat);
  led.rotation.x = Math.PI / 2; led.position.y = 0.06; c1.add(led);
  c1.position.set(2.35, TOP, 0.05); cam.add(c1);
  let recording = false;

  // ---- power switch (button + nub) ----
  const power = new T.Group();
  const pbtn = new T.Mesh(new T.CylinderGeometry(0.4, 0.43, 0.24, 48), metal());
  pbtn.position.y = 0.12; power.add(pbtn);
  const nub = new T.Mesh(new T.BoxGeometry(0.13, 0.12, 0.36),
    new T.MeshStandardMaterial({ color: 0x0d0d0f, metalness: 0.3, roughness: 0.6 }));
  nub.position.set(0, 0.23, 0.27); power.add(nub);
  power.position.set(2.55, TOP, -0.95); cam.add(power);

  // ---- MENU / INSTAGRAM (flat labels on the top face) ----
  function rr(x, a, b, w, h, r) { x.beginPath(); x.moveTo(a + r, b); x.arcTo(a + w, b, a + w, b + h, r); x.arcTo(a + w, b + h, a, b + h, r); x.arcTo(a, b + h, a, b, r); x.arcTo(a, b, a + w, b, r); x.closePath(); }
  function label(kind, w) {
    const cw = 820, ch = 220;
    const c = document.createElement('canvas'); c.width = cw; c.height = ch; const x = c.getContext('2d');
    const g = x.createLinearGradient(0, 0, 0, ch); g.addColorStop(0, '#26272d'); g.addColorStop(1, '#101115');
    x.fillStyle = g; rr(x, 6, 6, cw - 12, ch - 12, 44); x.fill();
    x.lineWidth = 4; x.strokeStyle = '#45464e'; x.stroke();
    const cy = ch / 2;
    x.fillStyle = '#f2f2f4'; x.strokeStyle = '#f2f2f4';
    if (kind === 'menu') {
      x.lineWidth = 14; x.lineCap = 'round';
      for (let i = 0; i < 3; i++) { const yy = cy - 30 + i * 30; x.beginPath(); x.moveTo(70, yy); x.lineTo(178, yy); x.stroke(); }
      x.font = '700 104px ui-sans-serif, system-ui, Arial'; x.textBaseline = 'middle'; x.fillText('MENU', 220, cy + 4);
    } else {
      x.lineWidth = 11; rr(x, 64, cy - 48, 96, 96, 26); x.stroke();        // IG rounded square
      x.beginPath(); x.arc(112, cy, 30, 0, Math.PI * 2); x.stroke();        // lens
      x.beginPath(); x.arc(142, cy - 30, 6, 0, Math.PI * 2); x.fill();      // dot
      x.font = '700 92px ui-sans-serif, system-ui, Arial'; x.textBaseline = 'middle'; x.fillText('INSTAGRAM', 196, cy + 4);
    }
    const t = new T.CanvasTexture(c); t.anisotropy = 8;
    const mesh = new T.Mesh(new T.PlaneGeometry(w, w * ch / cw),
      new T.MeshBasicMaterial({ map: t, transparent: true }));
    mesh.rotation.x = -Math.PI / 2; mesh.position.y = TOP + 0.03;
    cam.add(mesh); return mesh;
  }
  const menuBtn = label('menu', 1.85); menuBtn.position.set(0.35, TOP + 0.03, 0.92);
  const igBtn = label('ig', 2.25); igBtn.position.set(2.55, TOP + 0.03, 0.92);

  // ============ interaction ============
  const ray = new T.Raycaster();
  const ptr = new T.Vector2();
  let hoverDials = new Set();
  const px = { x: 0, y: 0 };

  function pickAt(clientX, clientY) {
    const r = renderer.domElement.getBoundingClientRect();
    ptr.x = ((clientX - r.left) / r.width) * 2 - 1;
    ptr.y = -((clientY - r.top) / r.height) * 2 + 1;
    ray.setFromCamera(ptr, camera);
    return ray;
  }
  function hits(group) { return ray.intersectObject(group, true).length > 0; }

  renderer.domElement.addEventListener('pointermove', (e) => {
    px.x = (e.clientX / innerWidth) * 2 - 1; px.y = (e.clientY / innerHeight) * 2 - 1;
    pickAt(e.clientX, e.clientY);
    hoverDials.clear();
    if (hits(modeDial)) hoverDials.add(modeDial);
    if (hits(expoDial)) hoverDials.add(expoDial);
    const over = hits(modeDial) || hits(expoDial) || hits(c1) || hits(menuBtn) || hits(igBtn);
    renderer.domElement.style.cursor = over ? 'pointer' : 'default';
  });
  renderer.domElement.addEventListener('pointerleave', () => hoverDials.clear());

  renderer.domElement.addEventListener('click', (e) => {
    pickAt(e.clientX, e.clientY);
    if (hits(menuBtn)) { window.cameraMenu && window.cameraMenu.open(); return; }
    if (hits(igBtn)) { window.open(IG, '_blank', 'noopener'); return; }
    if (hits(c1)) { recording = !recording; ledMat.emissiveIntensity = recording ? 4.0 : 0; return; }
  });

  // power nub follows scroll: ON (top) .. OFF (bottom)
  function scrollSync() {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    const p = max > 0 ? Math.min(1, Math.max(0, h.scrollTop / max)) : 0;
    power.rotation.y = THREE_lerp(0.6, -0.6, p);   // sweep the nub
  }
  function THREE_lerp(a, b, t) { return a + (b - a) * t; }
  addEventListener('scroll', scrollSync, { passive: true });

  // ---- resize ----
  function resize() {
    const w = mount.clientWidth, h = mount.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(mount);
  resize(); scrollSync();

  // ---- render loop ----
  let last = performance.now();
  function loop(t) {
    const dt = Math.min(0.05, (t - last) / 1000); last = t;
    if (!reduce) hoverDials.forEach((d) => { d.rotation.y += dt * 2.6; });
    // gentle parallax
    const tx = -px.x * 0.12, tz = px.y * 0.06;
    cam.rotation.y += (tx - cam.rotation.y) * 0.06;
    cam.rotation.x += ((-0.02 + tz) - cam.rotation.x) * 0.06;
    renderer.render(scene, camera);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
