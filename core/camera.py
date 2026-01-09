import carla
import numpy as np
import pygame


class CameraRGB:
    def __init__(self, world, vehicle, width=1280, height=720):
        self.world = world
        self.vehicle = vehicle
        self.surface = None
        self.sensor = None
        self.width = int(width)
        self.height = int(height)

        self.transforms = [
            carla.Transform(carla.Location(x=0.3, z=1.2),
                            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)), # inside with steering wheel
            carla.Transform(carla.Location(x=1.3, z=1.5)),  # inside no steering wheel
            carla.Transform(carla.Location(x=-2.5, z=1.4),
                            carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)), # rear view
            carla.Transform(carla.Location(z=15.0), # from above
                            carla.Rotation(pitch=-90))
        ]
        self.index = 0

        bp = world.get_blueprint_library().find("sensor.camera.rgb")
        bp.set_attribute("image_size_x", str(self.width))
        bp.set_attribute("image_size_y", str(self.height))
        bp.set_attribute("fov", "90")

        self.bp = bp
        self._spawn()

        print("[CAMERA][OK] Camera RGB spawned")

    def _spawn(self):
        if self.sensor:
            self.sensor.destroy()

        self.sensor = self.world.spawn_actor(
            self.bp,
            self.transforms[self.index],
            attach_to=self.vehicle
        )
        self.sensor.listen(self._on_image)

    def toggle(self):
        self.index = (self.index + 1) % len(self.transforms)
        self._spawn()
        print(f"[CAMERA] Switched to view {self.index}")

    def set_resolution(self, width, height):
        width = int(width)
        height = int(height)
        if width <= 0 or height <= 0:
            return
        if width == self.width and height == self.height:
            return
        self.width = width
        self.height = height
        self.bp.set_attribute("image_size_x", str(self.width))
        self.bp.set_attribute("image_size_y", str(self.height))
        self._spawn()
        print(f"[CAMERA] Resolution set to {self.width}x{self.height}")

    def _on_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((image.height, image.width, 4))
        array = array[:, :, :3][:, :, ::-1]
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

    def render(self, screen):
        if self.surface:
            if self.surface.get_size() != screen.get_size():
                scaled = pygame.transform.scale(self.surface, screen.get_size())
                screen.blit(scaled, (0, 0))
            else:
                screen.blit(self.surface, (0, 0))

    def destroy(self):
        if self.sensor:
            self.sensor.destroy()
