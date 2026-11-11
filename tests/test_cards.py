import datetime
import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import config  # noqa: E402
import fetch_data  # noqa: E402
from cards import activity, heatmap, hero, repos, tiles  # noqa: E402

SVG = "{http://www.w3.org/2000/svg}"
MAX_BYTES = 300_000


def sample_data():
    """53 full weeks ending on a Wednesday, with a repeating count pattern."""
    end = datetime.date(2026, 11, 11)
    start = end - datetime.timedelta(days=(end.weekday() + 1) % 7 + 52 * 7)
    days, d, i = [], start, 0
    while d <= end:
        c = (0, 1, 3, 0, 7, 12, 2)[i % 7]
        days.append({"date": d.isoformat(), "count": c, "level": min(4, (c + 2) // 3)})
        d += datetime.timedelta(days=1)
        i += 1
    return {
        "contributions": fetch_data.summarize(days),
        "repos": {
            "job-application-skills": {"stars": 4, "language": "TeX"},
            "Where-AI-Agents-Break": {"stars": 1, "language": None},
            "Trajectory": {"stars": 0, "language": "TypeScript"},
        },
        "trajectory_entries": 123,
    }


def texts(svg):
    return [t.text for t in ET.fromstring(svg).iter(f"{SVG}text")]


class CardTestMixin:
    def check(self, svg, width):
        root = ET.fromstring(svg)
        self.assertAlmostEqual(float(root.get("width")), width, places=2)
        self.assertLess(len(svg.encode("utf-8")), MAX_BYTES)


class HeroTest(CardTestMixin, unittest.TestCase):
    def test_hero_without_portrait(self):
        svg = hero.render(config, sample_data(), None)
        self.check(svg, 880)
        found = texts(svg)
        self.assertIn("WASIF", found)
        self.assertIn("SAEED", found)
        self.assertIn(config.ROLE, found)

    def test_hero_inlines_portrait(self):
        portrait = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path id="engraving" d="M0 0L1 1"/></svg>'
        svg = hero.render(config, sample_data(), portrait)
        self.check(svg, 880)
        self.assertIn('id="engraving"', svg)


class HeatmapTest(CardTestMixin, unittest.TestCase):
    def test_one_cell_per_day_in_53_weeks(self):
        data = sample_data()
        svg = heatmap.render(config, data)
        self.check(svg, 880)
        cells = [r for r in ET.fromstring(svg).iter(f"{SVG}rect") if r.get("class") == "cell"]
        self.assertEqual(len(cells), len(data["contributions"]["days"]))


class ActivityTest(CardTestMixin, unittest.TestCase):
    def test_shows_total_streaks_and_twelve_bars(self):
        data = sample_data()
        svg = activity.render(config, data)
        self.check(svg, 880)
        found = texts(svg)
        c = data["contributions"]
        self.assertIn(f"{c['total']:,}", found)
        self.assertIn(str(c["longest_streak"]), found)
        bars = [r for r in ET.fromstring(svg).iter(f"{SVG}rect") if r.get("class") == "bar"]
        self.assertEqual(len(bars), 12)


class TilesTest(CardTestMixin, unittest.TestCase):
    def test_hand_set_tile(self):
        svg = tiles.render(config, sample_data(), 0)
        self.check(svg, 880 / 3)
        self.assertIn(config.TILES[0]["value"], texts(svg))

    def test_learn_tile_uses_live_trajectory_count(self):
        svg = tiles.render(config, sample_data(), 2)
        self.assertIn("123", texts(svg))

    def test_section_title(self):
        svg = tiles.title(config, "WHAT I'M BUILDING", "LIVE FROM GITHUB")
        self.check(svg, 880)
        self.assertIn("WHAT I'M BUILDING", texts(svg))


class ReposTest(CardTestMixin, unittest.TestCase):
    def test_repo_card_shows_live_stars_and_language(self):
        svg = repos.render(config, sample_data(), 0)
        self.check(svg, 880 / 3)
        found = texts(svg)
        self.assertIn("job-application-skills", found)
        self.assertIn("4", found)
        self.assertIn("TeX", found)

    def test_repo_without_language_still_renders(self):
        svg = repos.render(config, sample_data(), 1)
        self.check(svg, 880 / 3)

    def test_description_wraps_to_three_lines_max(self):
        class LongCfg:
            FEATURED = [{"repo": "Trajectory", "desc": "word " * 60}]

        svg = repos.render(LongCfg, sample_data(), 0)
        desc_lines = [t for t in ET.fromstring(svg).iter(f"{SVG}text") if t.get("class") == "desc"]
        self.assertLessEqual(len(desc_lines), 3)


if __name__ == "__main__":
    unittest.main()
