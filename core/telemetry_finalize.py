from core.constants import NBACK_LEVEL


class TelemetryFinalizeMixin:
    def finalize(self):
        if self.nback_task is not None:
            self.nback_task.stop(self._get_elapsed_seconds())
        mission_duration_seconds = self._get_elapsed_seconds()
        average_speed_kmh = 0.0
        if self.speed_time_total > 0:
            average_speed_kmh = self.speed_time_sum / self.speed_time_total
        lane_center_offset_mean_meters = self.route_metrics.get_mean_offset()
        percent_time_in_lane = self.route_metrics.get_percent_in_route()
        takeover_requested_value = 1 if self.takeover_requested else 0
        takeover_reaction_value = "None"
        if takeover_requested_value == 1:
            reaction = self.takeover_reaction_time_seconds
            if reaction is None and self.takeover_controller is not None:
                reaction = self.takeover_controller.get_reaction_time()
            if reaction is not None:
                takeover_reaction_value = round(reaction, 2)
        metrics = {
            "timestamp": self.timestamp,
            "student_name": self.student_name,
            "selected_mode": self.selected_mode,
            "mission_duration_seconds": round(mission_duration_seconds, 2),
            "distance_traveled_meters": round(self.distance_traveled_meters, 2),
            "average_speed_kmh": round(average_speed_kmh, 2),
            "max_speed_kmh": round(self.max_speed_kmh, 2),
            "lane_center_offset_mean_meters": round(lane_center_offset_mean_meters, 2),
            "percent_time_in_lane": round(percent_time_in_lane, 2),
            "lane_invasion_count": self.lane_invasion_count,
            "collision_count": self.collision_count,
            "collision_max_intensity": round(self.collision_max_intensity, 2),
            "manual_time_seconds": round(self.manual_time_seconds, 2),
            "auto_time_seconds": round(self.auto_time_seconds, 2),
            "mode_switch_count": self.mode_switch_count,
            "takeover_requested": takeover_requested_value,
            "takeover_reaction_time_seconds": takeover_reaction_value,
        }
        if self.nback_task is not None:
            metrics.update(self.nback_task.get_metrics())
        else:
            metrics.update(
                {
                    "nback_level": NBACK_LEVEL,
                    "nback_total_trials": 0,
                    "nback_targets_count": 0,
                    "nback_hits": 0,
                    "nback_misses": 0,
                    "nback_false_alarms": 0,
                    "nback_correct_rejections": 0,
                    "nback_total_clicks": 0,
                    "nback_neutral_clicks": 0,
                    "nback_reaction_times": [],
                }
            )
        return metrics
