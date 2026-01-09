import pygame
import carla


class SteeringWheel:
    def __init__(self, debug=True):
        self.debug = debug
        self.steer_deadzone = 0.05
        self.throttle_deadzone = 0.03
        self.brake_deadzone = 0.02
        self.reverse_deadzone = 0.03
        self.throttle_curve = 1.4
        self.brake_curve = 1.2
        self.brake_boost = 0.2
        self._pedal_rest = {}

        pygame.joystick.init()
        count = pygame.joystick.get_count()
        print(f"[STEERING] Joystick count: {count}")

        if count == 0:
            raise RuntimeError("No steering wheel detected")

        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()

        print(f"[STEERING][OK] Device: {self.joy.get_name()}")
        print(f"[STEERING] Axes: {self.joy.get_numaxes()}")
        self._calibrate_pedals()

    def _calibrate_pedals(self):
        self._pedal_rest = {
            "throttle": self.joy.get_axis(1),
            "brake": self.joy.get_axis(2),
            "reverse": self.joy.get_axis(3),
        }

    def _normalize_pedal(self, raw, rest_value, curve=1.0, boost=0.0):
        denom = rest_value - (-1.0)
        if abs(denom) < 1e-6:
            value = 0.0
        else:
            value = (rest_value - raw) / denom
        value = max(0.0, min(1.0, value))
        if value <= 0.0:
            return 0.0
        value = min(1.0, value + boost)
        if curve != 1.0:
            value = value ** curve
        return min(1.0, value)

    def get_control(self):
        control = carla.VehicleControl()

        steer = self.joy.get_axis(0)

        accel_raw = self.joy.get_axis(1)   # pédale droite
        brake_raw = self.joy.get_axis(2)   # pédale milieu
        reverse_raw = self.joy.get_axis(3) # pédale gauche

        throttle = self._normalize_pedal(
            accel_raw,
            self._pedal_rest.get("throttle", 1.0),
            curve=self.throttle_curve,
        )
        brake = self._normalize_pedal(
            brake_raw,
            self._pedal_rest.get("brake", 1.0),
            curve=self.brake_curve,
            boost=self.brake_boost,
        )
        reverse = self._normalize_pedal(
            reverse_raw,
            self._pedal_rest.get("reverse", 1.0),
            curve=self.throttle_curve,
        )

        # deadzones
        steer = 0.0 if abs(steer) < self.steer_deadzone else steer
        throttle = 0.0 if throttle < self.throttle_deadzone else throttle
        brake = 0.0 if brake < self.brake_deadzone else brake
        reverse = 0.0 if reverse < self.reverse_deadzone else reverse

        if reverse > 0 and throttle == 0:
            control.reverse = True
            control.throttle = reverse
            control.brake = 0.0
        else:
            control.reverse = False
            control.throttle = throttle
            control.brake = brake

        control.steer = steer
        control.hand_brake = False

        if self.debug:
            print(
                f"[STEERING] steer={steer:+.2f} | "
                f"throttle={control.throttle:.2f} | "
                f"brake={control.brake:.2f} | "
                f"reverse={control.reverse}",
                end="\r"
            )

        return control
