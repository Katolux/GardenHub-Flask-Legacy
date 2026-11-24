"""New publication smoke checks; these tests were not part of the 2026 snapshot."""
from pathlib import Path
import os
import gc
import socket
import tempfile
import unittest
from unittest.mock import patch

import db
from demo import prepare_demo


class HistoricalSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gardenhub-test-")
        self.addCleanup(self.temp.cleanup)
        self.network = patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.network_ex = patch.object(socket.socket, "connect_ex", side_effect=AssertionError("Network forbidden"))
        self.network_ex.start()
        self.addCleanup(self.network_ex.stop)
        prepare_demo(Path(self.temp.name) / "test.db")
        from app import app
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def tearDown(self):
        # Historical sqlite context managers commit, but do not close connections.
        # Collect unreachable connection cycles before removing Windows temp files.
        gc.collect()

    def test_main_pages_and_local_stylesheets(self):
        for url in ["/", "/history", "/automation", "/automation/beds", "/automation/plants",
                    "/automation/sensors", "/watering", "/automation/plants/add",
                    "/automation/plants/add-variety", "/automation/plants/demo_crop",
                    "/automation/plants/demo_crop/edit", "/static/css/main.css", "/static/style.css"]:
            with self.subTest(url=url):
                with self.client.get(url) as response:
                    self.assertEqual(response.status_code, 200)

    def test_sensor_validation_and_six_slots(self):
        self.assertEqual(self.client.post("/sensor_data", json={}).status_code, 400)
        body = {"bed": "demo_bed", "sensor": "demo_sensor", "moisture": "invalid"}
        self.assertEqual(self.client.post("/sensor_data", json=body).status_code, 400)
        body["moisture"] = 4000
        self.assertEqual(self.client.post("/sensor_data", json=body).status_code, 202)
        body["moisture"] = 1600
        for _ in range(5):
            self.assertEqual(self.client.post("/sensor_data", json=body).status_code, 200)
        self.assertEqual(self.client.post("/sensor_data", json=body).status_code, 409)
        with db.get_conn() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM sensor_readings").fetchone()[0], 6)
            self.assertEqual(conn.execute("SELECT moisture_pct FROM sensor_readings WHERE slot=2").fetchone()[0], 50)

    def test_watering_calculation_and_manual_event_are_persisted(self):
        self.assertEqual(self.client.post("/automation/run_watering_engine").status_code, 302)
        self.assertEqual(self.client.post("/water_now", data={"bed_id": "demo_bed", "minutes": 3}).status_code, 302)
        with db.get_conn() as conn:
            row = conn.execute("SELECT final_minutes, soil_factor FROM watering_decisions").fetchone()
            self.assertEqual(row, (13, 1.3))
            self.assertEqual(conn.execute("SELECT minutes, mode FROM watering_events").fetchone(), (3, "manual"))
            self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_bed_sensor_assignment_and_plant_crud(self):
        self.assertEqual(self.client.post("/automation/beds/add", data={"bed_id": "test_bed", "active": "1"}).status_code, 302)
        self.assertEqual(self.client.post("/automation/sensors/add", data={"sensor_id": "test_sensor", "active": "1"}).status_code, 302)
        self.assertEqual(self.client.post("/automation/sensors/assign", data={"sensor_id": "test_sensor", "bed_id": "test_bed"}).status_code, 302)
        form = {"plant_id": "test_crop", "name": "Test crop (synthetic)", "water_need": "medium",
                "sow_outdoors_months": "4,5", "harvest_months": "8,9"}
        self.assertEqual(self.client.post("/automation/plants/add", data=form).status_code, 302)
        self.assertEqual(self.client.get("/automation/plants/test_crop").status_code, 200)
        form["name"] = "Renamed synthetic crop"
        self.assertEqual(self.client.post("/automation/plants/test_crop/edit", data=form).status_code, 302)
        self.assertEqual(self.client.post("/automation/plants/add-variety", data={"plant_id": "test_crop", "variety_id": "test_variety", "name": "Synthetic variety"}).status_code, 302)
        self.assertEqual(self.client.post("/automation/plants/test_crop/varieties/test_variety/delete-confirm").status_code, 302)
        self.assertEqual(self.client.post("/automation/plants/test_crop/delete-confirm").status_code, 302)
        with db.get_conn() as conn:
            self.assertEqual(conn.execute("SELECT bed_id FROM sensors WHERE sensor_id='test_sensor'").fetchone()[0], "test_bed")
            self.assertIsNone(conn.execute("SELECT plant_id FROM plants WHERE plant_id='test_crop'").fetchone())

    def test_companion_cleanup_from_selected_historical_fix(self):
        from repositories import insert_rich_plant, delete_plant
        insert_rich_plant({"plant_id": "unplanted_crop", "name": "Synthetic unplanted crop"})
        with db.get_conn() as conn:
            conn.execute("INSERT INTO plant_companions(plant_id,other_plant_id,relation) VALUES(?,?,?)", ("demo_crop", "unplanted_crop", "good"))
        delete_plant("unplanted_crop")
        with db.get_conn() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM plant_companions").fetchone()[0], 0)

    def test_weather_retry_configuration_without_gpl_wrapper(self):
        import get_weather_new as weather
        import requests
        requirements = (Path(__file__).resolve().parents[1] / "requirements.txt").read_text()
        self.assertNotIn("retry-requests", requirements)
        session = requests.Session()
        self.addCleanup(session.close)
        with patch.dict(os.environ, {"GARDENHUB_LATITUDE": "0", "GARDENHUB_LONGITUDE": "0"}), \
             patch.object(weather.requests_cache, "CachedSession", return_value=session), \
             patch.object(weather.openmeteo_requests, "Client") as client:
            client.return_value.weather_api.side_effect = RuntimeError("Stop before weather transport")
            with self.assertRaisesRegex(RuntimeError, "Stop before weather transport"):
                weather.refresh_weather()
            self.assertIs(client.call_args.kwargs["session"], session)
            for scheme in ["http://", "https://"]:
                retry = session.get_adapter(scheme).max_retries
                self.assertEqual((retry.total, retry.read, retry.connect), (5, 5, 5))
                self.assertEqual(retry.backoff_factor, 0.2)
                self.assertEqual(set(retry.status_forcelist), {500, 502, 504})
                self.assertIsNone(retry.allowed_methods)
            self.assertEqual(client.return_value.weather_api.call_args.kwargs["params"]["latitude"], 0.0)

    def test_documented_historical_deletion_limit_for_planted_crop(self):
        import sqlite3
        from repositories import delete_plant
        with self.assertRaises(sqlite3.IntegrityError):
            delete_plant("demo_crop")
        with db.get_conn() as conn:
            self.assertIsNotNone(conn.execute("SELECT plant_id FROM plants WHERE plant_id='demo_crop'").fetchone())

    def test_missing_weather_configuration_does_not_make_request(self):
        from get_weather_new import refresh_weather
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GARDENHUB_LATITUDE"):
                refresh_weather()

    def test_demo_refuses_to_overwrite_data(self):
        with self.assertRaises(FileExistsError):
            prepare_demo(db.DB_PATH)

    def test_fresh_offline_schema_without_demo_data(self):
        db.DB_PATH = Path(self.temp.name) / "fresh.db"
        from db_init import init_all_tables
        init_all_tables()
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/history").status_code, 200)


if __name__ == "__main__":
    unittest.main()
