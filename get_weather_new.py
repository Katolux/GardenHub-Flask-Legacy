import os
import openmeteo_requests
import pandas as pd
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from datetime import datetime
from db import get_conn



def init_weather_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                date TEXT PRIMARY KEY,
                timestamp TEXT,
                temp_max REAL,
                temp_min REAL,
                precipitation REAL,
                sunshine REAL,
                daylight REAL,
                wind_max REAL,
                wind_dir REAL
            )
        """)



def save_weather_record(record):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO weather_data (
                date,
                timestamp,
                temp_max,
                temp_min,
                precipitation,
                sunshine,
                daylight,
                wind_max,
                wind_dir
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                timestamp = excluded.timestamp,
                temp_max = excluded.temp_max,
                temp_min = excluded.temp_min,
                precipitation = excluded.precipitation,
                sunshine = excluded.sunshine,
                daylight = excluded.daylight,
                wind_max = excluded.wind_max,
                wind_dir = excluded.wind_dir
            """,
            (
                record["date"],
                datetime.utcnow().isoformat(),
                record["temp_max"],
                record["temp_min"],
                record["precipitation"],
                record["sunshine"],
                record["daylight"],
                record["wind_max"],
                record["wind_dir"],
            ),
        )


def refresh_weather():
    # Portfolio privacy edit: no original installation coordinates are retained.
    latitude = os.environ.get("GARDENHUB_LATITUDE")
    longitude = os.environ.get("GARDENHUB_LONGITUDE")
    if not latitude or not longitude:
        raise RuntimeError("Set GARDENHUB_LATITUDE and GARDENHUB_LONGITUDE for live weather")

    print("\n=== REFRESH WEATHER===")

    init_weather_db()

    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    # Portfolio licensing edit: configure the existing policy via native APIs.
    adapter = HTTPAdapter(max_retries=Retry(
        total=5, read=5, connect=5, backoff_factor=0.2,
        status_forcelist=(500, 502, 504), allowed_methods=None,
    ))
    cache_session.mount("https://", adapter)
    cache_session.mount("http://", adapter)
    openmeteo = openmeteo_requests.Client(session=cache_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {

        "latitude": float(latitude),
        "longitude": float(longitude),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "sunshine_duration",
            "sunrise",
            "sunset",
            "precipitation_sum",
            "daylight_duration",
            "wind_speed_10m_max",
            "wind_direction_10m_dominant",
        ],
        "models": "best_match",
        "timezone": "UTC",
    }

    response = openmeteo.weather_api(url, params=params)[0]

    daily = response.Daily()

    temp_max = daily.Variables(0).ValuesAsNumpy()
    temp_min = daily.Variables(1).ValuesAsNumpy()
    sunshine = daily.Variables(2).ValuesAsNumpy()
    precipitation = daily.Variables(5).ValuesAsNumpy()
    daylight = daily.Variables(6).ValuesAsNumpy()
    wind_max = daily.Variables(7).ValuesAsNumpy()
    wind_dir = daily.Variables(8).ValuesAsNumpy()

    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s"),
        end=pd.to_datetime(daily.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    )

    print("\n🌤️  Daily Forecast (Formatted)")
    print("-------------------------------------------")

    for i in range(len(dates)):
        sunshine_minutes = float(sunshine[i]) / 60
        daylight_minutes = float(daylight[i]) / 60

        record = {
            "date": str(dates[i].date()),
            "temp_max": float(temp_max[i]),
            "temp_min": float(temp_min[i]),
            "precipitation": float(precipitation[i]),
            "sunshine": sunshine_minutes,
            "daylight": daylight_minutes,
            "wind_max": float(wind_max[i]),
            "wind_dir": float(wind_dir[i]),
        }

        save_weather_record(record)

        print(
            f"{record['date']} | "
            f"Max {record['temp_max']:.1f}°C | "
            f"Min {record['temp_min']:.1f}°C | "
            f"Rain {record['precipitation']:.2f} mm | "
            f"Sun {sunshine_minutes:.0f} min | "
            f"Daylight {daylight_minutes:.0f} min | "
            f"Wind max {record['wind_max']:.1f} km/h | "
            f"Dir {record['wind_dir']:.0f}°"
        )

    print("-" * 70)
    print("Weather data saved in SQLite.")
