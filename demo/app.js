(function () {
  var api = window.CalwatrsDemo;
  var state = api.cloneDefaults();

  var flowUnit = document.getElementById("flow-unit");
  var volumeUnit = document.getElementById("volume-unit");
  var tbody = document.getElementById("measurement-rows");
  var summary = document.getElementById("summary");
  var download = document.getElementById("download-csv");
  var reset = document.getElementById("reset-sample");
  var issues = document.getElementById("issues");

  function fillUnitSelect(select, units, selected) {
    select.textContent = "";
    units.forEach(function (unit) {
      var option = document.createElement("option");
      option.value = unit;
      option.textContent = unit;
      select.appendChild(option);
    });
    select.value = selected;
  }

  function renderRows() {
    tbody.textContent = "";
    state.rows.forEach(function (row, index) {
      var tr = document.createElement("tr");
      tr.appendChild(cellInput(index, "date", "DATE", row.date, "date"));
      tr.appendChild(cellInput(index, "time", "TIME", row.time, "time"));
      tr.appendChild(
        cellInput(
          index,
          "flow",
          "Flow rate",
          api.formatMeasurement(api.flowFromGpm(row.flowGpm, state.flowUnit)),
          "flow"
        )
      );
      tr.appendChild(
        cellInput(
          index,
          "volume",
          "Volume diverted to use",
          api.formatMeasurement(
            api.volumeFromGallons(row.volumeGallons, state.volumeUnit)
          ),
          "volume"
        )
      );
      tbody.appendChild(tr);
    });
  }

  function cellInput(index, field, label, value, kind) {
    var td = document.createElement("td");
    td.setAttribute("data-label", label);
    var input = document.createElement("input");
    var id = "row-" + index + "-" + field;
    input.id = id;
    input.type = "text";
    input.inputMode = kind === "date" || kind === "time" ? "numeric" : "decimal";
    input.autocomplete = "off";
    input.spellcheck = false;
    input.value = value;
    input.setAttribute("aria-label", "Row " + (index + 1) + " " + label);
    input.addEventListener("change", function () {
      applyEdit(index, kind, input.value, input);
    });
    td.appendChild(input);
    return td;
  }

  function applyEdit(index, kind, raw, input) {
    var row = state.rows[index];
    if (kind === "date") {
      row.date = raw.trim();
    } else if (kind === "time") {
      row.time = raw.trim();
    } else if (kind === "flow") {
      row.flowGpm = api.gpmFromDisplay(raw, state.flowUnit);
      input.value = api.formatMeasurement(api.flowFromGpm(row.flowGpm, state.flowUnit));
    } else if (kind === "volume") {
      row.volumeGallons = api.gallonsFromDisplay(raw, state.volumeUnit);
      input.value = api.formatMeasurement(
        api.volumeFromGallons(row.volumeGallons, state.volumeUnit)
      );
    }
    refreshSummary();
  }

  function refreshSummary() {
    var report = api.buildSummary(state);
    summary.textContent = report.text;
    issues.textContent = "";
    state.rows.forEach(function (row, index) {
      var dateInput = document.getElementById("row-" + index + "-date");
      var timeInput = document.getElementById("row-" + index + "-time");
      if (dateInput) dateInput.setAttribute("aria-invalid", String(!api.isValidDate(row.date)));
      if (timeInput) timeInput.setAttribute("aria-invalid", String(!api.isValidTime(row.time)));
    });
    if (report.issues.length) {
      report.issues.forEach(function (issue) {
        var li = document.createElement("li");
        li.textContent = issue;
        issues.appendChild(li);
      });
      download.disabled = true;
    } else {
      download.disabled = false;
    }
  }

  function downloadCsv() {
    var report = api.buildSummary(state);
    if (report.issues.length) return;
    var csv = api.buildA1Csv(state);
    var blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "demo-a1-" + api.SCENARIO.waterRight + ".csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  fillUnitSelect(flowUnit, api.FLOW_UNITS, state.flowUnit);
  fillUnitSelect(volumeUnit, api.VOLUME_UNITS, state.volumeUnit);
  renderRows();
  refreshSummary();

  flowUnit.addEventListener("change", function () {
    state.flowUnit = flowUnit.value;
    renderRows();
    refreshSummary();
  });

  volumeUnit.addEventListener("change", function () {
    state.volumeUnit = volumeUnit.value;
    renderRows();
    refreshSummary();
  });

  reset.addEventListener("click", function () {
    state = api.cloneDefaults();
    flowUnit.value = state.flowUnit;
    volumeUnit.value = state.volumeUnit;
    renderRows();
    refreshSummary();
  });

  download.addEventListener("click", downloadCsv);
})();
