import sys
from pathlib import Path
import time
import pygame
import carla
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, r"D:\CARLA\PythonAPI\carla")

from core.sim_cleanup import cleanup_simulation
from core.sim_debug import maybe_draw_debug
from core.sim_events import process_events
from core.sim_render import render_frame
from core.sim_setup import setup_world, spawn_vehicle, setup_runtime
from core.sim_step import run_mission_step
from core.sim_utils import cleanup_world_actors
from ui.pause import render_pause_screen


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("CARLA Simulator")
    camera = None
    vehicle = None
    mission_manager = None
    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(10.0)
    world, original_settings, sync_enabled, traffic_manager = setup_world(client, sync_enabled=True)
    cleanup_world_actors(world)
    vehicle = spawn_vehicle(world)
    camera, wheel, mission_manager, pause_controller = setup_runtime(client, world, vehicle)
    clock = pygame.time.Clock()
    running = True
    hud_visible = False
    try:
        while running:
            now = time.time()
            clock.tick(60)
            dt = clock.get_time() / 1000.0
            if pause_controller.telemetry is not mission_manager.telemetry:
                pause_controller.set_telemetry(mission_manager.telemetry)

            events = pygame.event.get()
            running, hud_visible, pause_clicks = process_events(
                events,
                mission_manager,
                pause_controller,
                camera,
                hud_visible,
            )

            if mission_manager.in_menu:
                if not mission_manager.run_menu(screen, clock):
                    break
            if sync_enabled and mission_manager.mission_active and not pause_controller.paused:
                try:
                    world.tick()
                except RuntimeError as e:
                    print(f"[WARN] world.tick failed: {e}")
                    sync_enabled = False
                    if traffic_manager is not None:
                        traffic_manager.set_synchronous_mode(False)

            if pause_controller.paused:
                pause_button_rect = render_pause_screen(screen)
                for pos in pause_clicks:
                    if pause_button_rect and pause_button_rect.collidepoint(pos):
                        pause_controller.resume()
                        mission_manager.reset_state_to_menu()
                pygame.display.flip()
                continue

            run_mission_step(mission_manager, wheel, dt)

            maybe_draw_debug(world, mission_manager, now)
            mission_manager.check_end()
            hud_visible = render_frame(
                screen,
                camera,
                mission_manager,
                hud_visible,
            )
            pygame.display.flip()

    finally:
        cleanup_simulation(
            mission_manager,
            camera,
            vehicle,
            world,
            sync_enabled,
            original_settings,
            traffic_manager,
        )
        pygame.quit()
        print("Exited cleanly")

if __name__ == "__main__":
    main()
