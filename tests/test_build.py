"""Static verification for generated GitHub Pages assets.

All builds go to temporary directories so running the tests never touches
the real `_site/` output used for deployment or local previews.
"""

import shutil
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import PLACEHOLDER, SOURCE, build_site  # noqa: E402

BASE_URL = 'https://example.github.io/race-control'


class SiteBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.target = build_site(BASE_URL, target=Path(cls._tmp.name) / '_site')

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_lua_has_real_asset_urls(self):
        script = (self.target / 'safetycar.lua').read_text(encoding='utf-8')
        self.assertIn(f"local SITE_BASE_URL = '{BASE_URL}'", script)
        self.assertIn("local SOUND_DEPLOYED_URL = SITE_BASE_URL .. '/sc_on.wav'", script)
        self.assertIn("local SOUND_LIGHTS_OFF_URL = SITE_BASE_URL .. '/sc_lights_off.wav'", script)
        self.assertNotIn(PLACEHOLDER, script)

    def test_config_has_correct_script_url(self):
        config = (self.target / 'extra_options.ini').read_text(encoding='utf-8')
        self.assertIn(f'SCRIPT = {BASE_URL}/safetycar.lua', config)
        self.assertIn('REQUIRED = 0', config)

    def test_wav_files_are_valid_and_distinct(self):
        content = []
        for filename in ('sc_on.wav', 'sc_lights_off.wav'):
            with wave.open(str(self.target / filename), 'rb') as audio:
                self.assertEqual(audio.getnchannels(), 1)
                self.assertEqual(audio.getsampwidth(), 2)
                self.assertIn(audio.getframerate(), (22050, 44100, 48000))
                self.assertGreater(audio.getnframes(), 1000)
                content.append(audio.readframes(audio.getnframes()))
        self.assertNotEqual(content[0], content[1])

    def test_source_lua_is_untouched(self):
        source = (SOURCE / 'safetycar.lua').read_text(encoding='utf-8')
        self.assertEqual(source.count(PLACEHOLDER), 1)


class BaseUrlValidationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.target = Path(self._tmp.name) / '_site'

    def test_trailing_slash_and_whitespace_are_removed(self):
        build_site('  https://example.github.io/race-control/  ', target=self.target)
        config = (self.target / 'extra_options.ini').read_text(encoding='utf-8')
        self.assertIn('SCRIPT = https://example.github.io/race-control/safetycar.lua', config)
        self.assertNotIn('//safetycar.lua', config)

    def test_custom_domain_without_path(self):
        build_site('https://racecontrol.example.com', target=self.target)
        script = (self.target / 'safetycar.lua').read_text(encoding='utf-8')
        self.assertIn("local SITE_BASE_URL = 'https://racecontrol.example.com'", script)

    def test_invalid_urls_are_rejected(self):
        for bad in (
            'http://example.github.io/race-control',
            'https://example.github.io/race-control?x=1',
            'https://example.github.io/race-control#top',
            'example.github.io/race-control',
            '',
        ):
            with self.subTest(url=bad), self.assertRaises(ValueError):
                build_site(bad, target=self.target)

    def test_rejected_url_does_not_touch_target(self):
        self.target.mkdir()
        marker = self.target / 'keep.txt'
        marker.write_text('x', encoding='utf-8')
        with self.assertRaises(ValueError):
            build_site('http://insecure.example.com', target=self.target)
        self.assertTrue(marker.exists())


class PlaceholderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = Path(self._tmp.name)
        self.source = tmp / 'site'
        shutil.copytree(SOURCE, self.source)
        self.lua = self.source / 'safetycar.lua'
        self.original = self.lua.read_text(encoding='utf-8')
        self.target = tmp / '_site'

    def test_missing_placeholder_is_rejected(self):
        self.lua.write_text(self.original.replace(PLACEHOLDER, 'https://x'), encoding='utf-8')
        with self.assertRaises(ValueError):
            build_site(BASE_URL, target=self.target, source=self.source)

    def test_duplicate_placeholder_is_rejected(self):
        self.lua.write_text(self.original + f"\n-- {PLACEHOLDER}\n", encoding='utf-8')
        with self.assertRaises(ValueError):
            build_site(BASE_URL, target=self.target, source=self.source)

    def test_missing_asset_is_rejected(self):
        (self.source / 'sc_on.wav').unlink()
        with self.assertRaises(FileNotFoundError):
            build_site(BASE_URL, target=self.target, source=self.source)


if __name__ == '__main__':
    unittest.main()
