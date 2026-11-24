# GardenHub — Flask Legacy

A historical Python/Flask portfolio snapshot of GardenHub's original garden-monitoring and irrigation-decision application, based on **4 May 2026**.

**This is an archived development snapshot, not the current live GardenHub platform.** The ongoing GardenHub project is maintained separately in a private repository. This repository has independent history and contains no later frontend or Planner expansion.

## Engineering objective

The original application explored an end-to-end IoT backend: receive raw soil-moisture measurements from an ESP32 sensor node, calibrate and store them, combine plant configuration with weather data, and explain a proposed watering duration through a server-rendered web interface.

The implementation demonstrates Flask routing, relational modelling, SQL repositories, sensor ingestion, rule-based decisions and operational event logging. It is a development prototype: **the code calculates recommendations and records manual watering requests; it does not actuate irrigation valves.**

## Architecture

```text
ESP32 / Arduino HTTP POST
          |
          v
Flask sensor receiver --> calibration --> SQLite
          |                                ^
          v                                |
Flask Blueprints + Jinja templates --> repositories
          ^                                ^
          |                                |
Web forms / history                 watering decision engine
                                           ^
                                           |
                              plant settings + weather records
                                           ^
                                           |
                              optional Open-Meteo forecast
```

- `app.py` initializes tables, registers routes and serves home/history pages.
- `gardenhub/routes/` separates automation, plants, sensors and watering into Blueprints.
- `repositories.py`, `db_access.py` and `system_events_repo.py` contain SQL data access.
- `db.py`, `db_schema.py` and `db_init.py` manage **SQLite**, including foreign-key checks. There is no Supabase or PostgreSQL requirement in this version.
- `python_receiver.py` and `calibration.py` implement JSON ingestion and raw-to-percentage conversion.
- `watering_decision.py` calculates duration from moisture, temperature and rainfall factors; `watering_engine.py` persists the result.
- `get_weather_new.py` and `historic_weather.py` ingest/read forecasts stored in SQLite.
- `scheduler.py` is a separate polling process with a morning decision window and periodic weather refresh. It is not an embedded Flask task queue.
- `seeding/` contains the historical JSON catalogue importer. The original catalogue data is intentionally omitted; see [provenance](docs/PROVENANCE.md).
- `templates/` and `static/` are the original Jinja views and CSS. No frontend build tool is required.

## Implemented functionality

| Area | Behavior present in the snapshot |
| --- | --- |
| Sensor ingestion | `POST /sensor_data` accepts bed, sensor and raw moisture; rejects missing/noninteger measurements; ignores air/unplugged readings; limits daily slots to six per bed. |
| Monitoring | Home, automation, bed, sensor, plant, watering and history pages. |
| Configuration | Create beds and sensors, assign sensors and plants to beds, manage rich plant records and varieties. |
| Persistence | SQLite tables for zones, beds, sensors, readings, plants, varieties, companion links, plantings, weather, decisions, watering events and system events. |
| Decision logic | Calculate and store suggested watering minutes with the individual moisture, temperature and rain multipliers. |
| Manual watering | Store an event and print a console message. This is a software-only workflow. |
| Weather | Optional Open-Meteo daily forecast retrieval, caching and upsert into SQLite. |
| Firmware | ESP32/Arduino C++ source for sampled moisture readings, scheduled HTTP posts, NTP timing and deep sleep. |

Raspberry Pi was the intended Python controller; a Pi is not needed for local inspection. The firmware targets the ESP32 Arduino environment and uses WiFi/HTTPClient and ESP sleep APIs. Hardware, firmware compilation, valve control and long-running scheduler behavior were not validated as part of preparing this repository.

## Local demo

Tested with **Python 3.12 on Windows**. Internet access is needed to install dependencies; the default demo uses synthetic data and makes no weather request. No account, API key, physical sensor or existing database is required.

