# Validation record

Prepared and tested on 24 November 2026 using Python 3.12 on Windows. These checks were added during portfolio preparation; they are not a claim that this test suite existed in the historical project.

## Historical comparison

Read-only exports of both requested candidates and the nearby May 4 stabilization commit were probed using separate fresh SQLite databases. Weather transport was blocked before any external request. Results are summarized in `PROVENANCE.md`.

The selected May tree starts offline, renders all seven primary pages, ingests a synthetic reading and deletes an unplanted plant referenced by an incoming companion link. The April tree demonstrably lacks offline weather-table initialization and incoming-link deletion cleanup. February requires manual setup to get past its unguarded startup weather request.

## Prepared snapshot checks

- The cleaned dependency set was installed in an isolated Python virtual environment. `pip check`: no broken requirements. `retry_requests` module: absent.
- `python -X utf8 -m unittest discover -s tests -v`: **10 tests passed**. Tests use fresh temporary SQLite files and patch `socket.socket.connect`/`connect_ex` to reject socket connections. Live weather is not requested.
- Thirteen page/static requests render successfully, covering all primary navigation plus plant create/detail/edit/variety forms and local CSS.
- Bed creation, sensor creation/assignment and plant create/edit/variety create/delete/unplanted deletion routes were exercised through Flask's real test client.
- Sensor missing/noninteger input returns 400; an air/unplugged reading returns 202; accepted readings are calibrated and stored; the seventh daily reading returns 409.
- Decision calculation persists the expected synthetic 13-minute result and 1.3 soil factor. Manual watering persists an event. No valve or relay is invoked.
- May's companion cleanup fix is exercised. A separate check confirms the documented foreign-key limitation for deleting an already planted crop; it has not been silently repaired.
- Fresh empty weather-table initialization allows home/history rendering. Missing coordinate configuration fails before weather transport.
- Native HTTP/HTTPS retry configuration is checked for the existing policy after removal of the GPL wrapper.
- The standalone demo was launched and inspected over actual loopback HTTP: home, beds, history and watering returned 200; the synthetic crop label was present. The validation process was stopped afterward.
- All retained historical files were compared against source hashes: **41 unchanged, 5 modified, 74 excluded**, out of 120 historical tracked paths. Each modification is identified in `SNAPSHOT_MANIFEST.json`.
- Source parsing and full-text privacy checks found no retained original coordinates, controller URL, personal biography or workstation paths.
- Gitleaks 8.30.1 full-tree scan with fully redacted output: no leaks found. Its official release ZIP checksum was verified. Scanning is one layer of review, not proof against every possible secret format.
- `pip-audit` checked all pinned demo dependencies on the preparation date: no known vulnerabilities reported. This is a dated advisory result, not a guarantee of future security.
- All assets and original catalogue data without verified redistribution permission were omitted. Installed dependency license metadata is recorded in `DEPENDENCIES.json`; no third-party package or firmware SDK is vendored.

## Not validated

Physical ESP32/Raspberry Pi operation, firmware compilation, sensor accuracy, valve actuation, live Open-Meteo responses, long-running scheduler behavior, multi-process ingestion, Linux/macOS installation and production deployment were not validated. Original `datetime.utcnow()` use produces a Python deprecation warning; it remains historical code.

The local demo intentionally uses synthetic weather. Real weather data is not embedded, and no claim is made that the original field deployment is still operating.

## Publication verification

The new repository is initialized independently, using a public handle/noreply identity and a parentless initial commit. Only the reviewed payload is eligible for publication. Public visibility, remote commit, tree and README are checked separately after push; this record does not itself assert a push occurred.
