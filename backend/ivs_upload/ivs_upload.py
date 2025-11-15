import os
import time
import cv2
import subprocess
import threading
import queue
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

INGEST_ENDPOINT = os.getenv("IVS_INGEST_ENDPOINT")
STREAM_KEY = os.getenv("IVS_STREAM_KEY")
WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))
VIDEO_BITRATE = os.getenv("VIDEO_BITRATE", "2500k")
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")

FULL_RTMPS_URL = f"{INGEST_ENDPOINT}{STREAM_KEY}"

class IVSUploader:
    def __init__(self, frame_queue, width=WIDTH, height=HEIGHT, bitrate=VIDEO_BITRATE):
        self.frame_queue = frame_queue
        self.width = width
        self.height = height
        self.bitrate = bitrate
        self.ffmpeg_proc = None
        self.running = False

    def build_ffmpeg_command(self):
        """Amazon IVS verified FFmpeg command"""
        return [
            FFMPEG_BIN,
            "-f", "rawvideo",
            "-pix_fmt", "yuv420p",   # match converted CV input!
            "-s", f"{self.width}x{self.height}",
            "-r", "30",
            "-i", "-",

            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-b:v", self.bitrate,
            "-maxrate", self.bitrate,
            "-bufsize", "5000k",
            "-g", "60",
            "-an",

            "-f", "flv",
            FULL_RTMPS_URL,
        ]

    def log_ffmpeg_errors(self):
        while self.running and self.ffmpeg_proc and self.ffmpeg_proc.stderr:
            line = self.ffmpeg_proc.stderr.readline().decode(errors="ignore").strip()
            if line:
                print("FFmpeg:", line)

    def restart_ffmpeg(self):
        print("🚨 Restarting FFmpeg...")
        if self.ffmpeg_proc:
            try:
                self.ffmpeg_proc.terminate()
                self.ffmpeg_proc.wait(timeout=2)
            except:
                self.ffmpeg_proc.kill()

        cmd = self.build_ffmpeg_command()
        self.ffmpeg_proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        threading.Thread(target=self.log_ffmpeg_errors, daemon=True).start()

    def frame_sender(self):
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if frame is None:
                continue

            # Ensure correct size
            if frame.shape[1] != self.width or frame.shape[0] != self.height:
                frame = cv2.resize(frame, (self.width, self.height))

            # Convert BGR -> YUV420 (strict format Amazon IVS expects)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)

            # Check FFmpeg process still alive
            if self.ffmpeg_proc.poll() is not None:
                print("⚠ FFmpeg exited unexpectedly")
                self.restart_ffmpeg()
                continue

            try:
                self.ffmpeg_proc.stdin.write(frame.tobytes())
            except (BrokenPipeError, OSError):
                print("❌ FFmpeg pipe broken during write")
                self.restart_ffmpeg()

    def start(self):
        if self.running:
            return

        print("Starting IVS uploader...")
        self.running = True
        self.restart_ffmpeg()
        threading.Thread(target=self.frame_sender, daemon=True).start()
        print(f"✓ Streaming → {FULL_RTMPS_URL}")

    def stop(self):
        print("Stopping IVS uploader...")
        self.running = False
        if self.ffmpeg_proc:
            try:
                self.ffmpeg_proc.terminate()
                self.ffmpeg_proc.wait(timeout=2)
            except:
                self.ffmpeg_proc.kill()

if __name__ == "__main__":
    # Quick test mode
    test_queue = queue.Queue(maxsize=1)
    uploader = IVSUploader(test_queue)
    uploader.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        uploader.stop()
