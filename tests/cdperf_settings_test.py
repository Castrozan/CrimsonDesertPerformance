import importlib.machinery
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "package/linux/cdperf-settings"
loader = importlib.machinery.SourceFileLoader("cdperf_settings", str(SCRIPT))
specification = importlib.util.spec_from_loader("cdperf_settings", loader)
cdperf_settings = importlib.util.module_from_spec(specification)
loader.exec_module(cdperf_settings)

FRAME_GENERATION_ON = """<EngineOptionSave>
\t\t<EngineOptionVideo Name="_videoOption">
\t\t\t<OptionStringVector Name="_frameGenerationModeSelect" _value="AMD FSR Frame Generation"/>
\t\t\t<OptionBool Name="_enableNvidiaReflex" _value="True"/>
\t\t</EngineOptionVideo>
</EngineOptionSave>
"""


class CdperfSettingsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.settings = Path(self.directory.name) / "user_engine_option_save.xml"
        self.settings.write_text(FRAME_GENERATION_ON)

    def tearDown(self):
        self.directory.cleanup()

    def test_apply_removes_only_the_frame_generation_choice(self):
        cdperf_settings.apply(self.settings)
        text = self.settings.read_text()
        self.assertNotIn("_frameGenerationModeSelect", text)
        self.assertIn("_enableNvidiaReflex", text)

    def test_apply_twice_keeps_the_first_backup(self):
        cdperf_settings.apply(self.settings)
        cdperf_settings.apply(self.settings)
        self.assertEqual(cdperf_settings.backup_path(self.settings).read_text(), FRAME_GENERATION_ON)

    def test_revert_restores_the_original_byte_for_byte(self):
        cdperf_settings.apply(self.settings)
        cdperf_settings.revert(self.settings)
        self.assertEqual(self.settings.read_text(), FRAME_GENERATION_ON)
        self.assertFalse(cdperf_settings.backup_path(self.settings).exists())

    def test_matches_the_real_settings_file_backup(self):
        real = Path.home() / ".local/share/cdmp/save-backups/20261116-194910-cdperf/user_engine_option_save.xml"
        if not real.exists():
            self.skipTest("no real settings backup on this machine")
        shutil.copy2(real, self.settings)
        cdperf_settings.apply(self.settings)
        self.assertNotIn("_frameGenerationModeSelect", self.settings.read_text())


if __name__ == "__main__":
    unittest.main()
