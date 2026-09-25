"""File-backed first slice. No database and no login.

Registry, raw ingest, the A1 Template Data File, and the audit log are files.
Whether a later version uses a database is still open.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import re
import sys
import uuid
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
DATA_SHEET = "xl/worksheets/sheet2.xml"
HOW_TO_SHEET = "xl/worksheets/sheet1.xml"
SHARED_STRINGS = "xl/sharedStrings.xml"

FLOW_UNITS = ("CUBIC FEET PER SECOND", "GALLONS PER MINUTE")
VOLUME_UNITS = ("GALLONS", "ACRE-FEET")
# Same factors as the what-if demo.
GPM_PER_CFS = 448.83116883
GALLONS_PER_ACRE_FOOT = 325851

A1_HEADERS = (
    "DATE",
    "TIME",
    "FLOW_RATE",
    "FLOW_RATE_UNIT",
    "VOLUME_DIVERTED_TO_USE",
    "VOLUME_UNIT",
    "BENEFICIAL_USE",
    "WATER_RIGHT",
    "REDIVERSION_STATUS",
    "PLACE_OF_USE",
)
NUMERIC_HEADERS = {"FLOW_RATE", "VOLUME_DIVERTED_TO_USE"}
COLUMNS = tuple("ABCDEFGHIJ")
TIMESTAMP_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$"
)

FORMULA = (
    "Each row's pulses are pulses counted in the interval ending at timestamp. "
    "Interval volume in gallons = pulses * volume per pulse. "
    "The first timestamp is a start mark with no previous timestamp, so the interval length is unknown. "
    "Its volume is still pulses * volume per pulse, and its flow rate is 0 only when that volume is 0. "
    "A positive volume on the first row is rejected because a flow rate would require inventing a duration. "
    "For each later row, interval minutes = (this timestamp - previous timestamp) in minutes, "
    "and flow rate in gallons per minute = interval volume / interval minutes. "
    "Output flow and volume use the registry units. "
    "GALLONS PER MINUTE and GALLONS are unchanged. "
    "CUBIC FEET PER SECOND = gallons per minute / 448.83116883. "
    "ACRE-FEET = gallons / 325851."
)

ACTOR = "local run (no login in this slice)"


class SliceError(Exception):
    """A first-slice input or method problem. No Template Data File is written."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SliceError(f"Could not read {path}: {exc}") from exc


