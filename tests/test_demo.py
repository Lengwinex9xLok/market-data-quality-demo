import copy
import math
import unittest

from demo import audit, synthetic_quotes


class QualityAuditTests(unittest.TestCase):
    def test_fixture_detects_each_injected_failure(self):
        result = audit(synthetic_quotes())
        self.assertEqual(result["total_rows"], 6)
        self.assertEqual(result["rows_without_detected_issues"], 2)
        self.assertEqual(result["issue_counts"], {
            "DUPLICATE_EVENT": 1, "TIMESTAMP_REGRESSION": 1,
            "CROSSED_QUOTE": 1, "INVALID_PRICE": 1,
        })
        self.assertEqual([item["row"] for item in result["issues"]], [3, 4, 5, 6])

    def test_equivalent_times_and_distinct_symbols_do_not_regress(self):
        records = synthetic_quotes()[:2]
        records[1]["timestamp"] = "2024-01-02T07:00:00-05:00"
        records.append(dict(records[0], symbol="DEMO_B"))
        self.assertEqual(audit(records)["rows_with_detected_issues"], 0)

    def test_naive_time_and_unknown_prices_are_not_invented(self):
        for bad_price in (None, math.nan, math.inf, True, 0, -1):
            with self.subTest(price=bad_price):
                record = dict(synthetic_quotes()[0], bid=bad_price,
                              timestamp="2024-01-02T12:00:00")
                self.assertEqual(audit([record])["issue_counts"], {
                    "INVALID_TIMESTAMP": 1, "INVALID_PRICE": 1,
                })

    def test_audit_preserves_original_input(self):
        records = synthetic_quotes()
        original = copy.deepcopy(records)
        audit(records)
        self.assertEqual(records, original)

    def test_regression_does_not_reset_the_ordering_reference(self):
        records = synthetic_quotes()[:2]
        records.extend([
            dict(records[0], event_id="earlier-1"),
            dict(records[0], event_id="earlier-2"),
        ])
        self.assertEqual(audit(records)["issue_counts"], {"TIMESTAMP_REGRESSION": 2})


    def test_utc_suffix_and_offsets_refer_to_the_same_instant(self):
        times = (
            "2024-01-02T12:00:00.500Z",
            "2024-01-02T12:00:00.500+00:00",
            "2024-01-02T07:00:00.500-05:00",
        )
        records = [dict(synthetic_quotes()[0], event_id=f"time-{i}", timestamp=t)
                   for i, t in enumerate(times)]
        self.assertEqual(audit(records)["rows_with_detected_issues"], 0)

    def test_malformed_utc_designators_are_rejected(self):
        for value in (
            "2024-01-02Z12:00:00+00:00",
            "2024-01-02T12:00:00Z+00:00",
            "2024-01-02T12:00:00ZZ",
            "2024-01-02T12:00:00Zjunk",
            "2024-01-02T12:00:00+25:00",
            "2024-01-02T12:00:00",
        ):
            with self.subTest(timestamp=value):
                record = dict(synthetic_quotes()[0], timestamp=value)
                self.assertEqual(audit([record])["issue_counts"],
                                 {"INVALID_TIMESTAMP": 1})

    def test_numeric_price_strings_are_checked_without_rewriting(self):
        record = dict(synthetic_quotes()[0], bid="100", ask="100.02")
        original = copy.deepcopy(record)
        self.assertEqual(audit([record])["rows_with_detected_issues"], 0)
        self.assertEqual(record, original)
        crossed = dict(record, bid="100.03")
        self.assertEqual(audit([crossed])["issue_counts"], {"CROSSED_QUOTE": 1})

    def test_invalid_price_strings_are_rejected(self):
        for value in ("", "unknown", "NaN", "inf", "-inf", "1e999", "0", "-1"):
            with self.subTest(price=value):
                record = dict(synthetic_quotes()[0], bid=value)
                self.assertEqual(audit([record])["issue_counts"], {"INVALID_PRICE": 1})


if __name__ == "__main__":
    unittest.main()
