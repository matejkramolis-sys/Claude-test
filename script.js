// ====== Current year in footer ======
document.getElementById('year').textContent = new Date().getFullYear();

// ====== On-site video player ======
// Clicking a video card opens an overlay and plays the video right here.
// Visitors never get redirected off the page.

const overlay = document.getElementById('player');
const video = document.getElementById('player-video');
const closeBtn = document.getElementById('player-close');

function openPlayer(src) {
  video.src = src;
  overlay.hidden = false;
  document.body.style.overflow = 'hidden'; // stop background scrolling
  const play = video.play();
  if (play && typeof play.catch === 'function') {
    play.catch(() => { /* autoplay blocked — visitor can press play */ });
  }
}

function closePlayer() {
  video.pause();
  video.removeAttribute('src');
  video.load();
  overlay.hidden = true;
  document.body.style.overflow = '';
}

// Wire up every video card
document.querySelectorAll('.video-card').forEach((card) => {
  card.addEventListener('click', () => {
    const src = card.getAttribute('data-src');
    if (src) openPlayer(src);
  });
});

// Close: X button, clicking the dark backdrop, or pressing Escape
closeBtn.addEventListener('click', closePlayer);
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closePlayer();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !overlay.hidden) closePlayer();
});
