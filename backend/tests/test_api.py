"""Offline API security and validation checks; no database secrets required."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as module


class RoutesTests(unittest.TestCase):
    def setUp(self):
        module.app.config["TESTING"] = True
        self.client = module.app.test_client()

    def test_health_offline(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["purpose"], "research-prototype")

    def test_admin_upload_has_no_public_endpoint(self):
        response = self.client.post("/api/admin/upload?token=in-url")
        self.assertEqual(response.status_code, 404)

    def test_crashes_with_stubbed_db(self):
        with patch.object(module, "get_recent_crashes", return_value=[{"borough": "QUEENS"}]) as get:
            response = self.client.get("/api/crashes?limit=2")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [{"borough": "QUEENS"}])
            get.assert_called_once_with(limit=2)

    def test_invalid_limits_and_bboxes(self):
        for url in ("/api/crashes?limit=x", "/api/crashes/bbox",
                    "/api/crashes/bbox?min_lon=1&max_lon=0&min_lat=1&max_lat=2",
                    "/api/crashes/bbox?min_lon=nan&max_lon=2&min_lat=1&max_lat=2"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 400)

    def test_bbox_filters_and_caps_result_count(self):
        with patch.object(module, "get_crashes_in_bbox", return_value=[]) as get:
            response = self.client.get(
                "/api/crashes/bbox?min_lon=-75&min_lat=40&max_lon=-73&max_lat=41"
            )
            self.assertEqual(response.status_code, 200)
            get.assert_called_once_with(-75.0, 40.0, -73.0, 41.0, limit=500)

    def test_db_errors_are_sanitized(self):
        with patch.object(module, "get_recent_crashes", side_effect=RuntimeError("DB_PASSWORD=secret")):
            module.app.logger.disabled = True
            response = self.client.get("/api/crashes")
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("secret", response.get_data(as_text=True))

    def test_rejects_invalid_prediction_payload_without_model(self):
        for data in (None, {}, {"borough": "GOTHAM", "contributing_factor_vehicle_1": "Unknown"},
                     {"borough": "BRONX", "contributing_factor_vehicle_1": ""}):
            with self.subTest(data=data):
                response = self.client.post("/api/predict", json=data)
                self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