def parse_day(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SliceError(f"{label} must be YYYY-MM-DD") from exc


def require_unit(value: str, allowed: tuple[str, ...], label: str) -> str:
    if value not in allowed:
        raise SliceError(f"{label} must be one of: {', '.join(allowed)}")
    return value


def load_registry(path: Path) -> dict:
    registry = load_json(path)
    try:
        right = registry["claimedWaterRight"]
        device = registry["measurementDevice"]
        year = registry["waterYear"]
        method = registry["method"]
        defaults = registry["a1Defaults"]
        client_name = registry["client"]["name"]
        pod = registry["pointOfDiversion"]["label"]
    except (KeyError, TypeError) as exc:
        raise SliceError(f"Registry {path} is missing a required field: {exc}") from exc

    if right.get("templateType") != "A1":
        raise SliceError("This slice exports template A1 only")
    if method.get("name") != "Totalizer":
        raise SliceError("This slice runs the Totalizer method only")
    if method.get("pulseVolumeUnit") != "GALLONS":
        raise SliceError("This slice accepts a pulse volume unit of GALLONS only")

    volume_per_pulse = method.get("volumePerPulse")
    if not isinstance(volume_per_pulse, (int, float)) or isinstance(volume_per_pulse, bool):
        raise SliceError("Volume per pulse must be a number")
    if volume_per_pulse <= 0:
        raise SliceError("Volume per pulse must be greater than 0")

    flow_unit = require_unit(method.get("outputFlowUnit", ""), FLOW_UNITS, "Flow rate unit")
    volume_unit = require_unit(method.get("outputVolumeUnit", ""), VOLUME_UNITS, "Volume unit")
    start = parse_day(year.get("start", ""), "Water year start")
    end = parse_day(year.get("end", ""), "Water year end")
    if end < start:
        raise SliceError("Water year end is before the start")

    status = defaults.get("REDIVERSION_STATUS")
    if status not in ("yes", "no"):
        raise SliceError("Rediversion status must be yes or no")
    if defaults.get("WATER_RIGHT") != right.get("label"):
        raise SliceError("WATER_RIGHT must match the claimed water right label")
    for key in ("BENEFICIAL_USE", "PLACE_OF_USE"):
        if not str(defaults.get(key, "")).strip():
            raise SliceError(f"{key} is blank")
    if not str(client_name).strip() or not str(pod).strip():
        raise SliceError("Client name and Point of Diversion are required")
    if not str(device.get("measurementDeviceId", "")).strip():
        raise SliceError("Measurement Device ID is required")
    return registry


def load_column_map(path: Path) -> dict:
    column_map = load_json(path)
    for key in ("timestampColumn", "readingColumn"):
        if not str(column_map.get(key, "")).strip():
            raise SliceError(f"Column map is missing {key}")
    if column_map.get("readingKind") not in (None, "pulses"):
        raise SliceError("This slice maps a pulses column only")
    column_map.setdefault("readingKind", "pulses")
    column_map.setdefault(
        "assumption",
        "Each row's pulses are pulses counted in the interval ending at timestamp.",
    )
    return validate_column_map(column_map)


def validate_column_map(column_map: dict) -> dict:
    """A person maps logger columns onto Board A1 fields. WATER_RIGHT is never a CSV column."""
    fields = column_map.get("a1Fields")
    if not isinstance(fields, dict):
        raise SliceError("Column map must say which Board A1 field each source feeds")
    timestamp_column = column_map["timestampColumn"]
    reading_column = column_map["readingColumn"]
    if fields.get("DATE") != timestamp_column or fields.get("TIME") != timestamp_column:
        raise SliceError("DATE and TIME must both be mapped from the timestamp column")
    if fields.get("FLOW_RATE") != reading_column or fields.get("VOLUME_DIVERTED_TO_USE") != reading_column:
        raise SliceError(
            "FLOW_RATE and VOLUME_DIVERTED_TO_USE must be mapped from the pulses column through Totalizer"
        )
    locked = {
        "FLOW_RATE_UNIT": "registry",
        "VOLUME_UNIT": "registry",
        "BENEFICIAL_USE": "registry",
        "REDIVERSION_STATUS": "registry",
        "PLACE_OF_USE": "registry",
        "WATER_RIGHT": "sticky claimed water right",
    }
    for header, source in locked.items():
        if fields.get(header) != source:
            raise SliceError(f"{header} must use {source}, not a different CSV column")
    missing = [header for header in A1_HEADERS if header not in fields]
    if missing:
        raise SliceError("Column map is missing Board field(s): " + ", ".join(missing))
    return column_map


def parse_timestamp(value: str, line_number: int) -> datetime:
    match = TIMESTAMP_RE.match(value.strip())
    if not match:
        raise SliceError(
            f"Line {line_number}: timestamp must be YYYY-MM-DDThh:mm:ss with no timezone"
        )
    parts = [int(part) for part in match.groups()]
    try:
        return datetime(*parts)
    except ValueError as exc:
        raise SliceError(f"Line {line_number}: timestamp is not a real date") from exc


def parse_pulses(value: str, line_number: int) -> float:
    text = value.strip()
    try:
        pulses = float(text)
    except ValueError as exc:
        raise SliceError(f"Line {line_number}: pulses must be a number") from exc
    if pulses < 0:
        raise SliceError(f"Line {line_number}: pulses must not be negative")
    return pulses


def read_readings(raw: bytes, column_map: dict) -> list[dict]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise SliceError("Logger CSV must be UTF-8") from exc

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise SliceError("Logger CSV has no header row")
    fields = [name.strip() for name in reader.fieldnames]
    timestamp_column = column_map["timestampColumn"]
    reading_column = column_map["readingColumn"]
    missing = [name for name in (timestamp_column, reading_column) if name not in fields]
    if missing:
        raise SliceError(
            "Logger CSV is missing mapped column(s): " + ", ".join(missing)
        )

    readings = []
    for index, row in enumerate(reader, start=2):
        if row is None or all(not str(cell or "").strip() for cell in row.values()):
            continue
        moment = parse_timestamp(row[timestamp_column] or "", index)
        pulses = parse_pulses(row[reading_column] or "", index)
        readings.append({"line": index, "timestamp": moment, "pulses": pulses})

    if not readings:
        raise SliceError("Logger CSV has no readings")
    return readings


def format_measurement(value: float) -> str:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise SliceError("A derived measurement was not a number")
    if value < 0:
        raise SliceError("Refusing to write a negative flow rate or volume")
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text if text else "0"


def convert_output(volume_gallons: float, flow_gpm: float, method: dict) -> tuple[str, str]:
    flow_unit = method["outputFlowUnit"]
    volume_unit = method["outputVolumeUnit"]
    if flow_unit == "GALLONS PER MINUTE":
        flow = flow_gpm
    else:
        flow = flow_gpm / GPM_PER_CFS
    if volume_unit == "GALLONS":
        volume = volume_gallons
    else:
        volume = volume_gallons / GALLONS_PER_ACRE_FOOT
    return format_measurement(flow), format_measurement(volume)


def derive_rows(readings: list[dict], registry: dict) -> list[dict]:
    method = registry["method"]
    defaults = registry["a1Defaults"]
    year = registry["waterYear"]
    start = date.fromisoformat(year["start"])
    end = date.fromisoformat(year["end"])
    factor = float(method["volumePerPulse"])
    derived = []

    for index, reading in enumerate(readings):
        moment = reading["timestamp"]
        if moment.date() < start or moment.date() > end:
            raise SliceError(
                f"Line {reading['line']}: timestamp is outside {year['label']}"
            )
        pulses = reading["pulses"]
        volume_gallons = pulses * factor
        previous = None
        interval_minutes = None
        if index == 0:
            if volume_gallons != 0:
                raise SliceError(
                    "The first row has pulses but no previous timestamp, "
                    "so a flow rate would require inventing a duration"
                )
            flow_gpm = 0.0
            short_formula = (
                f"start mark; volume_gallons = {format_measurement(pulses)} * "
                f"{format_measurement(factor)}; flow_gpm = 0 because volume_gallons is 0"
            )
        else:
            previous = readings[index - 1]["timestamp"]
            seconds = (moment - previous).total_seconds()
            if seconds <= 0:
                raise SliceError(
                    f"Line {reading['line']}: timestamps must be strictly increasing"
                )
            interval_minutes = seconds / 60.0
            flow_gpm = volume_gallons / interval_minutes
            short_formula = (
                f"volume_gallons = {format_measurement(pulses)} * {format_measurement(factor)}; "
                f"interval_minutes = {format_measurement(interval_minutes)}; "
                f"flow_gpm = {format_measurement(volume_gallons)} / "
                f"{format_measurement(interval_minutes)}"
            )

        flow_text, volume_text = convert_output(volume_gallons, flow_gpm, method)
        output = {
            "DATE": moment.strftime("%Y-%m-%d"),
            "TIME": moment.strftime("%H:%M:%S"),
            "FLOW_RATE": flow_text,
            "FLOW_RATE_UNIT": method["outputFlowUnit"],
            "VOLUME_DIVERTED_TO_USE": volume_text,
            "VOLUME_UNIT": method["outputVolumeUnit"],
            "BENEFICIAL_USE": defaults["BENEFICIAL_USE"],
            "WATER_RIGHT": defaults["WATER_RIGHT"],
            "REDIVERSION_STATUS": defaults["REDIVERSION_STATUS"],
            "PLACE_OF_USE": defaults["PLACE_OF_USE"],
        }
        derived.append(
            {
                "rowIndex": index,
                "sourceLine": reading["line"],
                "source": {
                    "timestamp": moment.strftime("%Y-%m-%dT%H:%M:%S"),
                    "pulses": pulses,
                    "previousTimestamp": (
                        None if previous is None else previous.strftime("%Y-%m-%dT%H:%M:%S")
                    ),
                },
                "intervalMinutes": interval_minutes,
                "volumeGallons": volume_gallons,
                "flowGpm": flow_gpm,
                "formula": short_formula,
                "output": output,
            }
        )
    return derived


def shared_strings(xml: bytes) -> list[str]:
    root = ET.fromstring(xml)
    values = []
    for item in root.findall("m:si", NS):
        texts = [node.text or "" for node in item.iter(MAIN + "t")]
        values.append("".join(texts))
    return values


def cell_value(cell: ET.Element, strings: list[str]) -> str:
    kind = cell.get("t")
    if kind == "s":
        node = cell.find("m:v", NS)
        return strings[int(node.text)]
    if kind == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(MAIN + "t"))
    node = cell.find("m:v", NS)
    if node is None or node.text is None:
        return ""
    return node.text


