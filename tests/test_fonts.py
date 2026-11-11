import os
import unittest

FONTS = os.path.join(os.path.dirname(__file__), "..", "fonts")


class FontFilesTest(unittest.TestCase):
    def test_subset_fonts_exist_and_are_small_woff(self):
        for name in ("archivo-black.woff", "jetbrains-mono-400.woff", "jetbrains-mono-700.woff"):
            path = os.path.join(FONTS, name)
            self.assertTrue(os.path.exists(path), f"{name} missing")
            with open(path, "rb") as f:
                self.assertEqual(f.read(4), b"wOFF", f"{name} is not WOFF")
            self.assertLess(os.path.getsize(path), 40_000, f"{name} too big to embed")

    def test_licences_are_shipped(self):
        for name in ("OFL-ArchivoBlack.txt", "OFL-JetBrainsMono.txt"):
            self.assertTrue(os.path.exists(os.path.join(FONTS, name)))


if __name__ == "__main__":
    unittest.main()
