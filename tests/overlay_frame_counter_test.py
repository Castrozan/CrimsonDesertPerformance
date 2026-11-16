import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from sample_metrics import OverlayFrameCounter


def overlay_line(clock: str, frames: int) -> str:
    return f"[{clock}] INF [T1316] Overlay diag: frames {frames} | cam world space\n"


class OverlayFrameCounterTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.log_path = Path(self.directory.name) / "cdmp.log"
        self.counter = OverlayFrameCounter(self.log_path)

    def tearDown(self):
        self.directory.cleanup()

    def append(self, text: str):
        with self.log_path.open("a") as handle:
            handle.write(text)

    def test_rate_between_two_readings(self):
        self.append(overlay_line("18:54:19.994", 7622))
        self.assertIsNone(self.counter.frames_per_second())
        self.append("[18:54:21.101] INF [T360] Timing: unrelated\n")
        self.append(overlay_line("18:54:24.994", 7718))
        self.assertAlmostEqual(self.counter.frames_per_second(), 19.2)

    def test_restarted_game_resets_instead_of_negative_rate(self):
        self.append(overlay_line("18:54:19.994", 7622))
        self.counter.frames_per_second()
        self.append(overlay_line("18:54:24.994", 40))
        self.assertIsNone(self.counter.frames_per_second())

    def test_missing_log_gives_no_rate(self):
        self.assertIsNone(self.counter.frames_per_second())


if __name__ == "__main__":
    unittest.main()
