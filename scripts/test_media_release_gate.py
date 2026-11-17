"""Regression tests for the Gates A-G media release gate.

Roadmap v1.1 M1 exit test: "A deliberately truncated valid-hash clip, duplicated
footage, wrong soundtrack and broken final output are all blocked; a correct item
passes." These tests exercise the deterministic gates against synthetic fixtures.
"""
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HAS_FFMPEG = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'media_release_gate', ROOT / 'scripts' / 'media_release_gate.py')
gate = importlib.util.module_from_spec(spec)
# dataclasses resolve string annotations via sys.modules, so register before exec.
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)


def make_clip(dest: Path, seconds: float = 2.0, draw: str | None = None,
              audio_db: float = -14.0, size: str = '1080x1920') -> None:
    vf = f'scale={size}'
    if draw:
        vf += (",drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
               f":text='{draw}':fontcolor=white:fontsize=48:x=40:y=40")
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error',
        '-f', 'lavfi', '-i', f'testsrc=size={size}:rate=30:duration={seconds}',
        '-f', 'lavfi', '-i', f'sine=frequency=440:duration={seconds}',
        '-vf', vf, '-af', f'volume={audio_db}dB',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(dest),
    ], capture_output=True)


@unittest.skipUnless(HAS_FFMPEG, 'ffmpeg/ffprobe required for media gate regression fixtures')
class GateRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='zyk-gate-test-'))
        cls.valid = cls.tmp / 'valid.mp4'
        make_clip(cls.valid, draw='AI-Assisted Visuals')
        cls.truncated = cls.tmp / 'truncated.mp4'
        data = cls.valid.read_bytes()
        cls.truncated.write_bytes(data[: len(data) // 2])  # valid header, cut payload

    def test_gate_b_passes_valid_clip(self):
        res = gate.gate_b(self.valid)
        self.assertEqual(res.status, 'pass', res.detail)

    def test_gate_b_blocks_truncated_clip_with_same_prefix(self):
        """A truncated file can still hash consistently; decode must catch it."""
        res = gate.gate_b(self.truncated)
        self.assertEqual(res.status, 'fail', f'expected fail, got {res.status}: {res.detail}')

    def test_gate_f_blocks_broken_final_output(self):
        res = gate.gate_f(self.truncated, {}, 'truncated.mp4')
        self.assertEqual(res.status, 'fail')

    def test_gate_f_passes_when_disclosure_present(self):
        res = gate.gate_f(self.valid, {}, 'valid.mp4')
        self.assertIn(res.status, {'pass', 'pending'}, res.detail)
        if res.status == 'pending':
            self.assertIn('disclosure undetermined', res.detail)

    def test_gate_e_flags_loudness_drift(self):
        quiet = self.tmp / 'quiet.mp4'
        make_clip(quiet, seconds=1.5, audio_db=-40.0)
        meta = gate.ffprobe_streams(quiet)
        res = gate.gate_e(quiet, meta)
        details = res.detail
        self.assertTrue(res.status == 'fail' and 'loudness' in details, details)

    def test_gate_c_flags_duplicate_footage_across_assets(self):
        hashes = gate.sample_dhashes(self.valid)
        self.assertTrue(hashes, 'expected sampled dHashes')
        shared = {'a.mp4': hashes, 'b.mp4': hashes}
        res = gate.gate_c('a.mp4', shared)
        self.assertEqual(res.status, 'fail', res.detail)

    def test_gate_c_passes_for_distinct_assets(self):
        # dHash is structural, so a recolour keeps the same hash. The distinct
        # fixture must differ in structure (different lavfi pattern).
        other = self.tmp / 'other.mp4'
        subprocess.run([
            'ffmpeg', '-y', '-v', 'error',
            '-f', 'lavfi', '-i', 'smptehdbars=size=1080x1920:rate=30:duration=2',
            '-f', 'lavfi', '-i', 'sine=frequency=330:duration=2',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(other),
        ], capture_output=True)
        hashes = {'a.mp4': gate.sample_dhashes(self.valid),
                  'b.mp4': gate.sample_dhashes(other)}
        res = gate.gate_c('a.mp4', hashes)
        self.assertEqual(res.status, 'pass', res.detail)

    def test_gate_d_is_never_auto_passed(self):
        res = gate.gate_d(self.valid)
        self.assertEqual(res.status, 'pending',
                         'Gate D cannot be auto-decided without human/vision review')

    def test_receipt_verdict_is_fail_closed(self):
        rec = gate.AssetReceipt('x.mp4')
        rec.gates.append(gate.GateResult('A', 'pass', 'ok'))
        self.assertEqual(rec.verdict, 'RELEASE_READY')
        rec.gates.append(gate.GateResult('D', 'pending', 'review'))
        self.assertEqual(rec.verdict, 'PENDING_REVIEW')
        rec.gates.append(gate.GateResult('B', 'fail', 'broken'))
        self.assertEqual(rec.verdict, 'BLOCKED')


if __name__ == '__main__':
    unittest.main()
