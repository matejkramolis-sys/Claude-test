# Your videos go here

Drop your video files in this folder, then point the site at them.

## Steps

1. **Add your video file here**, for example: `videos/my-clip.mp4`
   - Use `.mp4` (H.264) — it plays everywhere (phones, laptops, all browsers).
   - (Optional) add a thumbnail image too, e.g. `videos/my-clip.jpg`.

2. **Open `index.html`** and find the "Videos" section. Copy one of the
   `video-card` blocks and update three things:
   - `data-src="videos/my-clip.mp4"`  — path to your video
   - the `<img src="videos/my-clip.jpg">` — path to your thumbnail
   - the title and description text

That's it. When someone clicks the video on your site, it plays right there
in a popup — no redirect to YouTube or anywhere else.

## Tips

- **Keep files reasonably small.** Big videos load slowly. Aim for under
  ~50 MB per clip if you can. Free tools like HandBrake can shrink them.
- **No thumbnail?** No problem — the card shows a clean placeholder and a
  play button automatically.
- **Lots of large videos / want it to feel instant?** Tell me and I'll set
  you up to stream them from a free video host while still playing on-site.
