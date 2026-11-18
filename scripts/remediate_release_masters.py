#!/usr/bin/env python3
"""Remediate INF-HIM-01 release masters: burn in the CAC AI-disclosure label and
normalise loudness to the roadmap target (-14 LUFS).

Why this exists
---------------
`scripts/media_release_gate.py` Gate F became decidable once `tesseract-ocr-chi-sim`
was installed, and it then reported a real compliance failure: none of the four
pilot masters carried the visible AI-disclosure label that China's CAC rules
(effective 2025-09-01) and YouTube/Meta/LinkedIn/TikTok policies require. Gate E
also flagged `student-leo-9x16.mp4` at -21.9 LUFS, outside the -14 +/- 6 window.

Both fixes are explicitly assigned by PROJECT-INFLUENCER.md (PR #419) line 473:
"burn in the updated bilingual captions + ZYKai.net end-card CTA + 2025 CAC
AI-content disclosure label" and the mandatory spec at line 233 (-14 LUFS).

The label is drawn inside the 9:16 safe zone (outside the top/bottom 250px that
platform UI occupies) at the vertical band left blank by the existing kicker and
subtitle blocks.

This script never publishes. It writes remediated masters to a staging directory
so the gate can verify them; publishing is a separate, explicitly approved step.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "public-site" / "assets" / "media"

# Must stay in sync with AI_DISCLOSURE_PATTERNS in media_release_gate.py.
DISCLOSURE_LABEL = "AI生成合成内容 · AI-Assisted Visuals & Voice · ZYKai.net"
FONT = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
TARGET_LUFS = -14.0
TARGET_TP = -1.5
TARGET_LRA = 11.0

DEFAULT_ASSETS = (
    "pilot-ep1-9x16.mp4",
    "student-leo-9x16.mp4",
    "student-chloe-9x16.mp4",
    "student-pd-drama-ep1-9x16.mp4",
)


def run(cmd: list[str], text: bool = True):
    return subprocess.run(cmd, capture_output=True, text=text)


def measure_loudness(path: Path) -> dict:
    r = run(["ffmpeg", "-v", "info", "-i", str(path),
             "-af", f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}"
                    ":print_format=json",
             "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        raise RuntimeError(f"loudnorm measurement failed for {path}")
    return json.loads(m.group(0))


def remediate(src: Path, dst: Path) -> dict:
    """Burn the disclosure label, then loudness-normalise. Two-pass loudnorm."""
    meas = measure_loudness(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    # Disclosure band: y=258 sits just below the kicker block and outside the
    # platform-UI exclusion zone (top 250px).
    dt = (
        f"drawtext=fontfile={FONT}"
        f":text='{DISCLOSURE_LABEL}'"
        ":fontcolor=white:fontsize=30"
        ":x=(w-text_w)/2:y=258"
        ":box=1:boxcolor=black@0.55:boxborderw=10"
    )
    ln = (
        f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}"
        f":measured_I={meas['input_i']}"
        f":measured_TP={meas['input_tp']}"
        f":measured_LRA={meas['input_lra']}"
        f":measured_thresh={meas['input_thresh']}"
        f":offset={meas['target_offset']}:linear=true"
    )
    r = run([
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-vf", dt, "-af", ln,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30",
        # loudnorm internally resamples to 192k and would otherwise emit 96 kHz
        # AAC. Platforms expect 48 kHz; pin it so the master is delivery-clean.
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(dst),
    ])
    if r.returncode != 0:
        raise RuntimeError(f"remediate failed for {src}: {r.stderr[:300]}")
    return {"asset": src.name, "input_lufs": float(meas["input_i"])}


def check_output(path: Path) -> dict:
    r = run(["ffmpeg", "-v", "info", "-i", str(path),
             "-af", "ebur128=peak=true", "-f", "null", "-"])
    lufs = peak = None
    for line in r.stderr.splitlines():
        m = re.search(r"I:\s*(-?\d+\.\d+)\s*LUFS", line)
        if m:
            lufs = float(m.group(1))
        m = re.search(r"Peak:\s*(-?\d+\.\d+)\s*dBFS", line)
        if m:
            peak = float(m.group(1))
    return {"lufs": lufs, "peak": peak}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", nargs="*", default=None)
    ap.add_argument("--out", default="/tmp/zyk-remediated",
                    help="staging directory (never the served media dir)")
    ap.add_argument("--src-dir", default=None,
                    help="read masters from here instead of the served media dir "
                         "(e.g. a fresh render staging dir)")
    args = ap.parse_args()

    assets = args.assets or list(DEFAULT_ASSETS)
    src_dir = Path(args.src_dir) if args.src_dir else MEDIA
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for a in assets:
        src = src_dir / a
        if not src.is_file():
            print(f"SKIP  {a}: not on disk")
            continue
        if src.resolve() in {out.resolve() / a}:
            print(f"SKIP  {a}: source and destination are the same file")
            continue
        dst = out / a
        info = remediate(src, dst)
        after = check_output(dst)
        ok = after["lufs"] is not None and abs(after["lufs"] - TARGET_LUFS) <= 1.0
        results.append({**info, "output_lufs": after["lufs"],
                        "output_peak": after["peak"], "in_tolerance": ok})
        print(f"{'OK  ' if ok else 'WARN'} {a}: "
              f"{info['input_lufs']} -> {after['lufs']} LUFS, peak {after['peak']} dBFS")
    print(json.dumps({"staged": str(out), "results": results}, indent=2))
    return 0 if all(r["in_tolerance"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
