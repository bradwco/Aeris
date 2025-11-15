import threading
import time
import cv2
import queue
from retrieval.retrieval import WebcamProducer

def give_bounding_boxes(gray, cascade):
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

def detect_faces(device=0, frame_queue=None, bounding_box_queue=None, output_frame_queue=None):
    """
    Detect faces in frames and pass processed frames to output queue for IVS streaming.
    
    Args:
        device: Webcam device index
        frame_queue: Input queue of frames from retrieval
        bounding_box_queue: Output queue of bounding boxes for computation
        output_frame_queue: Output queue of processed frames for IVS upload
    """
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    if frame_queue is None:
        frame_queue = queue.Queue(maxsize=2)
        producer = WebcamProducer(frame_queue, device=device)
        producer.start()

    while True:
        try:
            frame = frame_queue.get(timeout=0.1)
        except queue.Empty:
            time.sleep(0.01)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = give_bounding_boxes(gray, cascade)

        for (x, y, fw, fh) in faces:
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), (0, 255, 0), 2)

        if bounding_box_queue and len(faces) > 0:
            try:
                faces_sorted = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                bounding_box_queue.put(faces_sorted[0], block=False)
            except queue.Full:
                try:
                    bounding_box_queue.get_nowait()
                    bounding_box_queue.put(faces_sorted[0], block=False)
                except queue.Empty:
                    pass

        if output_frame_queue:
            try:
                output_frame_queue.put(frame, block=False)
            except queue.Full:
                try:
                    output_frame_queue.get_nowait()
                    output_frame_queue.put(frame, block=False)
                except queue.Empty:
                    pass

if __name__ == "__main__":
    detect_faces()
