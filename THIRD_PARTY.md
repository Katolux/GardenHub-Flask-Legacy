# Third-party dependency and asset review

No third-party runtime code, binary, firmware SDK, font, image or dataset is vendored in this repository. Dependencies are installed separately from Python package distributions. Their copyright notices and licenses remain in those distributions; this document does not relicense them or the project.

The historical tree contains no project LICENSE. No new project license is imposed during portfolio preparation.

## Licensing adaptation

The original weather module imported `retry-requests`. Installed version 2.0.0 identifies its license as GPLv3+ and includes the GPLv3 text; the [upstream repository](https://github.com/bustawin/retry-requests) also identifies GPL-3.0. To avoid leaving an unresolved copyleft compatibility question in an otherwise unlicensed historical project, that wrapper is not included in either published requirements file and is not imported by the cleaned source.

The existing retry policy is configured using the public Requests `HTTPAdapter` and urllib3 `Retry` APIs. See [Requests retry documentation](https://requests.readthedocs.io/en/latest/user/advanced/#example-automatic-retries) and [urllib3's Retry API](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry). The preparation tests check the retained retry configuration and a fresh environment is checked for absence of `retry_requests`.

## Installed dependency license families

License information was read from the installed distributions resolved for `requirements-demo.txt` on 24 November 2026. `docs/DEPENDENCIES.json` records every installed runtime distribution/version and its license metadata. These are the resolved validation versions, not historical version claims.

- Flask, Werkzeug, Jinja2, MarkupSafe, click, itsdangerous and pandas: BSD family.
- Requests, niquests, flatbuffers and tzdata: Apache-2.0 family.
- Open-Meteo client/SDK, requests-cache, urllib3 and supporting packages: MIT/BSD or other permissive licenses, as recorded in the inventory.
- certifi: MPL-2.0; installed separately and not modified or vendored.
- NumPy: compound BSD/0BSD/MIT/Zlib/CC0 license expression in the resolved package.
- typing_extensions: PSF-2.0.

Dependency installation does not mean those packages are copied into this source snapshot. Consult their included license texts before redistributing an environment or binaries. No unresolved asset permission issue is carried into the prepared payload: all unverified catalogue data and photos have been excluded.

## Firmware and weather

`arduino_send_final.cpp` includes APIs from the external ESP32 Arduino platform. That platform and its WiFi/HTTPClient/ESP components must be obtained separately under their own licenses. No Arduino/ESP SDK files or firmware binaries are distributed here.

[Open-Meteo](https://open-meteo.com/) is an external optional weather service, not bundled weather data. Consult its [terms](https://open-meteo.com/en/terms) before live use or redistribution of obtained data. The demo uses newly created synthetic values, not an API response.

## Artwork and catalogue

Only original template/CSS source and Unicode text are included; system fonts are referenced without bundling font files. Original photos and plant JSON data were excluded because redistribution rights were not established. No external stock artwork, screenshots or commercial catalogue text is included.
