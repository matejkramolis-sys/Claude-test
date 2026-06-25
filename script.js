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
  const LEFT = 27, RIGHT = 73;   // knob left% travel (OFF .. ON)
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

// ---------- hover preview (pops out beside the thumbnail) + click to watch ----------
const peek = document.getElementById('peek');
const peekPanel = peek.querySelector('.peek-panel');
const peekVideo = document.getElementById('peekVideo');
const peekTitle = document.getElementById('peekTitle');
const peekSub = document.getElementById('peekSub');

const player = document.getElementById('player');
const playerVideo = document.getElementById('player-video');
const playerClose = document.getElementById('player-close');

function cardInfo(card) {
  const img = card.querySelector('.thumb img');
  return {
    src: card.getAttribute('data-src'),
    poster: img ? img.getAttribute('src') : '',
    title: card.querySelector('.vc-title') ? card.querySelector('.vc-title').textContent : '',
    sub: card.querySelector('.vc-sub') ? card.querySelector('.vc-sub').textContent : ''
  };
}

let peekHideTimer = null, peekCard = null;

// aspect ratio for the preview: prefer the loaded video, else the poster image,
// else fall back to 16:9. Poster matches the clip's orientation, so this is
// correct immediately (no waiting on video metadata).
function peekAspect(card) {
  if (peekVideo.videoWidth && peekVideo.videoHeight) {
    return peekVideo.videoWidth / peekVideo.videoHeight;
  }
  const img = card && card.querySelector('.thumb img');
  if (img && img.naturalWidth && img.naturalHeight) {
    return img.naturalWidth / img.naturalHeight;
  }
  return 16 / 9;
}

// size + position the panel to the video's real shape, popped out beside the card
function placePeek(card) {
  const ar = peekAspect(card);
  let W, H;
  if (ar < 1) {                                   // vertical (9:16-ish)
    H = Math.min(innerHeight * 0.66, 560);
    W = H * ar;
  } else {                                        // horizontal
    W = Math.min(innerWidth * 0.44, 600);
    H = W / ar;
    if (H > innerHeight * 0.7) { H = innerHeight * 0.7; W = H * ar; }
  }
  const r = card.getBoundingClientRect();
  const gap = 18;
  let left = r.right + gap, side = 'right';
  if (left + W > innerWidth - 12) { left = r.left - gap - W; side = 'left'; }   // flip if no room
  left = Math.max(12, Math.min(left, innerWidth - W - 12));
  let top = r.top + r.height / 2 - H / 2;
  top = Math.max(12, Math.min(top, innerHeight - H - 12));
  peek.style.left = left + 'px'; peek.style.top = top + 'px';
  peek.style.width = W + 'px'; peek.style.height = H + 'px';
  peek.classList.toggle('left', side === 'left');
}

function showPeek(card) {
  if (player && !player.hidden) return;           // not while watching full
  peekCard = card;
  const d = cardInfo(card);
  clearTimeout(peekHideTimer);
  peekTitle.textContent = d.title; peekSub.textContent = d.sub;
  if (d.poster) peekVideo.poster = d.poster;
  if (peekVideo.getAttribute('src') !== d.src) { peekVideo.src = d.src; }
  placePeek(card);                                // size with what we know now
  peek.setAttribute('aria-hidden', 'false');
  requestAnimationFrame(() => peek.classList.add('show'));
  const p = peekVideo.play(); if (p && p.catch) p.catch(() => {});
}
// once the real dimensions are known, re-fit (handles vertical clips)
peekVideo.addEventListener('loadedmetadata', () => { if (peekCard) placePeek(peekCard); });
function hidePeek() {
  peek.classList.remove('show');
  peekCard = null;
  peekHideTimer = setTimeout(() => {
    peek.setAttribute('aria-hidden', 'true');
    peekVideo.pause();
  }, 260);
}

function openPlayer(src) {
  hidePeek();
  playerVideo.src = src; player.hidden = false; document.body.style.overflow = 'hidden';
  const p = playerVideo.play(); if (p && p.catch) p.catch(() => {});
}
function closePlayer() {
  playerVideo.pause(); playerVideo.removeAttribute('src'); playerVideo.load();
  player.hidden = true; document.body.style.overflow = '';
}

document.querySelectorAll('.video-card').forEach((card) => {
  card.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'touch') showPeek(card); });
  card.addEventListener('pointerleave', hidePeek);
  card.addEventListener('click', () => openPlayer(card.getAttribute('data-src')));
});
// keep preview aligned if the page scrolls while hovering
addEventListener('scroll', () => { if (peekCard) showPeek(peekCard); }, { passive: true });

playerClose.addEventListener('click', closePlayer);
player.addEventListener('click', (e) => { if (e.target === player) closePlayer(); });

// ---------- escape closes whatever is open ----------
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  if (!player.hidden) closePlayer();
  else if (!menu.hidden) closeMenu();
});
