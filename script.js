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

// ---------- swap to the exact-photo menu when assets/camera-top.png exists ----------
(function () {
  const wrap = document.getElementById('camPhotoWrap');
  const plate = document.getElementById('camPlate');
  const img = wrap && wrap.querySelector('.camera-photo');
  if (!wrap || !plate || !img) return;
  const showPhoto = () => { wrap.hidden = false; plate.hidden = true; };
  const showPlate = () => { wrap.remove(); plate.hidden = false; };
  if (img.complete) { (img.naturalWidth > 0 ? showPhoto : showPlate)(); }
  img.addEventListener('load', showPhoto);
  img.addEventListener('error', showPlate);
})();

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

// ---------- power switch = scroll position (ON at top, OFF at bottom) ----------
const switchDot = document.getElementById('switchDot');
if (switchDot) {
  const ON_TOP = 17.5, OFF_TOP = 10; // % positions of the dot (ON lower, OFF higher)
  const sync = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    const p = max > 0 ? Math.min(1, Math.max(0, h.scrollTop / max)) : 0; // 0 top .. 1 bottom
    switchDot.style.top = (ON_TOP - p * (ON_TOP - OFF_TOP)) + '%';
    // green (ON) -> red (OFF)
    const r = Math.round(43 + p * (255 - 43)), g = Math.round(212 - p * (153)), b = Math.round(107 - p * 59);
    switchDot.style.background = 'radial-gradient(circle at 35% 30%, #fff, rgb(' + r + ',' + g + ',' + b + '))';
    switchDot.style.boxShadow = '0 0 9px rgba(' + r + ',' + g + ',' + b + ',0.85)';
  };
  addEventListener('scroll', sync, { passive: true });
  sync();
}

// ---------- C1 press feedback ----------
document.querySelectorAll('[data-c1]').forEach((btn) => {
  btn.addEventListener('click', () => {
    btn.classList.remove('press');
    void btn.offsetWidth;        // restart animation
    btn.classList.add('press');
    setTimeout(() => btn.classList.remove('press'), 560);
  });
});

// ---------- dials rotate as you slide across them ----------
if (!reduceMotion) {
  document.querySelectorAll('.cam-dialimg').forEach((dial) => {
    dial.addEventListener('pointermove', (e) => {
      const r = dial.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;   // -0.5 .. 0.5
      dial.style.transition = 'transform 0.08s linear';
      dial.style.transform = 'rotate(' + (x * 60) + 'deg)';
    });
    dial.addEventListener('pointerleave', () => {
      dial.style.transition = 'transform 0.6s cubic-bezier(0.16,1,0.3,1)';
      dial.style.transform = 'rotate(0deg)';
    });
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
