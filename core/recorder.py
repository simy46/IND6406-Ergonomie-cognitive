import subprocess

import pygame


_FFMPEG_WARNED = False


class ScreenRecorder:
    def __init__(self, output_path, width, height, fps=30):
        self.output_path = output_path
        self.width = int(width)
        self.height = int(height)
        self.fps = int(fps)
        self.process = None
        self.active = False

    def start(self):
        global _FFMPEG_WARNED
        if self.active:
            return True
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{self.width}x{self.height}",
            "-r",
            str(self.fps),
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(self.output_path),
        ]
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.active = True
        except FileNotFoundError:
            if not _FFMPEG_WARNED:
                print("[REC][WARN] ffmpeg not found; recording disabled.")
                _FFMPEG_WARNED = True
            self.process = None
            self.active = False
        except Exception as e:
            print(f"[REC][WARN] Failed to start recorder: {e}")
            self.process = None
            self.active = False
        return self.active

    def write_frame(self, surface):
        if not self.active or self.process is None or self.process.stdin is None:
            return
        try:
            if surface.get_size() != (self.width, self.height):
                surface = pygame.transform.scale(surface, (self.width, self.height))
            frame = pygame.image.tostring(surface, "RGB")
            self.process.stdin.write(frame)
        except (BrokenPipeError, OSError):
            self.stop()
        except Exception:
            self.stop()

    def stop(self):
        if not self.active:
            return
        self.active = False
        if self.process is None:
            return
        try:
            if self.process.stdin:
                self.process.stdin.close()
            self.process.wait(timeout=2.0)
        except Exception:
            try:
                self.process.kill()
            except Exception:
                pass
        finally:
            self.process = None
