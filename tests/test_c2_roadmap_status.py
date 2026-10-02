from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch
import c2_roadmap_status as status


class DashboardRetirementTests(unittest.TestCase):
    def test_retired_dashboard_never_fetches_or_opens_a_snapshot(self):
        with patch("subprocess.run") as run, patch("sqlite3.connect") as connect, redirect_stdout(StringIO()) as output:
            self.assertEqual(status.main(), 2)
        run.assert_not_called()
        connect.assert_not_called()
        self.assertIn("retired_permanently", output.getvalue())


if __name__ == "__main__":
    unittest.main()
