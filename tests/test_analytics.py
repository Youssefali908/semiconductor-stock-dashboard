import unittest
import numpy as np
import pandas as pd
from analytics import compute_metrics, strongest_return_correlation


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.prices = pd.DataFrame(
            {
                "AAA": [100, 110, 105, 115, 120, 125],
                "BBB": [50, 50, 51, 48, 49, 50],
                "CCC": [20, 19, 21, 20, 22, 24],
            },
            index=pd.bdate_range("2026-01-05", periods=6),
        )

    def test_return_and_index(self):
        report = compute_metrics(self.prices)
        self.assertAlmostEqual(report["period_return_pct"]["AAA"], 25.0)
        self.assertAlmostEqual(report["period_return_pct"]["BBB"], 0.0)
        self.assertAlmostEqual(report["period_return_pct"]["CCC"], 20.0)
        self.assertEqual(report["indexed"].iloc[0].tolist(), [100, 100, 100])
        self.assertEqual(len(report["daily_returns"]), 5)

    def test_volatility_and_correlation(self):
        report = compute_metrics(self.prices)
        self.assertTrue((report["annualized_volatility_pct"] > 0).all())
        self.assertTrue(np.allclose(np.diag(report["correlation"]), [1, 1, 1]))
        best = strongest_return_correlation(report["correlation"])
        self.assertIsNotNone(best)
        self.assertNotEqual(best[0], best[1])

    def test_requirements(self):
        with self.assertRaisesRegex(ValueError, "three"):
            compute_metrics(self.prices[["AAA", "BBB"]])
        with self.assertRaisesRegex(ValueError, "five"):
            compute_metrics(self.prices.iloc[:4])
        with self.assertRaisesRegex(ValueError, "positive"):
            compute_metrics(self.prices.assign(AAA=-5))


if __name__ == "__main__":
    unittest.main()
