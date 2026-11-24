# Historical source selection and cleanup

Prepared on 24 November 2026 from read-only Git object exports. The private checkout, branches, deployments and databases are outside this repository's history and were not used as runtime data.

## Comparison

| Snapshot | Structure and functionality | Setup/completeness findings |
| --- | --- | --- |
| `1315e04a268010fe73cf8b8a3d433d109c743a42` — 17 February 2026 | Flask entrypoint contains most page/configuration routes; separate sensor receiver; SQLite repositories; decision engine, scheduler and ESP32 firmware. Two plant JSON files. | An offline fresh import fails on the startup weather refresh before table initialization. After manual table/fixture preparation all seven main pages and sensor ingest respond successfully. Documentation mixes project goals with incomplete hardware and ML work. |
| `0d1ef4e971d010b0235352afe457d53c5859cdf2` — 28 April 2026 | Four route Blueprints plus sensor receiver; rich plant/variety/companion model, JSON seeder and a larger catalogue; improved home dashboard and moisture percentages. | Startup errors are caught, but the home/history routes fail on a fresh offline database because weather-table initialization is missing from `init_all_tables`. Deleting an unplanted plant referenced by an incoming companion link fails a foreign-key check. Original README still describes the structure as pre-refactor. |
| **`db37552f9dd68158004e5a2aa929af7a3b8e6eca` — 4 May 2026** | Same original Flask application, before subsequent package restructuring and later frontend/Planner expansion. | Adds weather-table initialization and removes both directions of companion links during deletion. Offline fresh import, seven main page requests, sensor ingestion and deletion of an unplanted companion target pass. Selected because the actual tree resolves both demonstrated April defects without adding the later platform. |

The May tree differs from the April candidate in `db_init.py`, `repositories.py` and three documentation files. Both code changes were verified from the exported trees and probes; newer application features were not merged in.

## Retained, excluded and changed material

`SNAPSHOT_MANIFEST.json` classifies all 120 paths tracked in the selected commit, with historical SHA-256 hashes. It records each retained file, modification and exclusion. `PUBLICATION_FILES.json` enumerates the final prepared payload (excluding itself to avoid a circular hash).

- Historical application modules, Blueprints, templates, CSS, firmware and seeder are retained.
- Original README/docs are replaced with verified portfolio documentation; obsolete deployment instructions, residential context and personal biography are not carried over.
- All `dev_tests/` scratch files are excluded. They are not the smoke tests in this repository's new `tests/` directory.
- All original plant JSON files are omitted. Their redistribution permission is not established; some catalogue records name commercial supplier sources. The original seeder and catalogue UI remain available for independently supplied data.
- All original hardware photos are omitted because both redistribution provenance and private-image metadata were not established. No replacement artwork or screenshots are fabricated.
- No SQLite database, environment file, private header, certificate, key, cache, model artifact or existing Git metadata is exported into the payload.
- `get_weather_new.py`: installation coordinates become required environment configuration. No default location is retained. Missing configuration fails before network transport.
- `get_weather_new.py` and `requirements.txt`: remove the GPLv3+ `retry-requests` dependency and configure the same existing retry settings through Requests/urllib3's native APIs (five total/read/connect retries, 0.2 backoff, status codes 500/502/504, both HTTP schemes). This is a narrowly scoped licensing adaptation, not a new application capability. No implementation from the removed package is vendored.
- `arduino_send_final.cpp`: private controller destination is replaced with the host/port macros from the local header; its measurement, scheduling and transmission logic is retained.
- `arduino_secrets.example.h`: only placeholders and a reserved documentation address remain.
- `.gitignore`: expanded to prevent tracking runtime databases, local credentials, certificates and generated files.

## Additions made for inspection

The README, this provenance record, validation record, third-party notices, manifests, `demo.py`, `tests/test_snapshot.py` and resolved `requirements-demo.txt` are new portfolio preparation material. Synthetic data is created only at runtime in a fresh temporary database. These additions are not represented as work implemented in May 2026.

## Separate ongoing project

The current GardenHub application continues separately in a private repository. This snapshot is not connected to its deployment, data or original history. Public snapshot commits use the Katolux handle and a GitHub noreply address rather than copying historical author identities.
