"""Local pages for the first slice. No login and no database."""

from __future__ import annotations

import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from first_slice.pipeline import SliceError, default_paths, run_slice

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
MAX_CSV_BYTES = 1_000_000

PAGES = {
    "/": STATIC / "index.html",
    "/slice.js": STATIC / "slice.js",
    "/slice.css": STATIC / "slice.css",
}
TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


def fixture_payload() -> dict:
    paths = default_paths()
    registry = json.loads(paths["registry"].read_text(encoding="utf-8"))
    csv_text = paths["csv"].read_text(encoding="utf-8")
    header = csv_text.splitlines()[0]
    return {
        "clientName": registry["client"]["name"],
        "claimedWaterRight": registry["claimedWaterRight"]["label"],
        "templateType": registry["claimedWaterRight"]["templateType"],
        "pointOfDiversion": registry["pointOfDiversion"]["label"],
        "deviceNickname": registry["measurementDevice"]["nickname"],
        "measurementDeviceId": registry["measurementDevice"]["measurementDeviceId"],
        "deviceNotes": registry["measurementDevice"]["notes"],
        "waterYear": registry["waterYear"],
        "method": registry["method"],
        "a1Defaults": registry["a1Defaults"],
        "headers": json.loads(paths["expected_headers"].read_text(encoding="utf-8")),
        "csvText": csv_text,
        "csvName": paths["csv"].name,
        "csvColumns": [name.strip() for name in header.split(",")],
    }


class SliceHandler(BaseHTTPRequestHandler):
    out_dir: Path = default_paths()["out"]

    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/fixture":
            self._send_json(200, fixture_payload())
            return
        page = PAGES.get(path)
        if page is None or not page.is_file():
            self._send_json(404, {"error": "Not found"})
            return
        body = page.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", TYPES.get(page.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/run":
            self._send_json(404, {"error": "Not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_CSV_BYTES + 100_000:
            self._send_json(400, {"error": "The logger CSV is too large for this slice"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "The request was not JSON"})
            return
        try:
            result = self._run(payload)
        except SliceError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except OSError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(200, result)

    def _run(self, payload: dict) -> dict:
        if payload.get("mapConfirmed") is not True:
            raise SliceError(
                "Confirm the column map before producing a Template Data File. Nothing was exported."
            )
        csv_text = payload.get("csvText")
        if not isinstance(csv_text, str) or not csv_text.strip():
            raise SliceError("Choose a logger CSV before running Totalizer")
        raw = csv_text.encode("utf-8")
        if len(raw) > MAX_CSV_BYTES:
            raise SliceError("The logger CSV is too large for this slice")
        filename = Path(str(payload.get("csvName") or "reading.csv")).name
        if not filename or filename in (".", ".."):
            raise SliceError("Original filename is not a single file name")
        incoming = self.out_dir / "incoming"
        incoming.mkdir(parents=True, exist_ok=True)
        csv_path = incoming / filename
        csv_path.write_bytes(raw)

        column_map = payload.get("columnMap")
        if not isinstance(column_map, dict):
            raise SliceError("Column map must say which Board A1 field each source feeds")
        map_path = self.out_dir / "confirmed-column-map.json"
        map_path.write_text(json.dumps(column_map), encoding="utf-8")

        paths = default_paths()
        result = run_slice(
            csv_path=csv_path,
            registry_path=paths["registry"],
            column_map_path=map_path,
            template_path=paths["template"],
            out_dir=self.out_dir,
            expected_headers_path=paths["expected_headers"],
            map_confirmed=True,
            claimed_water_right=str(payload.get("claimedWaterRight") or ""),
        )
        return {
            "claimedWaterRight": result["rows"][0]["WATER_RIGHT"],
            "headers": result["headers"],
            "rows": result["rows"],
            "xlsxName": result["xlsx"].name,
            "xlsxBase64": base64.b64encode(result["xlsx"].read_bytes()).decode("ascii"),
            "auditPath": str(result["audit"]),
            "rawPath": str(result["raw"]),
        }

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(port: int, out_dir: Path | None = None) -> ThreadingHTTPServer:
    if out_dir is not None:
        SliceHandler.out_dir = out_dir
    return ThreadingHTTPServer(("127.0.0.1", port), SliceHandler)


def main() -> None:
    server = make_server(8766)
    print("http://127.0.0.1:8766/")
    print("First slice only. It does not submit to CalWATRS and it does not certify compliance.")
    server.serve_forever()


if __name__ == "__main__":
    main()