From this repository directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-demo.txt
.\.venv\Scripts\python.exe -X utf8 demo.py
```

On Linux/macOS, use `python3.12 -m venv .venv`, then `.venv/bin/python` for the remaining commands.

Open [the local demo](http://127.0.0.1:5000). All initial crop, reading and weather records are **synthetic demonstration data**, not measurements from the original installation. The new `demo.py` wrapper uses a fresh temporary SQLite database and binds to loopback. Stop it with Ctrl+C; a normal shutdown discards the demo database.

Try the Beds page, the plant editor, History, and Calculate Watering under Automation. The synthetic initial reading yields a 13-minute recommendation. A manual watering request records an event only.

`demo.py`, `tests/`, `requirements-demo.txt` and this documentation were added during portfolio preparation. They are not claimed as historical features. The pinned demo requirements describe the environment resolved on 24 November 2026; they are not a reconstruction of the dependencies originally installed in May. `requirements.txt` retains the historical dependency ranges with the documented retry-library cleanup.

## Persistent local use and optional weather

For an empty, persistent SQLite database, run the historical Flask application through the CLI, restricted to loopback:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m flask --app app run --host 127.0.0.1
```

It creates the ignored `garden_system.db` beside `db.py`. With no weather location configured, the startup refresh is skipped and the empty home/history pages still render. Add your own plant records in the UI; no licensed supplier catalogue is bundled.

For optional live weather, set `GARDENHUB_LATITUDE` and `GARDENHUB_LONGITUDE` in the process environment to your chosen location before starting, then use Refresh Weather. Do not commit location configuration or the weather cache. The original installation coordinates have been removed. Live weather requires network access and is subject to [Open-Meteo's terms](https://open-meteo.com/en/terms); retain the required [weather attribution](https://open-meteo.com/) when sharing derived weather data. No real forecast dataset is included here.

For hardware exploration, copy `arduino_secrets.example.h` to the ignored `arduino_secrets.h` and set your own Wi-Fi/controller values. The example address is reserved for documentation. Local testing of the Python demo does not validate the firmware or a physical deployment.

## Validation

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

The new smoke checks exercise real Flask routes and temporary SQLite databases, including page rendering, configuration forms, ingestion limits, decision/event persistence, companion cleanup and the privacy configuration. See [validation and limitations](docs/VALIDATION.md) for scope and evidence.

## Limitations and development status

- Historical prototype, not a production service. No login, authorization, CSRF protection or hardened sensor authentication is implemented. Use loopback for the local demo.
- Irrigation recommendations are heuristic. Calibration constants and watering durations need independent validation for a real installation.
- Daily slot allocation counts readings per bed, so multiple sensors share six slots. It is not a concurrent ingestion protocol.
- Deleting a plant already referenced by planting history can still fail a SQLite foreign-key check. The May fix resolves incoming companion links, not this separate historical limitation.
- SQLite connection context managers commit/rollback but do not explicitly close handles. New demo/test helpers collect unreachable connections before temporary-directory cleanup on Windows.
- Weather access can block on network calls. The default synthetic demo avoids that path; live weather availability is not guaranteed.
- `historic_sensor.py` is an older weather-query experiment with schema mismatches. `ml_pipeline.py` explicitly contains an unfinished idea and does not match the active schema. Neither is used by the demo; there is no trained ML model.
- The original direct `python app.py` entrypoint binds to all interfaces. Use the loopback CLI/demo commands above for inspection.

## Historical provenance and publication scope

Selected source: `Katolux/GardenHub`, commit **`db37552f9dd68158004e5a2aa929af7a3b8e6eca`**, authored **4 May 2026**. February and April candidates were compared against this nearby stabilization commit using fresh databases and offline probes. The [comparison and cleanup record](docs/PROVENANCE.md) explains the choice.

Application behavior comes from this single historical tree. Privacy configuration, a small retry-dependency replacement, demo/testing helpers and documentation are explicitly identified in the [snapshot manifest](docs/SNAPSHOT_MANIFEST.json). Original Git history, private data, original photos, unverified catalogue data and operational scratch scripts are excluded.

## Licensing and third-party material

No project license existed in the selected historical tree, and no new license grant is added here. The author's project code remains under its existing copyright; public availability is for portfolio inspection. Third-party dependencies have their own licenses. No dependency source, firmware SDK, fonts, stock images or hardware photographs are vendored.

The GPL `retry-requests` wrapper was removed during preparation; the existing retry policy is configured directly using Requests/urllib3. See [third-party notices](THIRD_PARTY.md) for the dependency review and omitted material.
