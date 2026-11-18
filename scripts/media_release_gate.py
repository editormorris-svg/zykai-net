#!/usr/bin/env python3
"""Gates A-G fail-closed media release gate (ZYK media roadmap v1.1 M1 / v1.2 §4).

Implements the seven gates from
`ops/ZYK_MEDIA_PRODUCTION_ROADMAP_v1.1_2026-11-12.md` §4 for an existing set of
final masters, emitting one machine-readable RELEASE_READY / BLOCKED receipt per
asset and a combined receipt.

Gates (from the roadmap text):
  A. Harvest & provenance   - manifest size + sha256 match, atomic/complete file
  B. Technical integrity    - ffprobe stream checks + full ffmpeg decode, audio present
  C. Recycled footage       - cross-asset perceptual (dHash) duplicate detection
  D. Content & narrative    - scene/script/character/lip-sync; needs vision review
  E. Audio/subtitle/stitch  - loudness, silence, clipping, A/V duration sync
  F. Final export           - independent full decode, re-hash, aspect ratio, disclosure
  G. Distribution           - release asset exists, public playback 200 + byte match

Honesty rule: a gate that cannot be decided without human/vision review is reported
`pending`, never `pass`. `--decide` requires every gate to be pass or explicitly
waived by the operator; anything else keeps the asset BLOCKED.

Usage:
  python3 scripts/media_release_gate.py                 # gate the default master set
  python3 scripts/media_release_gate.py --assets a.mp4  # gate specific files
  python3 scripts/media_release_gate.py --json          # machine-readable receipt
  python3 scripts/media_release_gate.py --decide        # exit non-zero unless READY
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MEDIA = ROOT / "public-site" / "assets" / "media"
MANIFEST = ROOT / "media-manifest.json"
RECEIPT_DIR = ROOT / "receipts" / "media-release"
# Recorded human/vision Gate D decisions, one JSON file per asset, bound to the
# sha256 of the exact master reviewed. See gate_d() for the required shape.
REVIEW_DIR = ROOT / "receipts" / "media-review"
MEDIA_RELEASE_TAG = "media-v20261108"
MEDIA_RELEASE_BASE = (
    "https://github.com/editormorris-svg/zykai-net/releases/download/" + MEDIA_RELEASE_TAG
)

# Default gate set: the pilot masters the Project Influencer roadmap packages as
# Videos #2, #9, #10 (INF-HIM-01).
DEFAULT_ASSETS = (
    "pilot-ep1-9x16.mp4",
    "student-leo-9x16.mp4",
    "student-chloe-9x16.mp4",
    "student-pd-drama-ep1-9x16.mp4",
)

# Perceptual thresholds (ham-ming distance on 64-bit dHash of a 64x36 gray frame).
DHASH_TAIL_FRAMES = 12
CROSS_DUP_HAM = 6      # <= this across ANY sampled frame pair => probable recycled footage
LOW_INFO_STD = 10.0    # frames below this std are near-uniform (skip in dup compare)
EXPECTED_ASPECTS = {(1080, 1920), (1920, 1080)}
EXPECTED_FPS = 30.0
MAX_AV_DELTA_S = 0.35  # |video_dur - audio_dur| tolerance
LOUDNESS_TOL_DB = 6.0  # tolerance around the -14 LUFS roadmap target
# OCR is unreliable on the glyph pair "AI": tesseract frequently returns "Al"/"A1",
# and inserts spaces inside CJK runs ("AI生成合成内容" -> "Ai 生成 合成 内 容"). Matching raw
# substrings therefore false-FAILS a correctly labelled master. Normalise whitespace and
# tolerate the I/l/1 confusion, then match patterns.
AI_DISCLOSURE_PATTERNS = (
    r"a[il1]-?assisted",
    r"a[il1]-?generated",
    r"a[il1]辅助",
    r"a[il1]生成",
    r"生成合成",
    r"合成内容",
    r"人工智能生成",
)


def _run(cmd: list[str], text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=text)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe_streams(path: Path) -> dict:
    r = _run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ])
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout)


@dataclass
class GateResult:
    gate: str
    status: str          # pass | fail | pending
    detail: str
    evidence: dict = field(default_factory=dict)


@dataclass
class AssetReceipt:
    asset: str
    gates: list[GateResult] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        if any(g.status == "fail" for g in self.gates):
            return "BLOCKED"
        if any(g.status == "pending" for g in self.gates):
            return "PENDING_REVIEW"
        return "RELEASE_READY"

    def as_dict(self) -> dict:
        return {
            "asset": self.asset,
            "verdict": self.verdict,
            "gates": [{"gate": g.gate, "status": g.status, "detail": g.detail,
                       "evidence": g.evidence} for g in self.gates],
        }


def load_manifest() -> dict[str, dict]:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out = {}
    for f in m.get("files", []):
        rel = f["path"]
        out[Path(rel).name] = {"bytes": f["bytes"], "sha256": f["sha256"], "path": rel}
    return out


def gate_a(asset: str, path: Path, man: dict[str, dict]) -> GateResult:
    entry = man.get(asset)
    if not path.is_file():
        return GateResult("A", "fail", f"missing on disk: {path}")
    size = path.stat().st_size
    if not entry:
        return GateResult("A", "fail", f"no manifest provenance entry for {asset}")
    if size != entry["bytes"]:
        return GateResult("A", "fail", f"size {size} != manifest {entry['bytes']}")
    digest = sha256_of(path)
    if digest != entry["sha256"]:
        return GateResult("A", "fail", f"sha256 {digest[:16]}... != manifest {entry['sha256'][:16]}...")
    return GateResult("A", "pass", "manifest size+sha256 match", {"sha256": digest, "bytes": size})


def gate_b(path: Path) -> GateResult:
    try:
        meta = ffprobe_streams(path)
    except RuntimeError as exc:
        return GateResult("B", "fail", str(exc))
    streams = meta.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video:
        return GateResult("B", "fail", "no video stream")
    if not audio:
        return GateResult("B", "fail", "no audio stream (speech expected)")
    # Full decode: any stderr output means corruption/truncation.
    dec = _run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"])
    err = dec.stderr.strip()
    bad = bool(err) or any(t in err for t in ("Invalid NAL", "partial file", "missing picture",
                                              "corrupt", "Error opening"))
    fps = video.get("r_frame_rate", "0/1")
    try:
        n, d = fps.split("/")
        fps_val = float(n) / float(d) if float(d) else 0.0
    except (ValueError, ZeroDivisionError):
        fps_val = 0.0
    ev = {
        "codec": video.get("codec_name"), "width": video.get("width"),
        "height": video.get("height"), "fps": round(fps_val, 3),
        "duration": meta.get("format", {}).get("duration"),
        "audio_samples": audio.get("duration"),
    }
    if bad:
        return GateResult("B", "fail", f"full decode reported errors: {err[:160]}", ev)
    return GateResult("B", "pass", "ffprobe valid + full decode clean", ev)


def _dhash_bits(gray: bytes, w: int, h: int) -> int:
    # gray is w*h bytes; dHash on 9x8 downsample handled by caller scaling to (9,8)
    return 0


def sample_dhashes(path: Path, frames: int = DHASH_TAIL_FRAMES) -> list[dict]:
    """dHash of `frames` frames spread across the tail block (recycled-footage probe)."""
    W, H = 64, 36
    fb = W * H
    try:
        meta = ffprobe_streams(path)
        dur = float(meta["format"]["duration"])
    except (RuntimeError, KeyError, ValueError):
        return []
    ss = max(0.0, dur - 10.0)
    raw = _run(["ffmpeg", "-v", "error", "-ss", f"{ss:.2f}", "-i", str(path),
                "-vf", f"fps={frames}/10,scale={W}:{H}", "-frames:v", str(frames),
                "-f", "rawvideo", "-pix_fmt", "gray", "-"], text=False).stdout
    if isinstance(raw, str):
        raw = raw.encode("latin-1", "ignore")
    n = len(raw) // fb
    out = []
    for i in range(n):
        px = raw[i * fb:(i + 1) * fb]
        # dHash: 8x8 bits comparing horizontally adjacent pixels on a 9x8 grid.
        # Recompute on a 9x8 tile by cheap nearest-neighbour resample.
        grid = []
        for r in range(8):
            row = []
            for c in range(9):
                x = min(W - 1, int((c + 0.5) * W / 9))
                y = min(H - 1, int((r + 0.5) * H / 8))
                row.append(px[y * W + x])
            grid.append(row)
        bits = 0
        for r in range(8):
            for c in range(8):
                bits = (bits << 1) | (1 if grid[r][c] > grid[r][c + 1] else 0)
        mean = sum(px) / len(px)
        std = (sum((v - mean) ** 2 for v in px) / len(px)) ** 0.5
        out.append({"t": round(ss + i * 10.0 / frames, 2), "h": bits,
                    "std": round(std, 1)})
    return out


def gate_c(asset: str, all_hashes: dict[str, list[dict]]) -> GateResult:
    mine = all_hashes.get(asset, [])
    if not mine:
        return GateResult("C", "pending", "no frames sampled; recycled-footage check inconclusive")
    clashes = []
    for other, theirs in all_hashes.items():
        if other == asset:
            continue
        for a in mine:
            if a["std"] < LOW_INFO_STD:
                continue
            for b in theirs:
                if b["std"] < LOW_INFO_STD:
                    continue
                ham = (a["h"] ^ b["h"]).bit_count()
                if ham <= CROSS_DUP_HAM:
                    clashes.append({"other": other, "ham": ham,
                                    "at": a["t"], "other_at": b["t"]})
    if clashes:
        return GateResult("C", "fail",
                          f"{len(clashes)} cross-asset near-identical frame pair(s)", 
                          {"clashes": clashes[:6]})
    return GateResult("C", "pass", f"no cross-asset duplicate footage across {len(mine)} sampled frames")


def gate_d(path: Path, reviews: dict[str, dict] | None = None) -> GateResult:
    """Content/narrative review: decidable only from a recorded human/vision verdict.

    This gate never auto-passes. A decision must be recorded as
    `receipts/media-review/<asset>.json`:

        {"asset": "<name>.mp4", "sha256": "<full digest>",
         "reviewer": "<who>", "reviewed_utc": "<iso8601>",
         "verdict": "pass"|"fail", "notes": "..."}

    The sha256 is mandatory and must equal the digest of the file on disk, so a
    review cannot be carried over to a re-rendered master. Any deviation
    (missing file, wrong hash, unknown verdict) keeps the gate `pending`.
    """
    digest = sha256_of(path) if path.is_file() else ""
    entry = (reviews or {}).get(path.name)
    if not entry:
        return GateResult("D", "pending",
                          "no recorded content review; needs human/vision judgement",
                          {"sha256": digest,
                           "note": "record a verdict in receipts/media-review/<asset>.json"})
    ev = {"sha256": digest, "review_sha256": entry.get("sha256"),
          "reviewer": entry.get("reviewer"), "reviewed_utc": entry.get("reviewed_utc"),
          "notes": entry.get("notes", "")}
    if entry.get("sha256") != digest:
        return GateResult("D", "pending",
                          "recorded review hash does not match this master; re-review required",
                          ev)
    verdict = str(entry.get("verdict", "")).lower()
    if verdict == "pass":
        return GateResult("D", "pass",
                          f"content review passed by {entry.get('reviewer', 'reviewer')}", ev)
    if verdict == "fail":
        return GateResult("D", "fail",
                          f"content review failed: {entry.get('notes', 'see review record')}", ev)
    return GateResult("D", "pending",
                      f"review record has unrecognised verdict {verdict!r}", ev)


def gate_e(path: Path, meta: dict) -> GateResult:
    streams = meta.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    try:
        vdur = float(video.get("duration") or meta.get("format", {}).get("duration") or 0)
        adur = float(audio.get("duration") or 0)
    except ValueError:
        vdur = adur = 0.0
    # Loudness + clipping + silence via ebur128.
    r = _run(["ffmpeg", "-v", "info", "-i", str(path),
              "-af", "ebur128=peak=true", "-f", "null", "-"])
    log = r.stderr
    lufs = None
    peak = None
    for line in log.splitlines():
        m = re.search(r"I:\s*(-?\d+\.\d+)\s*LUFS", line)
        if m:
            lufs = float(m.group(1))
        m = re.search(r"Peak:\s*(-?\d+\.\d+)\s*dBFS", line)
        if m:
            peak = float(m.group(1))
    # Silence scan.
    s = _run(["ffmpeg", "-v", "error", "-i", str(path),
              "-af", "silencedetect=noise=-50dB:d=2.0", "-f", "null", "-"]).stderr
    long_silences = len(re.findall(r"silence_start", s))
    ev = {"video_dur": round(vdur, 3), "audio_dur": round(adur, 3),
          "integrated_lufs": lufs, "true_peak_dbfs": peak, "silences_ge_2s": long_silences}
    problems = []
    if vdur and adur and abs(vdur - adur) > MAX_AV_DELTA_S:
        problems.append(f"A/V duration delta {abs(vdur - adur):.2f}s > {MAX_AV_DELTA_S}s")
    if lufs is None:
        problems.append("loudness undetermined")
    elif abs(lufs - (-14.0)) > LOUDNESS_TOL_DB:
        problems.append(f"loudness {lufs} LUFS outside -14±{LOUDNESS_TOL_DB}")
    if peak is not None and peak > -0.1:
        problems.append(f"true peak {peak} dBFS risks clipping")
    if long_silences:
        problems.append(f"{long_silences} silence gap(s) >= 2s")
    if problems:
        return GateResult("E", "fail", "; ".join(problems), ev)
    return GateResult("E", "pass", "A/V sync, loudness and silence within tolerance", ev)


def gate_f(path: Path, man: dict[str, dict], asset: str) -> GateResult:
    dec = _run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"])
    if dec.stderr.strip():
        return GateResult("F", "fail", f"final decode errors: {dec.stderr.strip()[:160]}")
    try:
        meta = ffprobe_streams(path)
    except RuntimeError as exc:
        return GateResult("F", "fail", str(exc))
    v = next((s for s in meta.get("streams", []) if s.get("codec_type") == "video"), {})
    dims = (int(v.get("width", 0)), int(v.get("height", 0)))
    ev = {"width": dims[0], "height": dims[1], "sha256": sha256_of(path),
          "bytes": path.stat().st_size}
    problems = []
    if dims not in EXPECTED_ASPECTS:
        problems.append(f"unexpected aspect {dims}")
    # Burned-in AI disclosure: OCR a mid frame and the end card.
    ocr_text = _ocr_frames(path, meta)
    ev["ocr_excerpt"] = ocr_text[:400]
    langs = _ocr_langs()
    ev["ocr_langs"] = sorted(langs)
    has_cjk = any(l.startswith("chi") for l in langs)
    if _has_disclosure(ocr_text):
        disclosure = "pass"
    elif not has_cjk:
        # A Chinese disclosure label (e.g. "AI生成合成内容") cannot be OCR-verified
        # without a CJK language pack, so this is undecidable, not a failure.
        disclosure = "pending"
    else:
        disclosure = "fail"
        problems.append("no AI-disclosure label detected on sampled frames")
    if problems:
        return GateResult("F", "fail", "; ".join(problems), ev)
    if disclosure == "pending":
        return GateResult("F", "pending",
                          "aspect + decode OK; disclosure undetermined (no CJK OCR pack to read a zh label)",
                          ev)
    return GateResult("F", "pass", "final decode, aspect and disclosure verified", ev)


def _has_disclosure(ocr_text: str) -> bool:
    """Tolerant AI-disclosure detection against noisy OCR output."""
    compact = re.sub(r"\s+", "", ocr_text.lower())
    return any(re.search(p, compact) for p in AI_DISCLOSURE_PATTERNS)


def _ocr_langs() -> set[str]:
    if not shutil.which("tesseract"):
        return set()
    r = _run(["tesseract", "--list-langs"])
    return {ln.strip() for ln in (r.stdout or "").splitlines()
            if ln.strip() and " " not in ln and ln.strip() != "List of available languages"}


def _ocr_frames(path: Path, meta: dict) -> str:
    if not shutil.which("tesseract"):
        return ""
    try:
        dur = float(meta.get("format", {}).get("duration") or 0)
    except ValueError:
        dur = 0.0
    text = []
    tmp = Path("/tmp/zyk_gate_ocr.png")
    # Sample across the whole timeline, not just two frames: a disclosure label may sit
    # anywhere in the video, and a miss would falsely report a compliance failure.
    # Upscale 3x + grayscale: the label is small relative to a 1080x1920 frame and
    # tesseract drops it at native resolution, which would false-FAIL a compliant master.
    durs = max(0.0, dur - 0.5)
    for frac in (0.02, 0.25, 0.5, 0.75, 0.98):
        at = min(durs, dur * frac)
        _run(["ffmpeg", "-y", "-v", "error", "-ss", f"{at:.2f}", "-i", str(path),
              "-vf", "scale=iw*3:ih*3,format=gray",
              "-frames:v", "1", "-update", "1", str(tmp)])
        if tmp.is_file() and tmp.stat().st_size:
            r = _run(["tesseract", str(tmp), "stdout", "-l", "eng+chi_sim"])
            text.append(r.stdout or "")
    return "\n".join(text)


def gate_g(asset: str, path: Path) -> GateResult:
    url = f"{MEDIA_RELEASE_BASE}/{asset}"
    # Release asset presence via gh (no browser needed).
    r = _run(["gh", "release", "view", MEDIA_RELEASE_TAG, "--repo",
              "editormorris-svg/zykai-net", "--json", "assets"])
    if r.returncode != 0:
        return GateResult("G", "pending",
                          f"cannot query release assets: {r.stderr.strip()[:120]}",
                          {"url": url})
    try:
        names = [a["name"] for a in json.loads(r.stdout).get("assets", [])]
    except json.JSONDecodeError:
        return GateResult("G", "pending", "release assets payload unparseable", {"url": url})
    if asset not in names:
        return GateResult("G", "fail", f"{asset} not present in release {MEDIA_RELEASE_TAG}",
                          {"url": url})
    # Roadmap Gate G asks for "uploaded bytes/hash where possible". GitHub's asset API
    # exposes size but not a digest, so verify the published byte length against the
    # local master. A mismatch means the served rendition is not the reviewed master.
    local_bytes = path.stat().st_size
    try:
        assets = json.loads(r.stdout).get("assets", [])
        pub_bytes = next((a.get("size") for a in assets if a["name"] == asset), None)
    except (json.JSONDecodeError, KeyError, TypeError):
        pub_bytes = None
    ev = {"url": url, "bytes": local_bytes, "published_bytes": pub_bytes}
    if pub_bytes is None:
        return GateResult("G", "pending",
                          f"{asset} present but published size unavailable; byte match unverified",
                          ev)
    if pub_bytes != local_bytes:
        return GateResult("G", "fail",
                          f"published bytes {pub_bytes} != local master {local_bytes}",
                          ev)
    return GateResult("G", "pass", f"release asset present, bytes match ({local_bytes}) at {url}",
                      ev)


def load_reviews() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if REVIEW_DIR.is_dir():
        for f in sorted(REVIEW_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            name = data.get("asset") or f.stem
            out[name] = data
    return out


def gate_asset(asset: str, path: Path, man: dict, all_hashes: dict,
               reviews: dict | None = None) -> AssetReceipt:
    rec = AssetReceipt(asset)
    rec.gates.append(gate_a(asset, path, man))
    b = gate_b(path)
    rec.gates.append(b)
    rec.gates.append(gate_c(asset, all_hashes))
    rec.gates.append(gate_d(path, reviews))
    try:
        meta = ffprobe_streams(path)
    except RuntimeError as exc:
        meta = {}
        rec.gates.append(GateResult("E", "fail", str(exc)))
    else:
        rec.gates.append(gate_e(path, meta))
    rec.gates.append(gate_f(path, man, asset))
    rec.gates.append(gate_g(asset, path))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", nargs="*", default=None)
    ap.add_argument("--media-dir", default=None,
                    help="override the media directory (e.g. a remediation staging dir)")
    ap.add_argument("--manifest", default=None,
                    help="override the provenance manifest (e.g. a staging manifest)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--decide", action="store_true",
                    help="exit 1 unless every asset is RELEASE_READY")
    args = ap.parse_args()

    assets = args.assets or list(DEFAULT_ASSETS)
    global MANIFEST
    if args.manifest:
        MANIFEST = Path(args.manifest)
    man = load_manifest()
    reviews = load_reviews()
    media_dir = Path(args.media_dir) if args.media_dir else PUBLIC_MEDIA
    paths = {a: (media_dir / a) for a in assets}

    all_hashes = {}
    for a, p in paths.items():
        if p.is_file():
            all_hashes[a] = sample_dhashes(p)

    receipts = [gate_asset(a, paths[a], man, all_hashes, reviews) for a in assets]

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "gate_set": "A-G (ZYK_MEDIA_PRODUCTION_ROADMAP v1.1 §4 / v1.2 §4)",
        "media_dir": str(media_dir),
        "reviews_loaded": sorted(reviews),
        "assets": [r.as_dict() for r in receipts],
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (RECEIPT_DIR / f"receipt-{stamp}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for r in receipts:
            print(f"{r.verdict:16} {r.asset}")
            for g in r.gates:
                mark = {"pass": "ok ", "fail": "FAIL", "pending": "hold"}[g.status]
                print(f"    [{mark}] Gate {g.gate}: {g.detail}")
        print(f"\nreceipt: {RECEIPT_DIR}/receipt-{stamp}.json")

    if args.decide:
        return 0 if all(r.verdict == "RELEASE_READY" for r in receipts) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
