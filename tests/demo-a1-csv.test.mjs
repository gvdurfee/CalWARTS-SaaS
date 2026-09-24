import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const require = createRequire(import.meta.url);
const demo = require("../demo/a1-csv.js");
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const expectedHeaders = JSON.parse(
  readFileSync(join(root, "fixtures/first-slice/expected-a1-headers.json"), "utf8")
);

test("CSV header matches the Board A1 Data columns", () => {
  assert.deepEqual(demo.A1_HEADERS, expectedHeaders);
  const csv = demo.buildA1Csv(demo.cloneDefaults());
  const header = csv.split(/\r?\n/)[0];
  assert.equal(header, expectedHeaders.join(","));
});

test("default sample rows are deterministic and non-negative", () => {
  const records = demo.buildA1Records(demo.cloneDefaults());
  assert.equal(records.length, 4);
  assert.deepEqual(
    records.map((row) => [row.DATE, row.TIME, row.FLOW_RATE, row.VOLUME_DIVERTED_TO_USE]),
    [
      ["2025-10-01", "00:00:00", "0", "0"],
      ["2025-10-01", "01:00:00", "10", "600"],
      ["2025-10-01", "02:00:00", "10", "600"],
      ["2025-10-01", "03:00:00", "0", "0"],
    ]
  );
  for (const row of records) {
    assert.equal(row.FLOW_RATE_UNIT, "GALLONS PER MINUTE");
    assert.equal(row.VOLUME_UNIT, "GALLONS");
    assert.equal(row.BENEFICIAL_USE, "irrigation");
    assert.equal(row.WATER_RIGHT, "SAMPLE-WR-001");
    assert.equal(row.REDIVERSION_STATUS, "no");
    assert.equal(row.PLACE_OF_USE, "North field");
    assert.ok(Number(row.FLOW_RATE) >= 0);
    assert.ok(Number(row.VOLUME_DIVERTED_TO_USE) >= 0);
  }
});

test("edited measurements change the CSV and reject negatives", () => {
  const state = demo.cloneDefaults();
  state.rows[1].flowGpm = -25;
  state.rows[1].volumeGallons = 1200;
  const records = demo.buildA1Records(state);
  assert.equal(records[1].FLOW_RATE, "0");
  assert.equal(records[1].VOLUME_DIVERTED_TO_USE, "1200");
  assert.equal(records[0].VOLUME_DIVERTED_TO_USE, "0");
});

test("unit switch uses only allowed Board strings", () => {
  const state = demo.cloneDefaults();
  state.flowUnit = "CUBIC FEET PER SECOND";
  state.volumeUnit = "ACRE-FEET";
  const records = demo.buildA1Records(state);
  assert.equal(records[1].FLOW_RATE_UNIT, "CUBIC FEET PER SECOND");
  assert.equal(records[1].VOLUME_UNIT, "ACRE-FEET");
  assert.equal(records[1].FLOW_RATE, demo.formatMeasurement(10 / demo.GPM_PER_CFS));
  assert.equal(records[1].VOLUME_DIVERTED_TO_USE, demo.formatMeasurement(600 / demo.GALLONS_PER_ACRE_FOOT));
  for (const row of records) {
    assert.ok(demo.FLOW_UNITS.includes(row.FLOW_RATE_UNIT));
    assert.ok(demo.VOLUME_UNITS.includes(row.VOLUME_UNIT));
    assert.ok(Number(row.FLOW_RATE) >= 0);
    assert.ok(Number(row.VOLUME_DIVERTED_TO_USE) >= 0);
  }
});

test("unknown unit strings are rejected", () => {
  const state = demo.cloneDefaults();
  state.flowUnit = "CFS";
  assert.throws(() => demo.buildA1Csv(state), /Flow rate unit/);
});

test("summary names the right, units, and demo limit", () => {
  const summary = demo.buildSummary(demo.cloneDefaults());
  assert.equal(summary.rowCount, 4);
  assert.match(summary.text, /claimed water right SAMPLE-WR-001/);
  assert.match(summary.text, /North Ditch – Sample Ranch/);
  assert.match(summary.text, /GALLONS PER MINUTE/);
  assert.match(summary.text, /1200 GALLONS/);
  assert.match(summary.text, /does not certify compliance/);
  assert.match(summary.text, /not a CalWATRS filing/);
  assert.deepEqual(summary.issues, []);
});

test("invalid DATE blocks a clean summary", () => {
  const state = demo.cloneDefaults();
  state.rows[0].date = "10/01/2025";
  const summary = demo.buildSummary(state);
  assert.equal(summary.issues.length, 1);
  assert.match(summary.issues[0], /YYYY-MM-DD/);
});
