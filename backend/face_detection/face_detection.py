from http import server
import socketserver
import threading
import time
import cv2
import socket
import json
import queue
from retrieval.retrieval import WebcamProducer

latest_jpeg = None
SERVER_ADDRS = []
SERVER_PORT = 8080

def give_bounding_boxes(gray, cascade):
    return cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))

def capture_thread(device=0, frame_queue=None, bounding_box_queue=None):
    global latest_jpeg
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

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = give_bounding_boxes(gray, cascade)

        if len(faces) > 0:
            # largest face
            (x, y, fw, fh) = max(faces, key=lambda f: f[2]*f[3])
            cv2.rectangle(frame, (x,y), (x+fw, y+fh), (0,255,0), 2)

            face_data = ((x,y,fw,fh), w, h)
            try:
                bounding_box_queue.put(face_data, block=False)
            except queue.Full:
                try:
                    _ = bounding_box_queue.get_nowait()
                    bounding_box_queue.put(face_data, block=False)
                except queue.Empty:
                    pass

        ret, jpg = cv2.imencode(".jpg", frame)
        if ret:
            latest_jpeg = jpg.tobytes()
