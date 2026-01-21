import pygame
import carla


class SteeringWheel:
    def __init__(self, debug=True):
        self.debug = debug
        self._prev_buttons = {}

        pygame.joystick.init()
        count = pygame.joystick.get_count()
        print(f"[STEERING] Joystick count: {count}")

        if count == 0:
            raise RuntimeError("No steering wheel detected")

        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()

        print(f"[STEERING][OK] Device: {self.joy.get_name()}")
        print(f"[STEERING] Axes: {self.joy.get_numaxes()}")

    def _normalize_pedal(self, raw):
        return max(0.0, (1 - raw) / 2)

    def get_control(self):
        control = carla.VehicleControl()

        steer = self.joy.get_axis(0)

        accel_raw = self.joy.get_axis(1)   # pédale droite
        brake_raw = self.joy.get_axis(2)   # pédale milieu
        reverse_raw = self.joy.get_axis(3) # pédale gauche

        throttle = self._normalize_pedal(accel_raw)
        brake = self._normalize_pedal(brake_raw)
        reverse = self._normalize_pedal(reverse_raw)

        # deadzones
        steer = 0.0 if abs(steer) < 0.05 else steer
        throttle = 0.0 if throttle < 0.03 else throttle
        brake = 0.0 if brake < 0.03 else brake
        reverse = 0.0 if reverse < 0.03 else reverse

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

    def was_button_pressed(self, button_index):
        current = bool(self.joy.get_button(button_index))
        previous = self._prev_buttons.get(button_index, False)
        self._prev_buttons[button_index] = current
        return current and not previous
