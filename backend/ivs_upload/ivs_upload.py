import os
import time
import cv2
import subprocess
import threading
import numpy as np
from dotenv import load_dotenv
from face_detection.face_detection import latest_jpeg

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

INGEST_ENDPOINT = os.getenv("IVS_INGEST_ENDPOINT")
STREAM_KEY = os.getenv("IVS_STREAM_KEY")
WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))
VIDEO_BITRATE = os.getenv("VIDEO_BITRATE", "2500k")
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")

FULL_RTMPS_URL = f"{INGEST_ENDPOINT}{STREAM_KEY}"

def build_ffmpeg_command():
    return [
        FFMPEG_BIN,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-r", "30",
        "-i", "-",
        "-timeout", "20000000",
        "-vcodec", "libx264",
        "-preset", "veryfast",
        "-tune", "zerolatency",
        "-b:v", VIDEO_BITRATE,
        "-maxrate", VIDEO_BITRATE,
        "-bufsize", "5000k",
        "-pix_fmt", "yuv420p",
        "-g", "60",
        "-an",
        "-f", "flv",
        FULL_RTMPS_URL,
        "-rtmp_transport", "tcp",
        "-rtmp_sni", "a8f10c5a7c92.global-contribute.live-video.net",
        "-flags", "low_delay"
    ]

def frame_sender(ffmpeg_proc):
    global latest_jpeg
    while True:
        if latest_jpeg is None:
            time.sleep(0.01)
            continue
        frame = cv2.imdecode(
            np.frombuffer(latest_jpeg, dtype=np.uint8),
            cv2.IMREAD_COLOR,
        )
        if frame is None:
            continue
        print("frame to IVS")
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        ffmpeg_proc.stdin.write(frame.tobytes())

def stream_forever():
    cmd = build_ffmpeg_command()
    ffmpeg_proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE
    )
    sender = threading.Thread(target=frame_sender, args=(ffmpeg_proc,), daemon=True)
    sender.start()
    ffmpeg_proc.wait()

if __name__ == "__main__":
    stream_forever()
