import csv
from pathlib import Path


FIELDNAMES = [
    "timestamp",
    "student_name",
    "selected_mode",
    "mission_duration_seconds",
    "distance_traveled_meters",
    "average_speed_kmh",
    "max_speed_kmh",
    "lane_center_offset_mean_meters",
    "percent_time_in_lane",
    "lane_invasion_count",
    "collision_count",
    "collision_max_intensity",
    "manual_time_seconds",
    "auto_time_seconds",
    "mode_switch_count",
    "takeover_requested",
    "takeover_reaction_time_seconds",
]


def append_row(metrics, csv_path=None):
    if csv_path is None:
        csv_path = Path(__file__).resolve().parent.parent / "missions.csv"
    else:
        csv_path = Path(csv_path)
    try:
        file_exists = csv_path.exists()
        with csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(metrics)
    except Exception as e:
        print(f"[LOGGER][ERROR] Failed to write CSV: {e}")
