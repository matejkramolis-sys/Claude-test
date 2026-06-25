// ============================================================
//  Interactivity — no dependencies. Degrades gracefully.
// ============================================================
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer  = window.matchMedia('(pointer: fine)').matches;

// ---------- footer year ----------
document.getElementById('year').textContent = new Date().getFullYear();

// ---------- scroll progress bar ----------
const progress = document.getElementById('progress');
function updateProgress() {
  const h = document.documentElement;
  const max = h.scrollHeight - h.clientHeight;
  progress.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
}
addEventListener('scroll', updateProgress, { passive: true });
updateProgress();

// ---------- reveal on scroll ----------
const revealEls = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !reduceMotion) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add('in'));
}

// ---------- cursor spotlight + aurora follow ----------
if (finePointer && !reduceMotion) {
  document.body.classList.add('has-pointer');
  const spot = document.getElementById('spotlight');
  let tx = 0, ty = 0, cx = 0, cy = 0;
  addEventListener('pointermove', (e) => {
    tx = e.clientX; ty = e.clientY;
    document.documentElement.style.setProperty('--mx', (e.clientX / innerWidth * 100) + '%');
    document.documentElement.style.setProperty('--my', (e.clientY / innerHeight * 100) + '%');
  }, { passive: true });
  (function loop() {
    cx += (tx - cx) * 0.15; cy += (ty - cy) * 0.15;
    spot.style.transform = `translate(${cx}px, ${cy}px)`;
    requestAnimationFrame(loop);
  })();
}

// ---------- 3D tilt on video cards ----------
if (finePointer && !reduceMotion) {
  document.querySelectorAll('.video-card').forEach((card) => {
    const thumb = card.querySelector('.thumb');
    card.addEventListener('pointermove', (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      thumb.style.transform = `rotateY(${px * 12}deg) rotateX(${-py * 12}deg) translateZ(0)`;
    });
    card.addEventListener('pointerleave', () => { thumb.style.transform = ''; });
  });
}

// ---------- camera-top menu actions ----------
const menu = document.getElementById('menu');
const menuClose = document.getElementById('menu-close');

function openMenu()  { menu.hidden = false; document.body.style.overflow = 'hidden'; }
function closeMenu() { menu.hidden = true;  document.body.style.overflow = ''; }

const smooth = reduceMotion ? 'auto' : 'smooth';
document.querySelectorAll('[data-action]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const action = btn.getAttribute('data-action');
    if (action === 'menu')   openMenu();
    if (action === 'top')    window.scrollTo({ top: 0, behavior: smooth });
    if (action === 'bottom') window.scrollTo({ top: document.documentElement.scrollHeight, behavior: smooth });
  });
});
menuClose.addEventListener('click', closeMenu);
menu.addEventListener('click', (e) => { if (e.target === menu) closeMenu(); });
menu.querySelectorAll('[data-jump]').forEach((a) => a.addEventListener('click', closeMenu));

// ---------- power switch: the real nub rotates ON<->OFF with scroll ----------
const pwDial = document.getElementById('pwDial');
if (pwDial) {
  const ON_DEG = 124, OFF_DEG = 86;   // nub points at ON (page top) .. OFF (page bottom)
  const sync = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    const p = max > 0 ? Math.min(1, Math.max(0, h.scrollTop / max)) : 0; // 0 top(ON) .. 1 bottom(OFF)
    pwDial.style.transform = 'rotate(' + (ON_DEG + p * (OFF_DEG - ON_DEG)) + 'deg)';
  };
  addEventListener('scroll', sync, { passive: true });
  sync();
}

// ---------- C1 = record toggle (red LED ring on/off) ----------
document.querySelectorAll('[data-c1]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const on = btn.classList.toggle('rec');
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
});

// ---------- dials: smooth continuous spin while hovered/held (reliable, centered) ----------
if (!reduceMotion) {
  document.querySelectorAll('[data-dial]').forEach((dial) => {
    let angle = 0, spinning = false, lastT = null;
    const SPEED = 150; // degrees per second
    function step(t) {
      if (!spinning) { lastT = null; return; }
      if (lastT === null) lastT = t;
      angle += (t - lastT) / 1000 * SPEED; lastT = t;
      dial.style.transform = 'rotate(' + angle + 'deg)';
      requestAnimationFrame(step);
    }
    const start = () => { if (!spinning) { spinning = true; requestAnimationFrame(step); } };
    const stop  = () => { spinning = false; };   // holds its position
    dial.addEventListener('pointerenter', start);
    dial.addEventListener('pointerleave', stop);
    dial.addEventListener('pointerdown', start);  // touch
    dial.addEventListener('pointerup', stop);
  });
}

// ---------- on-site video player ----------
const overlay = document.getElementById('player');
const video = document.getElementById('player-video');
const playerClose = document.getElementById('player-close');

function openPlayer(src) {
  video.src = src;
  overlay.hidden = false;
  document.body.style.overflow = 'hidden';
  const p = video.play();
  if (p && typeof p.catch === 'function') p.catch(() => {});
}
function closePlayer() {
  video.pause(); video.removeAttribute('src'); video.load();
  overlay.hidden = true; document.body.style.overflow = '';
}
document.querySelectorAll('.video-card').forEach((card) => {
  card.addEventListener('click', () => {
    const src = card.getAttribute('data-src');
    if (src) openPlayer(src);
  });
});
playerClose.addEventListener('click', closePlayer);
overlay.addEventListener('click', (e) => { if (e.target === overlay) closePlayer(); });

// ---------- escape closes whatever is open ----------
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  if (!overlay.hidden) closePlayer();
  else if (!menu.hidden) closeMenu();
});