def column_index(ref: str) -> int:
    letters = "".join(char for char in ref if char.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index - 1


def read_data_sheet(xlsx_path: Path) -> tuple[list[str], list[dict]]:
    with zipfile.ZipFile(xlsx_path) as workbook:
        strings = shared_strings(workbook.read(SHARED_STRINGS))
        sheet = ET.fromstring(workbook.read(DATA_SHEET))
    rows = []
    for row in sheet.findall("m:sheetData/m:row", NS):
        cells = {}
        for cell in row.findall("m:c", NS):
            cells[column_index(cell.get("r", "A1"))] = cell_value(cell, strings)
        if cells:
            rows.append(cells)
    if not rows:
        raise SliceError(f"{xlsx_path} Data sheet is empty")
    header_cells = rows[0]
    headers = [header_cells[index] for index in range(len(A1_HEADERS))]
    if any(index not in header_cells for index in range(len(A1_HEADERS))):
        raise SliceError("Data sheet header row is missing a Board column")
    if len(header_cells) != len(A1_HEADERS):
        raise SliceError("Data sheet header row does not have exactly the Board columns")
    records = []
    for cells in rows[1:]:
        if not any(cells.values()):
            continue
        records.append(
            {header: cells.get(index, "") for index, header in enumerate(headers)}
        )
    return headers, records


def template_headers(template_path: Path) -> list[str]:
    headers, _records = read_data_sheet(template_path)
    return headers


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def rewrite_data_sheet(xml: str, records: list[dict], headers: list[str]) -> str:
    start = xml.find("<sheetData>")
    end = xml.find("</sheetData>")
    if start < 0 or end < 0:
        raise SliceError("Board template Data sheet has no sheetData")
    header_start = xml.find("<row ", start)
    header_end = xml.find("</row>", header_start)
    if header_start < 0 or header_end < 0:
        raise SliceError("Board template Data sheet has no header row")
    header_xml = xml[header_start : header_end + len("</row>")]

    body = []
    for index, record in enumerate(records):
        excel_row = index + 2
        cells = []
        for column, header in zip(COLUMNS, headers):
            ref = f"{column}{excel_row}"
            value = xml_escape(record[header])
            if header in NUMERIC_HEADERS:
                cells.append(f'<c r="{ref}"><v>{value}</v></c>')
            else:
                cells.append(
                    f'<c r="{ref}" s="1" t="inlineStr"><is><t>{value}</t></is></c>'
                )
        body.append(
            f'<row r="{excel_row}" spans="1:10" x14ac:dyDescent="0.2">{"".join(cells)}</row>'
        )

    sheet_data = "<sheetData>" + header_xml + "".join(body) + "</sheetData>"
    updated = xml[:start] + sheet_data + xml[end + len("</sheetData>") :]
    last_row = len(records) + 1
    return re.sub(
        r'<dimension ref="[^"]*"/>',
        f'<dimension ref="A1:J{last_row}"/>',
        updated,
        count=1,
    )


def write_a1_xlsx(template_path: Path, dest: Path, records: list[dict], headers: list[str]) -> None:
    with zipfile.ZipFile(template_path) as source:
        sheet_xml = source.read(DATA_SHEET).decode("utf-8")
        rewritten = rewrite_data_sheet(sheet_xml, records, headers).encode("utf-8")
        dest.parent.mkdir(parents=True, exist_ok=True)
        temporary = dest.with_suffix(dest.suffix + ".tmp")
        with zipfile.ZipFile(temporary, "w") as target:
            for info in source.infolist():
                data = rewritten if info.filename == DATA_SHEET else source.read(info.filename)
                replacement = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
                replacement.compress_type = info.compress_type
                replacement.external_attr = info.external_attr
                target.writestr(replacement, data)
    temporary.replace(dest)


def retain_raw(out_dir: Path, original_name: str, raw: bytes) -> Path:
    digest = sha256_bytes(raw)
    filename = Path(original_name).name or "reading.csv"
    if filename in (".", "..") or "/" in filename or "\\" in filename:
        raise SliceError("Original filename is not a single file name")
    dest = out_dir / "raw" / digest / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if dest.read_bytes() != raw:
            raise SliceError(f"Raw series already stored at {dest} with different bytes")
        return dest
    dest.write_bytes(raw)
    return dest


def append_audit(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def export_name(label: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", label).strip("-") or "water-right"
    return f"A1-{safe}.xlsx"


def event_base(run_id: str, kind: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "at": datetime.now(timezone.utc).isoformat(),
        "actor": ACTOR,
        "runId": run_id,
        "kind": kind,
    }


def run_slice(
    csv_path: Path,
    registry_path: Path,
    column_map_path: Path,
    template_path: Path,
    out_dir: Path,
    expected_headers_path: Path,
    map_confirmed: bool = False,
    claimed_water_right: str | None = None,
) -> dict:
    if not map_confirmed:
        raise SliceError(
            "Confirm the column map before producing a Template Data File. Nothing was exported."
        )
    registry = load_registry(registry_path)
    chosen_right = (
        registry["claimedWaterRight"]["label"]
        if claimed_water_right is None
        else str(claimed_water_right).strip()
    )
    if not chosen_right:
        raise SliceError("Enter a claimed water right once before export")
    registry = copy.deepcopy(registry)
    registry["claimedWaterRight"]["label"] = chosen_right
    registry["a1Defaults"]["WATER_RIGHT"] = chosen_right
    column_map = load_column_map(column_map_path)
    expected = json.loads(expected_headers_path.read_text(encoding="utf-8"))
    headers = template_headers(template_path)
    if headers != expected or headers != list(A1_HEADERS):
        raise SliceError(
            "Board A1 Data headers do not match fixtures/first-slice/expected-a1-headers.json"
        )

    raw = csv_path.read_bytes()
    raw_path = retain_raw(out_dir, csv_path.name, raw)
    template_hash = sha256_bytes(template_path.read_bytes())
    run_id = str(uuid.uuid4())
    audit_path = out_dir / "audit-log.jsonl"
    label = chosen_right
    xlsx_path = out_dir / export_name(label)

    base_events = [
        {**event_base(run_id, "registry"), "registry": registry},
        {
            **event_base(run_id, "raw_retained"),
            "sha256": sha256_bytes(raw),
            "byteLength": len(raw),
            "originalFilename": csv_path.name,
            "storedPath": str(raw_path.relative_to(out_dir)),
            "immutable": True,
        },
        {
            **event_base(run_id, "column_map"),
            "columnMap": column_map,
            "confirmed": True,
            "claimedWaterRight": label,
        },
    ]

    try:
        derived = derive_rows(read_readings(raw, column_map), registry)
    except SliceError as exc:
        append_audit(
            audit_path,
            [
                *base_events,
                {**event_base(run_id, "rejected"), "message": str(exc)},
            ],
        )
        raise

    records = [row["output"] for row in derived]
    write_a1_xlsx(template_path, xlsx_path, records, headers)
    method = registry["method"]
    events = [
        *base_events,
        {
            **event_base(run_id, "method_parameters"),
            "method": "Totalizer",
            "parameters": method,
            "formula": FORMULA,
            "measurementDeviceId": registry["measurementDevice"]["measurementDeviceId"],
            "claimedWaterRight": label,
            "waterYear": registry["waterYear"],
        },
    ]
    for row in derived:
        events.append(
            {
                **event_base(run_id, "derived_row"),
                "rowIndex": row["rowIndex"],
                "sourceLine": row["sourceLine"],
                "source": row["source"],
                "parameters": {
                    "volumePerPulse": method["volumePerPulse"],
                    "pulseVolumeUnit": method["pulseVolumeUnit"],
                },
                "intervalMinutes": row["intervalMinutes"],
                "volumeGallons": row["volumeGallons"],
                "flowGpm": row["flowGpm"],
                "formula": row["formula"],
                "output": row["output"],
            }
        )
    events.append(
        {
            **event_base(run_id, "export"),
            "templatePath": str(template_path),
            "templateSha256": template_hash,
            "dataSheet": "Data",
            "headers": headers,
            "outputPath": xlsx_path.name,
            "rowCount": len(records),
            "doesNotCertify": True,
            "doesNotSubmitToCalWATRS": True,
        }
    )
    append_audit(audit_path, events)
    return {
        "runId": run_id,
        "xlsx": xlsx_path,
        "audit": audit_path,
        "raw": raw_path,
        "rows": records,
        "headers": headers,
    }


def default_paths() -> dict[str, Path]:
    return {
        "csv": ROOT / "fixtures/first-slice/sample-logger.csv",
        "registry": ROOT / "fixtures/first-slice/registry.json",
        "column_map": ROOT / "fixtures/first-slice/column-map.json",
        "template": ROOT / "calwatrs-sources/template-a1.xlsx",
        "expected_headers": ROOT / "fixtures/first-slice/expected-a1-headers.json",
        "out": ROOT / "out/first-slice",
    }


def build_parser() -> argparse.ArgumentParser:
    defaults = default_paths()
    parser = argparse.ArgumentParser(
        description=(
            "Run the first slice: retain a logger CSV, apply Totalizer, "
            "and write one A1 Template Data File plus an audit log."
        )
    )
    parser.add_argument("--csv", type=Path, default=defaults["csv"])
    parser.add_argument("--registry", type=Path, default=defaults["registry"])
    parser.add_argument("--column-map", type=Path, default=defaults["column_map"])
    parser.add_argument("--template", type=Path, default=defaults["template"])
    parser.add_argument("--expected-headers", type=Path, default=defaults["expected_headers"])
    parser.add_argument("--out", type=Path, default=defaults["out"])
    parser.add_argument(
        "--confirm-map",
        action="store_true",
        help="Record that a person confirmed the column map.",
    )
    parser.add_argument(
        "--water-right",
        default=None,
        help="Sticky claimed water right written on every exported row.",
    )
    return parser


def summary(result: dict, registry_path: Path) -> str:
    registry = load_registry(registry_path)
    method = registry["method"]
    rows = result["rows"]
    total = 0.0
    for row in rows:
        total += float(row["VOLUME_DIVERTED_TO_USE"])
    total_text = format_measurement(total)
    return "\n".join(
        [
            f"Template Data File: {result['xlsx']}",
            f"Audit log: {result['audit']}",
            f"Raw series: {result['raw']}",
            "",
            (
                f"{len(rows)} rows for claimed water right {rows[0]['WATER_RIGHT']}. "
                f"Method: {method['name']}. "
                f"Flow rate unit is {method['outputFlowUnit']}. "
                f"Volume unit is {method['outputVolumeUnit']}. "
                f"Volume diverted to use in this file totals {total_text} {method['outputVolumeUnit']}."
            ),
            "",
            "This is a draft Template Data File. It does not submit to CalWATRS and it does not certify compliance.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.confirm_map:
        print(
            "Confirm the column map before producing a Template Data File. "
            "Check the map in the local page (python3 -m first_slice.ui) "
            "or re-run this command with --confirm-map. Nothing was exported.",
            file=sys.stderr,
        )
        return 1
    try:
        result = run_slice(
            csv_path=args.csv,
            registry_path=args.registry,
            column_map_path=args.column_map,
            template_path=args.template,
            out_dir=args.out,
            expected_headers_path=args.expected_headers,
            map_confirmed=True,
            claimed_water_right=args.water_right,
        )
    except (SliceError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(summary(result, args.registry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
