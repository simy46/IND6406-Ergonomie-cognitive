import random


class SpatialNBackTask:
    def __init__(self, level=2, interval_seconds=5.0, total_trials=20, positions=3):
        self.level = int(level)
        self.interval_seconds = float(interval_seconds)
        self.total_trials = int(total_trials)
        self.positions = int(positions)

        self.history = []
        self.trials_presented = 0
        self.targets_count = 0
        self.hits = 0
        self.misses = 0
        self.false_alarms = 0
        self.correct_rejections = 0
        self.reaction_times = []
        self.total_clicks = 0
        self.neutral_clicks = 0

        self.current_position = None
        self.current_is_target = False
        self.current_clicked = False
        self.current_start_time = None
        self.current_reaction_time = None

        self.completed = False
        self.last_response_time = None
        self.last_response_was_target = None
        self.last_response_kind = None

    def _start_trial(self, elapsed_seconds):
        if self.trials_presented >= self.total_trials:
            self.completed = True
            return
        position = random.randrange(self.positions)
        is_target = False
        if len(self.history) >= self.level:
            is_target = position == self.history[-self.level]
        self.history.append(position)

        self.current_position = position
        self.current_is_target = is_target
        self.current_clicked = False
        self.current_start_time = elapsed_seconds
        self.current_reaction_time = None
        self.trials_presented += 1
        self.last_response_kind = None
        if is_target:
            self.targets_count += 1

    def _finalize_current_trial(self):
        if self.current_start_time is None:
            return
        if self.current_clicked:
            if self.current_is_target:
                self.hits += 1
                if self.current_reaction_time is not None:
                    self.reaction_times.append(self.current_reaction_time)
            else:
                self.false_alarms += 1
        else:
            if self.current_is_target:
                self.misses += 1
            else:
                self.correct_rejections += 1

    def update(self, elapsed_seconds, user_clicked=False):
        if self.completed:
            return
        if self.current_position is None:
            self._start_trial(elapsed_seconds)
            return
        if user_clicked:
            self.total_clicks += 1
            if not self.current_clicked:
                self.current_clicked = True
                self.last_response_time = elapsed_seconds
                self.last_response_was_target = self.current_is_target
                self.last_response_kind = "hit" if self.current_is_target else "false_alarm"
                if self.current_is_target:
                    self.current_reaction_time = elapsed_seconds - self.current_start_time
            else:
                self.last_response_time = elapsed_seconds
                self.last_response_was_target = None
                self.last_response_kind = "neutral"
                self.neutral_clicks += 1
        if (elapsed_seconds - self.current_start_time) >= self.interval_seconds:
            self._finalize_current_trial()
            if self.trials_presented >= self.total_trials:
                self.completed = True
                return
            self._start_trial(elapsed_seconds)

    def stop(self, elapsed_seconds):
        if self.completed:
            return
        if self.current_position is not None:
            self._finalize_current_trial()
        self.completed = True

    def get_metrics(self):
        return {
            "nback_level": self.level,
            "nback_total_trials": self.trials_presented,
            "nback_targets_count": self.targets_count,
            "nback_hits": self.hits,
            "nback_misses": self.misses,
            "nback_false_alarms": self.false_alarms,
            "nback_correct_rejections": self.correct_rejections,
            "nback_total_clicks": self.total_clicks,
            "nback_neutral_clicks": self.neutral_clicks,
            "nback_reaction_times": list(self.reaction_times),
        }
