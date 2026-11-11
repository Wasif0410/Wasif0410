import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import fetch_data  # noqa: E402

FIXTURE = """
<table><tbody>
<tr>
<td tabindex="0" data-ix="0" style="width: 10px" data-date="2026-01-03" id="contribution-day-component-6-0" data-level="2" role="gridcell" data-view-component="true" class="ContributionCalendar-day"></td>
<td tabindex="0" data-ix="0" style="width: 10px" data-date="2026-01-01" id="contribution-day-component-4-0" data-level="0" role="gridcell" data-view-component="true" class="ContributionCalendar-day"></td>
<td tabindex="0" data-ix="0" style="width: 10px" data-date="2026-01-02" id="contribution-day-component-5-0" data-level="1" role="gridcell" data-view-component="true" class="ContributionCalendar-day"></td>
</tr>
</tbody></table>
<tool-tip id="tooltip-a" for="contribution-day-component-4-0" popover="manual" class="sr-only">No contributions on January 1st.</tool-tip>
<tool-tip id="tooltip-b" for="contribution-day-component-5-0" popover="manual" class="sr-only">1 contribution on January 2nd.</tool-tip>
<tool-tip id="tooltip-c" for="contribution-day-component-6-0" popover="manual" class="sr-only">1,205 contributions on January 3rd.</tool-tip>
"""


def series(start_counts):
    """Build days from (first ISO date, [counts]) consecutive days."""
    import datetime

    first, counts = start_counts
    d0 = datetime.date.fromisoformat(first)
    return [
        {"date": (d0 + datetime.timedelta(days=i)).isoformat(), "count": c, "level": min(c, 4)}
        for i, c in enumerate(counts)
    ]


class ParseContributionsTest(unittest.TestCase):
    def test_reads_dates_counts_and_levels_sorted_by_date(self):
        days = fetch_data.parse_contributions(FIXTURE)
        self.assertEqual(
            days,
            [
                {"date": "2026-01-01", "count": 0, "level": 0},
                {"date": "2026-01-02", "count": 1, "level": 1},
                {"date": "2026-01-03", "count": 1205, "level": 2},
            ],
        )

    def test_page_without_calendar_gives_empty_list(self):
        self.assertEqual(fetch_data.parse_contributions("<html>changed</html>"), [])


class SummarizeTest(unittest.TestCase):
    def setUp(self):
        # 01-28 .. 02-06
        self.days = series(("2026-01-28", [1, 2, 0, 3, 3, 5, 1, 0, 2, 0]))
        self.s = fetch_data.summarize(self.days)

    def test_total(self):
        self.assertEqual(self.s["total"], 17)

    def test_today_without_contributions_does_not_break_current_streak(self):
        self.assertEqual(self.s["current_streak"], 1)

    def test_longest_streak(self):
        self.assertEqual(self.s["longest_streak"], 4)

    def test_busiest_day(self):
        self.assertEqual(self.s["busiest"], {"date": "2026-02-02", "count": 5})

    def test_month_totals_in_order(self):
        self.assertEqual(
            self.s["months"],
            [{"month": "2026-01", "total": 6}, {"month": "2026-02", "total": 11}],
        )

    def test_keeps_days_for_the_graph(self):
        self.assertEqual(self.s["days"], self.days)

    def test_two_empty_days_at_the_end_mean_no_current_streak(self):
        s = fetch_data.summarize(series(("2026-03-01", [4, 0, 0])))
        self.assertEqual(s["current_streak"], 0)

    def test_today_with_contributions_counts(self):
        s = fetch_data.summarize(series(("2026-03-01", [0, 2, 3])))
        self.assertEqual(s["current_streak"], 2)

    def test_only_last_twelve_months_are_kept(self):
        import datetime

        d = datetime.date(2025, 1, 1)
        days = []
        while d <= datetime.date(2026, 2, 28):
            days.append({"date": d.isoformat(), "count": 1, "level": 1})
            d += datetime.timedelta(days=1)
        months = fetch_data.summarize(days)["months"]
        self.assertEqual(len(months), 12)
        self.assertEqual(months[0]["month"], "2025-03")
        self.assertEqual(months[-1]["month"], "2026-02")


class CountEntriesTest(unittest.TestCase):
    def test_counts_only_mdx_files_in_the_entries_folder(self):
        tree = {
            "tree": [
                {"path": "content/entries/2026-08-15-a.mdx", "type": "blob"},
                {"path": "content/entries/2026-08-16-b.mdx", "type": "blob"},
                {"path": "content/entries/notes.md", "type": "blob"},
                {"path": "content/context.md", "type": "blob"},
                {"path": "content/entries", "type": "tree"},
            ]
        }
        self.assertEqual(fetch_data.count_entries(tree, "content/entries"), 2)


if __name__ == "__main__":
    unittest.main()
