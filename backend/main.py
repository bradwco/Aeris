import argparse
import queue
import threading
from retrieval.retrieval import WebcamProducer
from face_detection.face_detection import run as face_detection_run, latest_jpeg
from computation.computation import Computation
from dotenv import load_dotenv
import os
import cv2
import numpy as np
import time

# Load environment variables (still used for width/height if present)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))

def computation_thread(bounding_box_queue, computation):
    old_box = None
    while True:
        try:
            new_box = bounding_box_queue.get(timeout=0.1)
            delta = computation.compute(old_box, new_box)
            old_box = new_box
        except queue.Empty:
            continue

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument("--device", default=0, type=int)
    args = parser.parse_args()

    frame_queue = queue.Queue(maxsize=2)
    bounding_box_queue = queue.Queue(maxsize=2)

    # Start webcam frame producer
    producer = WebcamProducer(frame_queue, device=args.device)
    producer.start()

    # Start computation thread
    computation = Computation()
    comp_thread = threading.Thread(
        target=lambda: computation_thread(bounding_box_queue, computation), 
        daemon=True
    )
    comp_thread.start()

    # Only run face detection + serve MJPEG stream locally
    face_detection_run(
        host=args.host,
        port=args.port,
        device=args.device,
        frame_queue=frame_queue,
        bounding_box_queue=bounding_box_queue
    )

if __name__ == '__main__':
    main()
