from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from auto_generator import build_codex_context, build_daimyojin_config, load_config


class AutoGeneratorTests(unittest.TestCase):
    def test_codex_context_extracts_all_configured_sources(self) -> None:
        context = build_codex_context()
        self.assertTrue(context["codex_ready"])
        self.assertGreaterEqual(len(context["codex_sources"]), 5)
        self.assertTrue(all(source["sha256"] for source in context["codex_sources"]))
        self.assertLess(context["generation_ms"], 1000)
        self.assertNotIn("Central OS", " ".join(context["codex_pipeline"]))

    def test_daimyojin_config_is_generated_from_shared_config(self) -> None:
        config = build_daimyojin_config()
        self.assertIn("文字化け補正中...", config["statuses"])
        self.assertEqual(54, config["desktopTypeDelayMs"])
        self.assertEqual(64, config["mobileTypeDelayMs"])

    def test_invalid_config_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(json.dumps({"codex": {}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
