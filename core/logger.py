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
    "nback_N",
    "nback_total_stimuli",
    "nback_true_targets",
    "user_total_clicks",
    "pourcentage_correct_clicks",
    "pourcentage_error_clicks",
    "pourcentage_neutral_clicks",
    "avg_reaction_time_s",
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


def prepare_trial_dir(student_name, timestamp, root_dir=None):
    if root_dir is None:
        root_dir = Path(__file__).resolve().parent.parent / "data"
    else:
        root_dir = Path(root_dir)
    return _get_trial_dir(root_dir, student_name, timestamp)


def _write_csv(path, fieldnames, row):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)


def append_row(metrics, csv_path=None):
    try:
        if csv_path is not None:
            trial_dir = Path(csv_path)
            trial_dir.mkdir(parents=True, exist_ok=True)
        else:
            root_dir = Path(__file__).resolve().parent.parent / "data"
            trial_dir = _get_trial_dir(
                root_dir,
                metrics.get("student_name", "unknown"),
                metrics.get("timestamp", ""),
            )
        mission_stats = {k: metrics.get(k) for k in MISSION_FIELDNAMES}

        nback_level = metrics.get("nback_level", 0)
        total_stimuli = metrics.get("nback_total_trials", 0)
        true_targets = metrics.get("nback_targets_count", 0)
        hits = metrics.get("nback_hits", 0)
        false_alarms = metrics.get("nback_false_alarms", 0)
        total_clicks = metrics.get("nback_total_clicks", 0)
        neutral_clicks = metrics.get("nback_neutral_clicks", 0)
        reaction_times = metrics.get("nback_reaction_times", [])

        non_targets = max(0, total_stimuli - true_targets)
        correct_clicks_pct = 0.0
        if true_targets > 0:
            correct_clicks_pct = (hits / true_targets) * 100.0
        error_clicks_pct = 0.0
        if non_targets > 0:
            error_clicks_pct = (false_alarms / non_targets) * 100.0
        neutral_clicks_pct = 0.0
        if total_clicks > 0:
            neutral_clicks_pct = (neutral_clicks / total_clicks) * 100.0
        avg_reaction_time = ""
        if reaction_times:
            avg_reaction_time = sum(reaction_times) / len(reaction_times)

        nback_stats = {
            "nback_N": nback_level,
            "nback_total_stimuli": total_stimuli,
            "nback_true_targets": true_targets,
            "user_total_clicks": total_clicks,
            "pourcentage_correct_clicks": correct_clicks_pct,
            "pourcentage_error_clicks": error_clicks_pct,
            "pourcentage_neutral_clicks": neutral_clicks_pct,
            "avg_reaction_time_s": avg_reaction_time,
        }
        _write_csv(trial_dir / "mission_stats.csv", MISSION_FIELDNAMES, mission_stats)
        _write_csv(trial_dir / "nback.csv", NBACK_FIELDNAMES, nback_stats)
    except Exception as e:
        print(f"[LOGGER][ERROR] Failed to write CSV: {e}")
