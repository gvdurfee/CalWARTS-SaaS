from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from first_slice.pipeline import (  # noqa: E402
    DATA_SHEET,
    HOW_TO_SHEET,
    SliceError,
    derive_rows,
    load_column_map,
    load_registry,
    read_data_sheet,
    read_readings,
    run_slice,
)

FIXTURES = ROOT / "fixtures/first-slice"
TEMPLATE = ROOT / "calwatrs-sources/template-a1.xlsx"
EXPECTED_HEADERS = json.loads(
    (FIXTURES / "expected-a1-headers.json").read_text(encoding="utf-8")
)


def run_fixture(out_dir: Path, csv_path: Path | None = None) -> dict:
    return run_slice(
        csv_path=csv_path or FIXTURES / "sample-logger.csv",
        registry_path=FIXTURES / "registry.json",
        column_map_path=FIXTURES / "column-map.json",
        template_path=TEMPLATE,
        out_dir=out_dir,
        expected_headers_path=FIXTURES / "expected-a1-headers.json",
        map_confirmed=True,
        claimed_water_right="SAMPLE-WR-001",
    )


class FirstSliceTest(unittest.TestCase):
    def test_sample_csv_writes_board_headers_and_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_fixture(out)
            headers, records = read_data_sheet(result["xlsx"])
            self.assertEqual(headers, EXPECTED_HEADERS)
            self.assertEqual(
                [
                    (
                        row["DATE"],
                        row["TIME"],
                        row["FLOW_RATE"],
                        row["VOLUME_DIVERTED_TO_USE"],
                    )
                    for row in records
                ],
                [
                    ("2025-10-01", "00:00:00", "0", "0"),
                    ("2025-10-01", "01:00:00", "10", "600"),
                    ("2025-10-01", "02:00:00", "10", "600"),
                    ("2025-10-01", "03:00:00", "0", "0"),
                ],
            )
            for row in records:
                self.assertIn(row["FLOW_RATE_UNIT"], ("CUBIC FEET PER SECOND", "GALLONS PER MINUTE"))
                self.assertIn(row["VOLUME_UNIT"], ("GALLONS", "ACRE-FEET"))
                self.assertGreaterEqual(float(row["FLOW_RATE"]), 0)
                self.assertGreaterEqual(float(row["VOLUME_DIVERTED_TO_USE"]), 0)
                self.assertEqual(row["BENEFICIAL_USE"], "irrigation")
                self.assertEqual(row["WATER_RIGHT"], "SAMPLE-WR-001")
                self.assertEqual(row["REDIVERSION_STATUS"], "no")
                self.assertEqual(row["PLACE_OF_USE"], "North field")
            self.assertEqual(records[0]["WATER_RIGHT"], records[-1]["WATER_RIGHT"])

            with zipfile.ZipFile(TEMPLATE) as original, zipfile.ZipFile(result["xlsx"]) as exported:
                self.assertEqual(original.read(HOW_TO_SHEET), exported.read(HOW_TO_SHEET))
                original_header = original.read(DATA_SHEET).decode("utf-8")
                exported_header = exported.read(DATA_SHEET).decode("utf-8")
            original_row = original_header[original_header.find("<row ") : original_header.find("</row>") + len("</row>")]
            exported_row = exported_header[exported_header.find("<row ") : exported_header.find("</row>") + len("</row>")]
            self.assertEqual(exported_row, original_row)

    def test_audit_log_records_method_raw_retention_and_each_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_fixture(out)
            raw = (FIXTURES / "sample-logger.csv").read_bytes()
            events = [
                json.loads(line)
                for line in result["audit"].read_text(encoding="utf-8").splitlines()
            ]
            kinds = [event["kind"] for event in events]
            self.assertEqual(
                kinds,
                [
                    "registry",
                    "raw_retained",
                    "column_map",
                    "method_parameters",
                    "derived_row",
                    "derived_row",
                    "derived_row",
                    "derived_row",
                    "export",
                ],
            )
            retained = events[1]
            self.assertEqual(retained["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(retained["byteLength"], len(raw))
            self.assertTrue(retained["immutable"])
            self.assertEqual((out / retained["storedPath"]).read_bytes(), raw)

            method = events[3]
            self.assertEqual(method["method"], "Totalizer")
            self.assertEqual(method["parameters"]["volumePerPulse"], 10)
            self.assertEqual(method["parameters"]["pulseVolumeUnit"], "GALLONS")
            self.assertIn("interval ending at timestamp", method["formula"])
            self.assertIn("pulses * volume per pulse", method["formula"])
            self.assertEqual(method["measurementDeviceId"], "M0SAMPLE1")
            self.assertTrue(events[2]["confirmed"])
            self.assertEqual(events[2]["claimedWaterRight"], "SAMPLE-WR-001")
            self.assertEqual(
                events[2]["columnMap"]["a1Fields"]["WATER_RIGHT"],
                "sticky claimed water right",
            )

            derived = [event for event in events if event["kind"] == "derived_row"]
            for event in derived:
                self.assertEqual(event["output"]["WATER_RIGHT"], "SAMPLE-WR-001")
            self.assertEqual(derived[1]["source"]["pulses"], 60)
            self.assertEqual(derived[1]["intervalMinutes"], 60)
            self.assertEqual(derived[1]["output"]["FLOW_RATE"], "10")
            self.assertEqual(derived[1]["output"]["VOLUME_DIVERTED_TO_USE"], "600")
            self.assertIn("600 / 60", derived[1]["formula"])

            exported = events[-1]
            self.assertEqual(
                exported["templateSha256"],
                hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(),
            )
            self.assertEqual(exported["headers"], EXPECTED_HEADERS)
            self.assertTrue(exported["doesNotCertify"])
            self.assertTrue(exported["doesNotSubmitToCalWATRS"])

    def test_second_run_appends_audit_and_does_not_rewrite_raw_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            first = run_fixture(out)
            raw_path = first["raw"]
            os.utime(raw_path, (1_700_000_000, 1_700_000_000))
            before = raw_path.read_bytes()
            run_fixture(out)
            self.assertEqual(raw_path.read_bytes(), before)
            self.assertEqual(raw_path.stat().st_mtime, 1_700_000_000)
            lines = first["audit"].read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 18)
            self.assertEqual(json.loads(lines[0])["kind"], "registry")
            self.assertEqual(json.loads(lines[9])["kind"], "registry")

    def test_negative_pulses_are_rejected_without_an_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            csv_path = out / "negative.csv"
            csv_path.write_text(
                "timestamp,pulses\n2025-10-01T00:00:00,-1\n",
                encoding="utf-8",
            )
            with self.assertRaises(SliceError):
                run_fixture(out, csv_path)
            self.assertEqual(list(out.glob("*.xlsx")), [])
            events = [
                json.loads(line)
                for line in (out / "audit-log.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertIn("raw_retained", [event["kind"] for event in events])
            self.assertIn("rejected", [event["kind"] for event in events])
            self.assertNotIn("export", [event["kind"] for event in events])

    def test_shorter_interval_uses_elapsed_minutes(self):
        registry = load_registry(FIXTURES / "registry.json")
        column_map = load_column_map(FIXTURES / "column-map.json")
        raw = (
            "timestamp,pulses\n"
            "2025-10-01T00:00:00,0\n"
            "2025-10-01T00:30:00,30\n"
        ).encode("utf-8")
        rows = derive_rows(read_readings(raw, column_map), registry)
        self.assertEqual(rows[1]["intervalMinutes"], 30)
        self.assertEqual(rows[1]["volumeGallons"], 300)
        self.assertEqual(rows[1]["output"]["FLOW_RATE"], "10")
        self.assertEqual(rows[1]["output"]["VOLUME_DIVERTED_TO_USE"], "300")

    def test_refuses_to_invent_a_duration_or_leave_the_water_year(self):
        registry = load_registry(FIXTURES / "registry.json")
        column_map = load_column_map(FIXTURES / "column-map.json")
        with self.assertRaises(SliceError):
            derive_rows(
                read_readings(
                    b"timestamp,pulses\n2025-10-01T00:00:00,5\n",
                    column_map,
                ),
                registry,
            )
        with self.assertRaises(SliceError):
            derive_rows(
                read_readings(
                    b"timestamp,pulses\n2024-09-30T00:00:00,0\n",
                    column_map,
                ),
                registry,
            )
        with self.assertRaises(SliceError):
            derive_rows(
                read_readings(
                    b"timestamp,pulses\n2025-10-01T02:00:00,0\n2025-10-01T01:00:00,0\n",
                    column_map,
                ),
                registry,
            )

    def test_export_waits_for_a_confirmed_map_and_uses_the_selected_right(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with self.assertRaises(SliceError):
                run_slice(
                    csv_path=FIXTURES / "sample-logger.csv",
                    registry_path=FIXTURES / "registry.json",
                    column_map_path=FIXTURES / "column-map.json",
                    template_path=TEMPLATE,
                    out_dir=out,
                    expected_headers_path=FIXTURES / "expected-a1-headers.json",
                    map_confirmed=False,
                )
            self.assertEqual(list(out.glob("*.xlsx")), [])
            self.assertFalse((out / "audit-log.jsonl").exists())

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_slice(
                csv_path=FIXTURES / "sample-logger.csv",
                registry_path=FIXTURES / "registry.json",
                column_map_path=FIXTURES / "column-map.json",
                template_path=TEMPLATE,
                out_dir=out,
                expected_headers_path=FIXTURES / "expected-a1-headers.json",
                map_confirmed=True,
                claimed_water_right="SAMPLE-WR-001",
            )
            self.assertTrue(str(result["xlsx"]).endswith("A1-SAMPLE-WR-001.xlsx"))
            for row in result["rows"]:
                self.assertEqual(row["WATER_RIGHT"], "SAMPLE-WR-001")

    def test_local_page_exports_only_after_the_map_is_confirmed(self):
        from first_slice.pipeline import default_paths
        from first_slice.ui import SliceHandler, make_server

        with tempfile.TemporaryDirectory() as tmp:
            server = make_server(0, Path(tmp))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            port = server.server_address[1]
            try:
                denied = HTTPConnection("127.0.0.1", port, timeout=5)
                denied.request(
                    "POST",
                    "/api/run",
                    body=json.dumps({"mapConfirmed": False}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                denied_response = denied.getresponse()
                self.assertEqual(denied_response.status, 400)
                denied_response.read()
                denied.close()

                accepted = HTTPConnection("127.0.0.1", port, timeout=5)
                accepted.request(
                    "POST",
                    "/api/run",
                    body=json.dumps(
                        {
                            "mapConfirmed": True,
                            "claimedWaterRight": "SAMPLE-WR-001",
                            "csvText": (FIXTURES / "sample-logger.csv").read_text(encoding="utf-8"),
                            "csvName": "sample-logger.csv",
                            "columnMap": json.loads(
                                (FIXTURES / "column-map.json").read_text(encoding="utf-8")
                            ),
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                accepted_response = accepted.getresponse()
                payload = json.loads(accepted_response.read().decode("utf-8"))
                self.assertEqual(accepted_response.status, 200, payload)
                self.assertEqual(payload["claimedWaterRight"], "SAMPLE-WR-001")
                self.assertEqual(payload["headers"], EXPECTED_HEADERS)
                self.assertTrue(all(row["WATER_RIGHT"] == "SAMPLE-WR-001" for row in payload["rows"]))
                self.assertTrue(all(float(row["FLOW_RATE"]) >= 0 for row in payload["rows"]))
                accepted.close()
            finally:
                server.shutdown()
                server.server_close()
                SliceHandler.out_dir = default_paths()["out"]

    def test_cli_prints_the_draft_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [sys.executable, "-m", "first_slice", "--out", tmp, "--confirm-map"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("does not certify compliance", completed.stdout)
            self.assertIn("does not submit to CalWATRS", completed.stdout)
            self.assertTrue((Path(tmp) / "A1-SAMPLE-WR-001.xlsx").is_file())


if __name__ == "__main__":
    unittest.main()
