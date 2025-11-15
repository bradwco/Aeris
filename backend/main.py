import argparse
import queue
import threading
from retrieval.retrieval import WebcamProducer
from face_detection.face_detection import run as face_detection_run
from computation.computation import Computation

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

    producer = WebcamProducer(frame_queue, device=args.device)
    producer.start()

    computation = Computation()
    comp_thread = threading.Thread(
        target=lambda: computation_thread(bounding_box_queue, computation),
        daemon=True
    )
    comp_thread.start()

    face_detection_run(
        host=args.host,
        port=args.port,
        device=args.device,
        frame_queue=frame_queue,
        bounding_box_queue=bounding_box_queue
    )

if __name__ == "__main__":
    main()
