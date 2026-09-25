(function () {
  var STORAGE_KEY = "calwatrs.claimedWaterRight";
  var fixture = null;
  var csvText = "";
  var csvName = "";
  var columns = [];
  var xlsxBase64 = "";
  var xlsxName = "";

  var sticky = document.getElementById("sticky-id");
  var waterRight = document.getElementById("water-right");
  var confirmMap = document.getElementById("confirm-map");
  var runButton = document.getElementById("run-totalizer");
  var download = document.getElementById("download-xlsx");

  var screens = {
    right: document.getElementById("screen-right"),
    ingest: document.getElementById("screen-ingest"),
    export: document.getElementById("screen-export"),
  };
  var tabs = {
    right: document.getElementById("tab-right"),
    ingest: document.getElementById("tab-ingest"),
    export: document.getElementById("tab-export"),
  };

  function selectedRight() {
    return sessionStorage.getItem(STORAGE_KEY) || "";
  }

  function renderSticky() {
    var id = selectedRight();
    sticky.textContent = id || "Not selected";
    var exportLine = document.getElementById("export-right");
    if (exportLine) {
      exportLine.textContent = id
        ? "Every row in this Template Data File uses claimed water right " + id + "."
        : "Select a claimed water right before export.";
    }
    document.querySelectorAll("[data-sticky-right]").forEach(function (node) {
      node.textContent = id || "Not selected";
    });
    tabs.ingest.disabled = !id;
    updateRunEnabled();
  }

  function show(name) {
    Object.keys(screens).forEach(function (key) {
      screens[key].hidden = key !== name;
      tabs[key].setAttribute("aria-selected", key === name ? "true" : "false");
    });
    renderSticky();
  }

  function updateRunEnabled() {
    runButton.disabled = !(confirmMap.checked && selectedRight() && csvText);
  }

  function fillFacts() {
    document.getElementById("registry-blurb").textContent =
      fixture.clientName +
      " · Point of Diversion " +
      fixture.pointOfDiversion +
      " · " +
      fixture.deviceNickname +
      " · " +
      fixture.waterYear.label +
      ".";
    var facts = document.getElementById("registry-facts");
    facts.textContent = "";
    [
      ["Client", fixture.clientName],
      ["Point of Diversion", fixture.pointOfDiversion],
      ["Measurement device", fixture.deviceNickname],
      ["Measurement Device ID", fixture.measurementDeviceId + " — " + fixture.deviceNotes],
      ["Water year", fixture.waterYear.label + " (" + fixture.waterYear.start + " through " + fixture.waterYear.end + ")"],
      ["Template", "A1 — Diversion to Direct Use"],
    ].forEach(function (pair) {
      var wrap = document.createElement("div");
      var term = document.createElement("dt");
      term.textContent = pair[0];
      var detail = document.createElement("dd");
      detail.textContent = pair[1];
      wrap.appendChild(term);
      wrap.appendChild(detail);
      facts.appendChild(wrap);
    });
    if (!selectedRight()) {
      waterRight.value = fixture.claimedWaterRight;
    } else {
      waterRight.value = selectedRight();
    }
  }

  function loadCsv(text, name) {
    csvText = text;
    csvName = name;
    var lines = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n").filter(Boolean);
    columns = lines[0].split(",").map(function (cell) { return cell.trim(); });
    var head = document.getElementById("preview-head");
    var body = document.getElementById("preview-body");
    head.textContent = "";
    body.textContent = "";
    columns.forEach(function (column) {
      var th = document.createElement("th");
      th.scope = "col";
      th.textContent = column;
      head.appendChild(th);
    });
    lines.slice(1, 6).forEach(function (line) {
      var tr = document.createElement("tr");
      line.split(",").forEach(function (cell) {
        var td = document.createElement("td");
        td.textContent = cell;
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    renderMap();
    confirmMap.checked = false;
    updateRunEnabled();
  }

  function selectFor(headers, selected) {
    var select = document.createElement("select");
    headers.forEach(function (header) {
      var option = document.createElement("option");
      option.value = header;
      option.textContent = header;
      select.appendChild(option);
    });
    select.value = headers.indexOf(selected) >= 0 ? selected : headers[0];
    select.addEventListener("change", function () {
      confirmMap.checked = false;
      updateRunEnabled();
    });
    return select;
  }

  function renderMap() {
    var body = document.getElementById("map-body");
    body.textContent = "";
    var timestamp = columns.indexOf("timestamp") >= 0 ? "timestamp" : columns[0];
    var pulses = columns.indexOf("pulses") >= 0 ? "pulses" : columns[0];
    var rows = [
      ["DATE", "column", timestamp],
      ["TIME", "column", timestamp],
      ["FLOW_RATE", "column", pulses],
      ["FLOW_RATE_UNIT", "text", fixture.method.outputFlowUnit],
      ["VOLUME_DIVERTED_TO_USE", "column", pulses],
      ["VOLUME_UNIT", "text", fixture.method.outputVolumeUnit],
      ["BENEFICIAL_USE", "text", fixture.a1Defaults.BENEFICIAL_USE],
      ["WATER_RIGHT", "sticky", ""],
      ["REDIVERSION_STATUS", "text", fixture.a1Defaults.REDIVERSION_STATUS],
      ["PLACE_OF_USE", "text", fixture.a1Defaults.PLACE_OF_USE],
    ];
    rows.forEach(function (row) {
      var tr = document.createElement("tr");
      var field = document.createElement("th");
      field.scope = "row";
      field.textContent = row[0];
      var source = document.createElement("td");
      if (row[1] === "column") {
        var select = selectFor(columns, row[2]);
        select.dataset.field = row[0];
        select.setAttribute("aria-label", row[0] + " source column");
        source.appendChild(select);
      } else if (row[1] === "sticky") {
        var strong = document.createElement("strong");
        strong.dataset.stickyRight = "true";
        strong.textContent = selectedRight() || "Not selected";
        source.appendChild(strong);
        source.appendChild(document.createTextNode(" — sticky claimed water right, not a CSV column"));
      } else {
        source.textContent = row[2] + " — from the fixture registry";
      }
      tr.appendChild(field);
      tr.appendChild(source);
      body.appendChild(tr);
    });
  }

  function fieldValue(name) {
    var node = document.querySelector('[data-field="' + name + '"]');
    return node ? node.value : "";
  }

  function columnMap() {
    var timestamp = fieldValue("DATE");
    var pulses = fieldValue("FLOW_RATE");
    return {
      dialect: "sample-logger",
      timestampColumn: timestamp,
      readingColumn: pulses,
      readingKind: "pulses",
      assumption: "Each row's pulses are pulses counted in the interval ending at timestamp.",
      a1Fields: {
        DATE: fieldValue("DATE"),
        TIME: fieldValue("TIME"),
        FLOW_RATE: fieldValue("FLOW_RATE"),
        FLOW_RATE_UNIT: "registry",
        VOLUME_DIVERTED_TO_USE: fieldValue("VOLUME_DIVERTED_TO_USE"),
        VOLUME_UNIT: "registry",
        BENEFICIAL_USE: "registry",
        WATER_RIGHT: "sticky claimed water right",
        REDIVERSION_STATUS: "registry",
        PLACE_OF_USE: "registry",
      },
    };
  }

  function showIssues(messages) {
    var list = document.getElementById("run-issues");
    list.textContent = "";
    messages.forEach(function (message) {
      var item = document.createElement("li");
      item.textContent = message;
      list.appendChild(item);
    });
  }

  function renderResult(payload) {
    xlsxBase64 = payload.xlsxBase64;
    xlsxName = payload.xlsxName;
    download.disabled = false;
    var head = document.getElementById("result-head");
    var body = document.getElementById("result-body");
    head.textContent = "";
    body.textContent = "";
    payload.headers.forEach(function (header) {
      var th = document.createElement("th");
      th.scope = "col";
      th.textContent = header;
      head.appendChild(th);
    });
    var mismatched = false;
    payload.rows.forEach(function (row) {
      if (row.WATER_RIGHT !== selectedRight()) mismatched = true;
      var tr = document.createElement("tr");
      payload.headers.forEach(function (header) {
        var td = document.createElement("td");
        td.textContent = row[header];
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    var total = payload.rows.reduce(function (sum, row) {
      return sum + Number(row.VOLUME_DIVERTED_TO_USE);
    }, 0);
    document.getElementById("export-summary").textContent = mismatched
      ? "Export stopped: a row claimed water right does not match the sticky ID."
      : payload.rows.length +
        " rows for claimed water right " +
        payload.claimedWaterRight +
        ". Flow rate unit is " +
        payload.rows[0].FLOW_RATE_UNIT +
        ". Volume unit is " +
        payload.rows[0].VOLUME_UNIT +
        ". Volume diverted to use totals " +
        total +
        " " +
        payload.rows[0].VOLUME_UNIT +
        ".";
    if (mismatched) download.disabled = true;
    document.getElementById("audit-note").textContent =
      "Audit log appended at " + payload.auditPath + ". Raw series retained at " + payload.rawPath + ".";
    show("export");
  }

  document.getElementById("use-right").addEventListener("click", function () {
    var id = waterRight.value.trim();
    if (!id) return;
    sessionStorage.setItem(STORAGE_KEY, id);
    renderSticky();
    show("ingest");
  });

  document.getElementById("use-sample").addEventListener("click", function () {
    loadCsv(fixture.csvText, fixture.csvName);
  });

  document.getElementById("csv-file").addEventListener("change", function (event) {
    var file = event.target.files && event.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {
      loadCsv(String(reader.result || ""), file.name);
    };
    reader.readAsText(file);
  });

  confirmMap.addEventListener("change", updateRunEnabled);

  runButton.addEventListener("click", function () {
    showIssues([]);
    fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        claimedWaterRight: selectedRight(),
        mapConfirmed: confirmMap.checked === true,
        columnMap: columnMap(),
        csvText: csvText,
        csvName: csvName,
      }),
    }).then(function (response) {
      return response.json().then(function (payload) {
        if (!response.ok) {
          showIssues([payload.error || "Totalizer did not run"]);
          return;
        }
        renderResult(payload);
      });
    }).catch(function () {
      showIssues(["The local first-slice page could not reach its server."]);
    });
  });

  download.addEventListener("click", function () {
    if (!xlsxBase64) return;
    var binary = atob(xlsxBase64);
    var bytes = new Uint8Array(binary.length);
    for (var i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
    var url = URL.createObjectURL(new Blob([bytes], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }));
    var link = document.createElement("a");
    link.href = url;
    link.download = xlsxName;
    link.click();
    URL.revokeObjectURL(url);
  });

  Object.keys(tabs).forEach(function (key) {
    tabs[key].addEventListener("click", function () {
      show(key);
    });
  });

  renderSticky();
  fetch("/api/fixture").then(function (response) { return response.json(); }).then(function (payload) {
    fixture = payload;
    fillFacts();
    loadCsv(fixture.csvText, fixture.csvName);
    renderSticky();
  });
})();
