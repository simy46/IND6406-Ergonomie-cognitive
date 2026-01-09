import sys
from pathlib import Path
import time
import pygame
import carla

# =========================
# PATHS
# =========================
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, r"D:\CARLA\PythonAPI\carla")

from core.mission import pick_start_and_destination
from core.mission_manager import MissionManager
from core.route_visualizer import draw_route, draw_destination
from core.camera import CameraRGB
from input.steering_wheel import SteeringWheel
from ui.hud import draw_hud_message, render_hud


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("CARLA Simulator")

    # =========================
    # CARLA CONNECT
    # =========================
    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(5.0)
    world = client.get_world()

    # =========================
    # CLEANUP VEHICLES
    # =========================
    for a in world.get_actors().filter("vehicle.*"):
        a.destroy()

    # =========================
    # SPAWN VEHICLE (ONCE)
    # =========================
    blueprint = world.get_blueprint_library().find("vehicle.tesla.model3")
    vehicle = world.spawn_actor(blueprint, pick_start_and_destination(world)[0])
    vehicle.apply_control(carla.VehicleControl())
    time.sleep(0.5)

    # =========================
    # CAMERA + INPUT
    # =========================
    camera = CameraRGB(world, vehicle)
    wheel = SteeringWheel(debug=True)
    mission_manager = MissionManager(world, vehicle, wheel)

    clock = pygame.time.Clock()
    running = True

    # =========================
    # MAIN LOOP
    # =========================
    while running:
        now = time.time()
        clock.tick(60)
        dt = clock.get_time() / 1000.0

        # -------------------------
        # EVENTS
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    camera.toggle()

                elif mission_manager.mission_active and event.key == pygame.K_ESCAPE:
                    mission_manager.handle_escape()

                elif mission_manager.show_restart_prompt and event.key == pygame.K_SPACE:
                    mission_manager.reset_state_to_menu()

        # =========================
        # MISSION POPUP
        # =========================
        if mission_manager.in_menu:
            if not mission_manager.run_menu(screen, clock):
                break

        # =========================
        # RUN MODE
        # =========================
        mission_manager.run_mission_mode()
        mission_manager.update_telemetry(dt)

        # =========================
        # DEBUG DRAW (1 Hz)
        # =========================
        if mission_manager.should_draw_debug(now):
            draw_route(world, mission_manager.route)
            draw_destination(world, mission_manager.destination.location)

        # =========================
        # MISSION END CHECK
        # =========================
        mission_manager.check_end()

        # =========================
        # RENDER
        # =========================
        screen.fill((0, 0, 0))
        camera.render(screen)
        render_hud(screen, mission_manager.telemetry, mission_manager.active_drive_mode)

        if mission_manager.show_restart_prompt:
            draw_hud_message(
                screen,
                "Mission terminée – Appuyez sur [ESPACE] (ESC = toggle MANUAL/AUTO)",
                position=(80, 30),
                color=(0, 220, 255),
            )

        pygame.display.flip()

    # =========================
    # CLEAN EXIT
    # =========================
    camera.destroy()
    vehicle.destroy()
    pygame.quit()
    print("Exited cleanly")


if __name__ == "__main__":
    main()
