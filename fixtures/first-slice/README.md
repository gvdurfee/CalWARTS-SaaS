# First-slice fixtures

- `sample-logger.csv` — interval pulse counts. Each row’s `pulses` are the pulses counted in the interval ending at `timestamp`.
- `column-map.json` — sample dialect map (`timestamp`, `pulses`). This slice uses that config instead of a mapping screen.
- `registry.json` — one client, one claimed water right, one Point of Diversion, one measurement device, Water year 2026, and Totalizer parameters. File-backed. A database is not chosen.
- Volume per pulse: 10 GALLONS.
- Interval volume in gallons = pulses * 10.
- The first timestamp is a start mark. There is no previous timestamp, so the interval length is unknown. Volume is still pulses * 10, and flow rate is 0 only when that volume is 0. A positive volume on the first row is rejected.
- For each later row, interval minutes = this timestamp minus the previous timestamp, in minutes. Flow rate in gallons per minute = interval volume / interval minutes.
- Output units for the fixture are `GALLONS PER MINUTE` and `GALLONS`.
- `expected-a1-headers.json` — Data sheet headers from Board `template-a1.xlsx`.
