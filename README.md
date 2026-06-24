# My Portfolio Website

A dark, cinematic, interactive portfolio for video editing & videography.
Two rows of **videos that play right on the page** — no redirects to YouTube
or anywhere else. Share one link, people click, they watch your work.

## What's interactive

- **Scroll animations** — the title rises, the marquee drifts, and every
  video tile slides in from the side as you scroll.
- **3D tilt** — video tiles lean toward your mouse like you're turning a lens.
- **Spotlight cursor** — a soft glow follows the pointer, and the background
  gradient shifts with it.
- **Camera-top menu** (bottom of the screen) — a metal "camera plate" with a
  mode **dial** (opens the menu), a **shutter** button (jumps to the top), an
  **Instagram** control, and a "BUILT WITH CLAUDE" engraving.

## Files

| File | What it is |
|------|------------|
| `index.html` | The page — your name, the two video rows, menu, and contact. |
| `styles.css` | The look and all the animations. |
| `script.js`  | Scroll reveals, 3D tilt, the menu, and the on-page player. |
| `videos/`    | Put your video files here (see `videos/README.md`). |

## Make it yours

Open `index.html` and replace the placeholders (all clearly marked):
- "Your Name" (appears in the title, page title, and copyright).
- The contact email (`you@example.com`) and Instagram link (`yourhandle`).
- Add your videos — just name the files as listed in `videos/README.md`.
- **Captions** under each video can be changed anytime — edit the
  `<figcaption>` text. You don't need final videos to launch; it's a ready
  template you fill in as you go.

You can preview it locally by just double-clicking `index.html` to open it in
your browser.

## Publish it (get your shareable link) — free, with GitHub Pages

1. Go to this repository on GitHub → **Settings** → **Pages**.
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. Pick the branch `claude/portfolio-website-videos-fqcuek` (or `main` after
   you merge), folder `/ (root)`, then **Save**.
4. Wait ~1 minute. GitHub shows your live link at the top of that page —
   something like `https://<your-username>.github.io/<repo>/`.

That link is the one you paste and share with anyone. 🎉

> Want a custom domain like `yourname.com`? That's easy to add later — just ask.
