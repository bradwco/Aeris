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
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = give_bounding_boxes(gray, cascade)

        for (x, y, fw, fh) in faces:
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), (0, 255, 0), 2)

        if bounding_box_queue and len(faces) > 0:
            try:
                # Choose largest face
                faces_sorted = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                bounding_box_queue.put(faces_sorted[0], block=False)
            except queue.Full:
                try:
                    bounding_box_queue.get_nowait()
                    bounding_box_queue.put(faces_sorted[0], block=False)
                except queue.Empty:
                    pass

        ret, jpg = cv2.imencode(".jpg", frame)
        if ret:
            latest_jpeg = jpg.tobytes()


class Handler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/stream":
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type",
                             "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            try:
                while True:
                    if latest_jpeg is None:
                        time.sleep(0.01)
                        continue
                    self.wfile.write(b"--jpgboundary\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(
                        f"Content-Length: {len(latest_jpeg)}\r\n\r\n".encode()
                    )
                    self.wfile.write(latest_jpeg)
                    self.wfile.write(b"\r\n")
                    time.sleep(0.05)
            except:
                return

        elif self.path.startswith("/frame"):
            if latest_jpeg is None:
                self.send_response(503)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(latest_jpeg)))
            self.end_headers()
            try:
                self.wfile.write(latest_jpeg)
            except:
                return

        elif self.path == "/info":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = {"addrs": SERVER_ADDRS, "port": SERVER_PORT}
            self.wfile.write(json.dumps(payload).encode())

        else:
            self.send_response(404)
            self.end_headers()


def run(host="0.0.0.0", port=8080, device=0, frame_queue=None, bounding_box_queue=None):
    threading.Thread(target=lambda: capture_thread(device, frame_queue, bounding_box_queue),
                     daemon=True).start()

    addrs = set(["127.0.0.1", "localhost", "192.168.137.47"])
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        addrs.add(s.getsockname()[0])
        s.close()
    except:
        pass

    for a in sorted(addrs):
        print(f"Serving stream: http://{a}:{port}/stream")
        print(f"Serving frame:  http://{a}:{port}/frame")
        print(f"Info endpoint:  http://{a}:{port}/info")

    global SERVER_ADDRS, SERVER_PORT
    SERVER_ADDRS = sorted(addrs)
    SERVER_PORT = port

    with socketserver.ThreadingTCPServer((host, port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run()
