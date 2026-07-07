#!/usr/bin/env python3
"""
analyze_video.py — pull the raw material the reel-cover skill needs to
understand a video, using a self-contained static ffmpeg (imageio-ffmpeg),
so it works in locked-down containers with no system ffmpeg.

It produces:
  * evenly-spaced keyframes (the skill Reads these to see the topic + your look)
  * the audio track as 16 kHz mono wav (for optional transcription)
  * an optional transcript, if faster-whisper is installed and its model is
    reachable (best-effort; the skill falls back to frames + your one-line topic)

Usage:
    python3 analyze_video.py --video reel.mp4 --out ./work --frames 9 [--transcribe]

Prints a small report the skill reads to plan the cover.
"""
import argparse
import json
import os
import subprocess
import sys


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        # fall back to a system ffmpeg if the pip static binary isn't present
        return "ffmpeg"


def probe_duration(exe, video):
    """Duration in seconds via ffmpeg stderr (avoids needing ffprobe)."""
    r = subprocess.run([exe, "-i", video], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "Duration:" in line:
            hms = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = hms.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def extract_frames(exe, video, out_dir, n, duration):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    # sample from 5% to 95% of the clip so we skip fades in/out
    if duration <= 0:
        duration = 30.0
    for i in range(n):
        t = duration * (0.05 + 0.9 * (i / max(1, n - 1)))
        p = os.path.join(out_dir, f"frame_{i:02d}.jpg")
        subprocess.run(
            [exe, "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
             "-vf", "scale=640:-1", "-q:v", "3", p],
            capture_output=True)
        if os.path.exists(p):
            paths.append(p)
    return paths


def extract_audio(exe, video, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, "audio.wav")
    r = subprocess.run(
        [exe, "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav],
        capture_output=True, text=True)
    return wav if os.path.exists(wav) else None


def transcribe(wav):
    """Best-effort transcription with faster-whisper (tiny model). Returns text
    or None if the package/model isn't available."""
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return None
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(wav)
        return " ".join(s.text.strip() for s in segments).strip()
    except Exception as e:
        sys.stderr.write(f"[analyze_video] transcription failed: {e}\n")
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--out", default="./work")
    p.add_argument("--frames", type=int, default=9)
    p.add_argument("--transcribe", action="store_true")
    a = p.parse_args()

    if not os.path.exists(a.video):
        sys.exit(f"video not found: {a.video}")

    exe = ffmpeg_exe()
    dur = probe_duration(exe, a.video)
    frames = extract_frames(exe, a.video, os.path.join(a.out, "frames"),
                            a.frames, dur)
    wav = extract_audio(exe, a.video, a.out)
    transcript = None
    if a.transcribe and wav:
        transcript = transcribe(wav)

    report = {
        "duration_sec": round(dur, 2),
        "frames": frames,
        "audio": wav,
        "transcript": transcript,
        "note": ("Read the frames to understand the topic + the creator's look. "
                 "If transcript is null, ask the user for a one-line topic."),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
