/*
 * Demo A1 CSV builder. Browser global and Node CommonJS.
 * Canonical storage is gallons and gallons per minute.
 * Export uses Board unit strings only.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.CalwatrsDemo = factory();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  var A1_HEADERS = [
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
  ];

  var FLOW_UNITS = ["CUBIC FEET PER SECOND", "GALLONS PER MINUTE"];
  var VOLUME_UNITS = ["GALLONS", "ACRE-FEET"];

  // 1 ft³ = 7.4805194805 US gal; × 60 s = gallons per minute in 1 cubic foot per second.
  var GPM_PER_CFS = 448.83116883;
  // Common water-rights conversion: 1 acre-foot = 325,851 gallons.
  var GALLONS_PER_ACRE_FOOT = 325851;

  var SCENARIO = {
    clientName: "Sample Irrigation Client",
    scenarioName: "North Ditch – Sample Ranch",
    waterRight: "SAMPLE-WR-001",
    templateLabel: "A1",
    templateLong: "Diversion to Direct Use",
    pod: "POD North Ditch",
    deviceNickname: "North ditch magnetic meter",
    deviceId: "M0SAMPLE1",
    waterYear: "Water year 2026",
    beneficialUse: "irrigation",
    placeOfUse: "North field",
    rediversionStatus: "no",
    volumePerPulseGallons: 10,
  };

  // Pulses in the interval ending at each timestamp × 10 gallons.
  // First row is the start mark (no prior interval). Later rows are 60 minutes.
  var DEFAULT_ROWS = [
    { date: "2025-10-01", time: "00:00:00", flowGpm: 0, volumeGallons: 0 },
    { date: "2025-10-01", time: "01:00:00", flowGpm: 10, volumeGallons: 600 },
    { date: "2025-10-01", time: "02:00:00", flowGpm: 10, volumeGallons: 600 },
    { date: "2025-10-01", time: "03:00:00", flowGpm: 0, volumeGallons: 0 },
  ];

  function cloneDefaults() {
    return {
      flowUnit: "GALLONS PER MINUTE",
      volumeUnit: "GALLONS",
      rows: DEFAULT_ROWS.map(function (row) {
        return {
          date: row.date,
          time: row.time,
          flowGpm: row.flowGpm,
          volumeGallons: row.volumeGallons,
        };
      }),
    };
  }

  function clampNonNegative(value) {
    var n = typeof value === "number" ? value : Number(String(value).trim());
    if (!isFinite(n) || n < 0) return 0;
    return n;
  }

  function formatMeasurement(value) {
    var n = clampNonNegative(value);
    var text = n.toFixed(6).replace(/\.?0+$/, "");
    return text === "" ? "0" : text;
  }

  function flowFromGpm(gpm, unit) {
    var safe = clampNonNegative(gpm);
    if (unit === "CUBIC FEET PER SECOND") return safe / GPM_PER_CFS;
    return safe;
  }

  function volumeFromGallons(gallons, unit) {
    var safe = clampNonNegative(gallons);
    if (unit === "ACRE-FEET") return safe / GALLONS_PER_ACRE_FOOT;
    return safe;
  }

  function gpmFromDisplay(display, unit) {
    var safe = clampNonNegative(display);
    if (unit === "CUBIC FEET PER SECOND") return safe * GPM_PER_CFS;
    return safe;
  }

  function gallonsFromDisplay(display, unit) {
    var safe = clampNonNegative(display);
    if (unit === "ACRE-FEET") return safe * GALLONS_PER_ACRE_FOOT;
    return safe;
  }

  function csvCell(value) {
    var text = String(value);
    if (/[",\r\n]/.test(text)) {
      return '"' + text.replace(/"/g, '""') + '"';
    }
    return text;
  }

  function assertUnit(value, allowed, label) {
    if (allowed.indexOf(value) === -1) {
      throw new Error(label + " must be one of: " + allowed.join(", "));
    }
  }

  function isValidDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    var parts = value.split("-");
    var year = Number(parts[0]);
    var month = Number(parts[1]);
    var day = Number(parts[2]);
    var date = new Date(Date.UTC(year, month - 1, day));
    return (
      date.getUTCFullYear() === year &&
      date.getUTCMonth() === month - 1 &&
      date.getUTCDate() === day
    );
  }

  function isValidTime(value) {
    return /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/.test(value);
  }

  function normalizeState(input) {
    var source = input || cloneDefaults();
    assertUnit(source.flowUnit, FLOW_UNITS, "Flow rate unit");
    assertUnit(source.volumeUnit, VOLUME_UNITS, "Volume unit");
    if (!source.rows || !source.rows.length) {
      throw new Error("At least one measurement row is required");
    }
    return {
      flowUnit: source.flowUnit,
      volumeUnit: source.volumeUnit,
      rows: source.rows.map(function (row) {
        return {
          date: String(row.date || ""),
          time: String(row.time || ""),
          flowGpm: clampNonNegative(row.flowGpm),
          volumeGallons: clampNonNegative(row.volumeGallons),
        };
      }),
    };
  }

  function rowIssues(state) {
    var issues = [];
    state.rows.forEach(function (row, index) {
      var label = "Row " + (index + 1);
      if (!isValidDate(row.date)) {
        issues.push(label + " DATE must be YYYY-MM-DD");
      }
      if (!isValidTime(row.time)) {
        issues.push(label + " TIME must be hh:mm:ss");
      }
    });
    return issues;
  }

  function buildA1Records(input) {
    var state = normalizeState(input);
    return state.rows.map(function (row) {
      return {
        DATE: row.date,
        TIME: row.time,
        FLOW_RATE: formatMeasurement(flowFromGpm(row.flowGpm, state.flowUnit)),
        FLOW_RATE_UNIT: state.flowUnit,
        VOLUME_DIVERTED_TO_USE: formatMeasurement(
          volumeFromGallons(row.volumeGallons, state.volumeUnit)
        ),
        VOLUME_UNIT: state.volumeUnit,
        BENEFICIAL_USE: SCENARIO.beneficialUse,
        WATER_RIGHT: SCENARIO.waterRight,
        REDIVERSION_STATUS: SCENARIO.rediversionStatus,
        PLACE_OF_USE: SCENARIO.placeOfUse,
      };
    });
  }

  function buildA1Csv(input) {
    var records = buildA1Records(input);
    var lines = [A1_HEADERS.join(",")];
    records.forEach(function (record) {
      lines.push(
        A1_HEADERS.map(function (header) {
          return csvCell(record[header]);
        }).join(",")
      );
    });
    return lines.join("\r\n") + "\r\n";
  }

  function buildSummary(input) {
    var state = normalizeState(input);
    var issues = rowIssues(state);
    var totalGallons = state.rows.reduce(function (sum, row) {
      return sum + row.volumeGallons;
    }, 0);
    var totalText = formatMeasurement(
      volumeFromGallons(totalGallons, state.volumeUnit)
    );
    var text =
      "This demo output has " +
      state.rows.length +
      " rows for claimed water right " +
      SCENARIO.waterRight +
      " (" +
      SCENARIO.scenarioName +
      "). Flow rate unit is " +
      state.flowUnit +
      ". Volume unit is " +
      state.volumeUnit +
      ". Volume diverted to use in this sample totals " +
      totalText +
      " " +
      state.volumeUnit +
      ". This is a prototype demo, not a CalWATRS filing, and it does not certify compliance.";
    if (issues.length) {
      text += " Fix the highlighted DATE or TIME values before download. " + issues.join(". ") + ".";
    }
    return {
      rowCount: state.rows.length,
      waterRight: SCENARIO.waterRight,
      scenarioName: SCENARIO.scenarioName,
      flowUnit: state.flowUnit,
      volumeUnit: state.volumeUnit,
      totalVolume: totalText,
      issues: issues,
      text: text,
    };
  }

  return {
    A1_HEADERS: A1_HEADERS,
    FLOW_UNITS: FLOW_UNITS,
    VOLUME_UNITS: VOLUME_UNITS,
    GPM_PER_CFS: GPM_PER_CFS,
    GALLONS_PER_ACRE_FOOT: GALLONS_PER_ACRE_FOOT,
    SCENARIO: SCENARIO,
    cloneDefaults: cloneDefaults,
    clampNonNegative: clampNonNegative,
    formatMeasurement: formatMeasurement,
    flowFromGpm: flowFromGpm,
    volumeFromGallons: volumeFromGallons,
    gpmFromDisplay: gpmFromDisplay,
    gallonsFromDisplay: gallonsFromDisplay,
    isValidDate: isValidDate,
    isValidTime: isValidTime,
    normalizeState: normalizeState,
    rowIssues: rowIssues,
    buildA1Records: buildA1Records,
    buildA1Csv: buildA1Csv,
    buildSummary: buildSummary,
  };
});
