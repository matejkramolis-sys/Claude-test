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

document.querySelectorAll('[data-action]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const action = btn.getAttribute('data-action');
    if (action === 'menu') openMenu();
    if (action === 'top')  window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
  });
});
menuClose.addEventListener('click', closeMenu);
menu.addEventListener('click', (e) => { if (e.target === menu) closeMenu(); });
menu.querySelectorAll('[data-jump]').forEach((a) => a.addEventListener('click', closeMenu));

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
