"""Smoke tests for the initial project foundation."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.collectors.saramin import (
    QUERY_PARAMETERS,
    SaraminCollector,
    SaraminSearchParams,
)
from src.config import ConfigurationError, Settings
from src.models import JobPosting


class SettingsTests(unittest.TestCase):
    def test_missing_api_key_has_actionable_error(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "SARAMIN_API_KEY"):
            Settings().require_saramin_api_key()


class JobPostingTests(unittest.TestCase):
    def test_model_accepts_source_independent_fields(self) -> None:
        posting = JobPosting(
            source="sample",
            source_job_id="job-1",
            company="Example Company",
            title="AI Engineer",
            url="https://example.com/jobs/1",
            published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(posting.source_job_id, "job-1")


class SaraminCollectorTests(unittest.TestCase):
    def test_query_params_are_ready_for_page_iteration(self) -> None:
        collector = SaraminCollector(api_key="test-key")
        params = collector.build_query_params(
            SaraminSearchParams(keywords="AI", start=2, count=20)
        )

        self.assertEqual(params[QUERY_PARAMETERS["access_key"]], "test-key")
        self.assertEqual(params[QUERY_PARAMETERS["start"]], 2)
        self.assertEqual(params[QUERY_PARAMETERS["count"]], 20)

    def test_parse_response_preserves_raw_json(self) -> None:
        self.assertEqual(
            SaraminCollector.parse_response(b'{"jobs": {"job": []}}'),
            {"jobs": {"job": []}},
        )

    @patch("src.collectors.saramin.load_settings", return_value=Settings())
    def test_collector_requires_api_key(self, _mock_load_settings: object) -> None:
        with self.assertRaisesRegex(ConfigurationError, "SARAMIN_API_KEY"):
            SaraminCollector()


if __name__ == "__main__":
    unittest.main()
