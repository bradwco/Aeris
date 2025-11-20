import argparse
import queue
import threading
from retrieval.retrieval import WebcamProducer
from face_detection.face_detection import detect_faces
from ivs_upload.ivs_upload import IVSUploader
from websocket.websocket import WebSocket
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))

def computation_thread(bounding_box_queue, computation):
    """Process bounding boxes and compute movement."""
    old_box = None
    while True:
        try:
            new_box = bounding_box_queue.get(timeout=0.1)
            delta = computation.compute(old_box, new_box)
            if delta:
                print(f"Movement detected: {delta}")
            old_box = new_box
        except queue.Empty:
            continue

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=0, type=int, help="Webcam device index")
    args = parser.parse_args()

    frame_queue = queue.Queue(maxsize=2)
    bounding_box_queue = queue.Queue(maxsize=2)
    ivs_frame_queue = queue.Queue(maxsize=2)

    socket = WebSocket("0.0.0.0", 8080)

    print("Starting Aeris Pipeline (Pure IVS Mode)")
    print("Retrieval → Face Detection → IVS Upload")
    print()

    print("Starting webcam retrieval...")
    producer = WebcamProducer(frame_queue, device=args.device)
    producer.start()

    print("Starting face detection...")
    face_thread = threading.Thread(
        target=lambda: detect_faces(
            device=args.device,
            frame_queue=frame_queue,
            bounding_box_queue=bounding_box_queue,
            output_frame_queue=ivs_frame_queue
        ),
        daemon=True
    )
    face_thread.start()

    print("Starting IVS uploader...")
    uploader = IVSUploader(ivs_frame_queue, width=WIDTH, height=HEIGHT)
    uploader.start()

    print()
    print("Pipeline started successfully!")
    print("Frames are being streamed to IVS")
    print("Pull playback URL from IVS console")
    print()

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping pipeline...")
        uploader.stop()
        producer.stop()
        print("Pipeline stopped")

if __name__ == "__main__":
    main()
