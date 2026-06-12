import unittest
from pathlib import Path

import main


BASE_DIR = Path(__file__).resolve().parents[1]


class TwomiExternalSignalTests(unittest.TestCase):
    def test_affiliate_url_is_allowed(self):
        url = "https://px.a8.net/svt/ejp?a8mat=4B5TCD+32QNAQ+5VDQ+BX3J6"
        self.assertTrue(main.is_allowed_affiliate_url(url))

    def test_external_signal_template_has_required_disclosure_and_link(self):
        html = (BASE_DIR / "templates" / "external-signal.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("この通信にはTwomiへのアフィリエイトリンクが含まれます", html)
        self.assertIn("4B5TCD+32QNAQ+5VDQ+BX3J6", html)
        self.assertIn('rel="nofollow sponsored noopener"', html)
        self.assertIn('target="_blank"', html)
        self.assertIn("https://www15.a8.net/0.gif", html)

    def test_external_link_is_revealed_after_connection_loss(self):
        script = (BASE_DIR / "static" / "external-signal.js").read_text(
            encoding="utf-8"
        )

        self.assertIn('status.textContent = "接続維持不可"', script)
        self.assertIn("exit.hidden = false", script)
        self.assertIn("affiliate_outbound_click", script)
        self.assertIn('slot_name: "twomi_external_persona"', script)
        self.assertIn("await wait(3800)", script)
        self.assertIn("await wait(4500)", script)
        self.assertIn("await wait(3200)", script)

    def test_signal_room_uses_mobile_background_and_pillar_hotspot(self):
        html = (BASE_DIR / "templates" / "signal.html").read_text(encoding="utf-8")
        mobile_image = BASE_DIR / "static" / "signal-room-twomi-mobile.png"
        desktop_image = BASE_DIR / "static" / "signal-room-twomi-desktop.png"

        self.assertTrue(mobile_image.exists())
        self.assertTrue(desktop_image.exists())
        self.assertIn("/static/signal-room-twomi-mobile.png", html)
        self.assertIn("/static/signal-room-twomi-desktop.png", html)
        self.assertIn('class="signal-twomi-hotspot"', html)
        self.assertIn('href="/external-signal"', html)
        self.assertNotIn('href="https://px.a8.net/', html)
        self.assertIn("広告：外部通信を開始", html)
        self.assertNotIn("AD / EXTERNAL PERSONA DETECTED", html)
        self.assertNotIn("ky-monetize-route--signal", html)
        self.assertIn('"external_signal_entry"', html)
        self.assertNotIn('"affiliate_outbound_click"', html)


if __name__ == "__main__":
    unittest.main()
