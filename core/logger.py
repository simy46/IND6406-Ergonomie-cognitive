import csv
from pathlib import Path


MISSION_FIELDNAMES = [
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

NBACK_FIELDNAMES = [
    "nback_level",
    "nback_total_trials",
    "nback_targets_count",
    "nback_hits",
    "nback_misses",
    "nback_false_alarms",
    "nback_correct_rejections",
]


def _sanitize_student_name(name):
    return name.replace("/", "_").replace("\\", "_")


def _get_trial_dir(root_dir, student_name, timestamp):
    student_dir = root_dir / _sanitize_student_name(student_name)
    student_dir.mkdir(parents=True, exist_ok=True)
    time_part = "00h00"
    if timestamp and " " in timestamp:
        time_part = timestamp.split(" ", 1)[1].replace(":", "h")
    max_index = -1
    for path in student_dir.glob("trial*_*"):
        name = path.name
        if not name.startswith("trial"):
            continue
        parts = name.split("_", 1)
        if not parts:
            continue
        index_part = parts[0].replace("trial", "")
        try:
            max_index = max(max_index, int(index_part))
        except ValueError:
            continue
    next_index = max_index + 1
    if next_index <= 0:
        next_index = 1
    trial_dir = student_dir / f"trial{next_index}_{time_part}"
    trial_dir.mkdir(parents=True, exist_ok=True)
    return trial_dir


def _write_csv(path, fieldnames, row):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)


def append_row(metrics, csv_path=None):
    if csv_path is None:
        root_dir = Path(__file__).resolve().parent.parent / "data"
    else:
        root_dir = Path(csv_path)
    try:
        trial_dir = _get_trial_dir(
            root_dir,
            metrics.get("student_name", "unknown"),
            metrics.get("timestamp", ""),
        )
        mission_stats = {k: metrics.get(k) for k in MISSION_FIELDNAMES}
        nback_stats = {k: metrics.get(k) for k in NBACK_FIELDNAMES}
        _write_csv(trial_dir / "mission_stats.csv", MISSION_FIELDNAMES, mission_stats)
        _write_csv(trial_dir / "nback.csv", NBACK_FIELDNAMES, nback_stats)
    except Exception as e:
        print(f"[LOGGER][ERROR] Failed to write CSV: {e}")
