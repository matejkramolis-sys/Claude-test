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

// ============ camera controls (photo overlays) ============

// press-in animation for any [data-press] control
document.querySelectorAll('[data-press]').forEach((el) => {
  const press = () => el.classList.add('pressing');
  const release = () => el.classList.remove('pressing');
  el.addEventListener('pointerdown', press);
  el.addEventListener('pointerup', release);
  el.addEventListener('pointerleave', release);
  el.addEventListener('pointercancel', release);
});

// C1 = record LED toggle (black ring -> red light)
document.querySelectorAll('[data-c1]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const on = btn.classList.toggle('rec');
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
});

// ISO -> slide-out panel; higher ISO brightens the whole site
(function () {
  const panel = document.getElementById('isoPanel');
  const list = document.getElementById('isoList');
  const expo = document.getElementById('expo');
  if (!panel || !list || !expo) return;
  const stops = [100, 125, 160, 200, 250, 320, 400, 500];
  stops.forEach((iso, i) => {
    const b = document.createElement('button');
    b.className = 'iso-opt'; b.textContent = iso; b.dataset.i = i;
    b.addEventListener('click', () => setISO(i));
    list.appendChild(b);
  });
  function setISO(i) {
    const f = i / (stops.length - 1);            // 0 (ISO100) .. 1 (ISO500)
    expo.style.opacity = (f * 0.42).toFixed(3);  // brighten the site
    list.querySelectorAll('.iso-opt').forEach((o) => o.classList.toggle('active', +o.dataset.i === i));
  }
  setISO(0);
  document.querySelectorAll('[data-iso]').forEach((btn) => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); panel.classList.toggle('open'); });
  });
  document.addEventListener('click', (e) => {
    if (panel.classList.contains('open') && !panel.contains(e.target) && !e.target.closest('[data-iso]')) {
      panel.classList.remove('open');
    }
  });
})();

// OFF <-> ON slider: follows scroll (ON at top, OFF at bottom); draggable to scrub
(function () {
  const knob = document.getElementById('onoffKnob');
  const track = knob && knob.parentElement;
  if (!knob || !track) return;
  const LEFT = 18, RIGHT = 82;   // knob left% travel (OFF .. ON)
  let dragging = false;
  function fromScroll() {
    if (dragging) return;
    const h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    const p = max > 0 ? Math.min(1, Math.max(0, h.scrollTop / max)) : 0;
    knob.style.left = (RIGHT - p * (RIGHT - LEFT)) + '%';   // top -> ON (right)
  }
  function scrub(clientX) {
    const r = track.getBoundingClientRect();
    let f = (clientX - r.left) / r.width; f = Math.min(1, Math.max(0, f));  // 0 OFF .. 1 ON
    knob.style.left = (LEFT + f * (RIGHT - LEFT)) + '%';
    const h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    window.scrollTo({ top: (1 - f) * max, behavior: 'auto' });             // ON -> top
  }
  addEventListener('scroll', fromScroll, { passive: true });
  fromScroll();
  knob.addEventListener('pointerdown', (e) => { dragging = true; knob.setPointerCapture(e.pointerId); e.preventDefault(); });
  knob.addEventListener('pointermove', (e) => { if (dragging) scrub(e.clientX); });
  knob.addEventListener('pointerup', () => { dragging = false; });
  track.addEventListener('pointerdown', (e) => { if (e.target === track) scrub(e.clientX); });
})();

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
