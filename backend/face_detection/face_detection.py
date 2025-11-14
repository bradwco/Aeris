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
	
	# Create frame queue and producer if not provided
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
		target_w = 320
		scale = 1.0
		if w > target_w:
			scale = target_w / float(w)
			small = cv2.resize(frame, (int(w * scale), int(h * scale)))
		else:
			small = frame
		gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
		faces = give_bounding_boxes(gray, cascade)
		
		# Scale bounding boxes back to original frame size and send to queue
		scaled_faces = []
		for (x, y, fw, fh) in faces:
			if scale != 1.0:
				x = int(x / scale)
				y = int(y / scale)
				fw = int(fw / scale)
				fh = int(fh / scale)
			scaled_faces.append((x, y, fw, fh))
			cv2.rectangle(frame, (x, y), (x + fw, y + fh), (0, 255, 0), 2)
		
		# Send bounding boxes to queue if provided (send first/largest face)
		if bounding_box_queue is not None and len(scaled_faces) > 0:
			# Get the largest face (by area)
			largest_face = max(scaled_faces, key=lambda f: f[2] * f[3])
			try:
				bounding_box_queue.put(largest_face, block=False)
			except queue.Full:
				try:
					_ = bounding_box_queue.get_nowait()
					bounding_box_queue.put(largest_face, block=False)
				except queue.Empty:
					pass
		
		ret2, jpg = cv2.imencode('.jpg', frame)
		if not ret2:
			continue
		latest_jpeg = jpg.tobytes()

class Handler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/stream':
			self.send_response(200)
			self.send_header('Age', '0')
			self.send_header('Cache-Control', 'no-cache, private')
			self.send_header('Pragma', 'no-cache')
			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			try:
				while True:
					if latest_jpeg is None:
						time.sleep(0.01)
						continue
					self.wfile.write(b"--jpgboundary\r\n")
					self.wfile.write(b"Content-Type: image/jpeg\r\n")
					self.wfile.write(f"Content-Length: {len(latest_jpeg)}\r\n\r\n".encode())
					self.wfile.write(latest_jpeg)
					self.wfile.write(b"\r\n")
					time.sleep(0.03)
			except Exception:
				return
		elif self.path == '/frame':
			if latest_jpeg is None:
				self.send_response(503)
				self.end_headers()
				return
			self.send_response(200)
			self.send_header('Content-Type', 'image/jpeg')
			self.send_header('Content-Length', str(len(latest_jpeg)))
			self.end_headers()
			try:
				self.wfile.write(latest_jpeg)
			except Exception:
				return
		elif self.path == '/info':
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			payload = {"addrs": SERVER_ADDRS, "port": SERVER_PORT}
			try:
				self.wfile.write(json.dumps(payload).encode())
			except Exception:
				return
		else:
			self.send_response(404)
			self.end_headers()



def run(host='0.0.0.0', port=8080, device=0, frame_queue=None, bounding_box_queue=None):
	t = threading.Thread(target=lambda: capture_thread(device, frame_queue, bounding_box_queue), daemon=True)
	t.start()
	addrs = set()
	addrs.add('127.0.0.1')
	addrs.add('localhost')
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.connect(("8.8.8.8", 80))
		addrs.add(sock.getsockname()[0])
		sock.close()
	except Exception:
		pass
	try:
		infos = socket.getaddrinfo(socket.gethostname(), None)
		for info in infos:
			addr = info[4][0]
			if '.' in addr and not addr.startswith('127.'):
				addrs.add(addr)
	except Exception:
		pass
	for a in sorted(addrs):
		print(f"Serving stream at http://{a}:{port}/stream")
	global SERVER_ADDRS, SERVER_PORT
	SERVER_ADDRS = sorted(addrs)
	SERVER_PORT = port
	with socketserver.ThreadingTCPServer((host, port), Handler) as httpd:
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			pass


if __name__ == '__main__':
	run()

# To access the info endpoint, use the following curl command:
# curl http://<your-machine-ip>:8080/info
