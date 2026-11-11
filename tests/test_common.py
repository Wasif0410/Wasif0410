import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from cards import common  # noqa: E402


class CommonTest(unittest.TestCase):
    def test_svg_doc_is_valid_xml_with_embedded_fonts(self):
        doc = common.svg_doc(880, 100, common.card(1, 1, 872, 80), title="t & t")
        root = ET.fromstring(doc)
        self.assertEqual(root.get("width"), "880")
        self.assertIn("data:font/woff;base64,", doc)
        self.assertIn("prefers-reduced-motion", doc)

    def test_svg_doc_embeds_only_requested_fonts(self):
        doc = common.svg_doc(10, 10, "", fonts=("mono",))
        self.assertEqual(doc.count("@font-face"), 1)

    def test_wrap_respects_limit_and_keeps_words(self):
        text = "Claude Code skills that turn a job posting into a tailored resume"
        lines = common.wrap(text, 20)
        self.assertTrue(all(len(line) <= 20 for line in lines))
        self.assertEqual(" ".join(lines), text)

    def test_split_geometry_lines_up_three_cards(self):
        xs = []
        for i in range(3):
            svg_w, local_x, card_w = common.split_geometry(i)
            self.assertAlmostEqual(svg_w, 880 / 3)
            self.assertAlmostEqual(card_w, 280)
            xs.append(i * svg_w + local_x)
        for got, want in zip(xs, (1, 297, 593)):
            self.assertAlmostEqual(got, want)

    def test_text_escapes(self):
        self.assertIn("&amp;", common.text(0, 0, "A & B", 12))

    def test_fmt_int(self):
        self.assertEqual(common.fmt_int(2074), "2,074")


if __name__ == "__main__":
    unittest.main()
