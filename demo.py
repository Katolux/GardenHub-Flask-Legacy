"""New portfolio helper: synthetic, temporary data around the historical application."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gc
import tempfile


def prepare_demo(database_path):
    """Create a fresh synthetic database; refuse to overwrite an existing file."""
    import db
    db.DB_PATH = Path(database_path).resolve()
    if db.DB_PATH.exists():
        raise FileExistsError("The demo requires a new database path")

    from db_init import init_all_tables
    from get_weather_new import save_weather_record
    from repositories import (
        add_bed, add_sensor, assign_plant_to_bed,
        assign_sensor_to_bed, insert_rich_plant, save_reading,
    )
    init_all_tables()
    insert_rich_plant({
        "plant_id": "demo_crop", "name": "Demo crop (synthetic)",
        "category": "demo", "family": "Synthetic", "water_need_overall": "medium",
        "root_depth_min_cm": 20, "root_depth_max_cm": 40,
        "min_moisture": 50, "max_moisture": 70, "base_minutes": 10,
        "soil_json": {}, "calendar_json": {}, "nutrition_json": {}, "care_json": {},
        "plant_json": {},
    })
    add_bed("demo_bed")
    add_sensor("demo_sensor")
    assign_sensor_to_bed("demo_sensor", "demo_bed")
    assign_plant_to_bed("demo_bed", "demo_crop", quantity=1)
    save_reading("demo_bed", "demo_sensor", 1, 1800, 25)
    save_weather_record({
        "date": datetime.now(timezone.utc).date().isoformat(),
        "temp_max": 22.0, "temp_min": 12.0, "precipitation": 0.0,
        "sunshine": 300.0, "daylight": 700.0, "wind_max": 5.0, "wind_dir": 180.0,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="gardenhub-portfolio-") as directory:
        prepare_demo(Path(directory) / "demo.db")
        from app import app
        print("Historical GardenHub demo: all displayed crop/weather/readings are synthetic.")
        print("Temporary database is discarded when this process exits normally.")
        try:
            app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)
        finally:
            # The historical connection helper relies on object cleanup to close SQLite.
            gc.collect()


if __name__ == "__main__":
    main()
