import threading
import time
import queue
import cv2


class WebcamProducer(threading.Thread):
	def __init__(self, frame_queue, device=0, width=None, height=None):
		super().__init__(daemon=True)
		self.device = device
		self.frame_queue = frame_queue
		self._stop = threading.Event()
		self.width = width
		self.height = height

	def stop(self):
		self._stop.set()

	def run(self):
		cap = cv2.VideoCapture(self.device)
		if not cap.isOpened():
			print(f"Unable to open webcam device {self.device}")
			return
		if self.width:
			cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
		if self.height:
			cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

		try:
			while not self._stop.is_set():
				ret, frame = cap.read()
				if not ret:
					time.sleep(0.01)
					continue
				try:
					self.frame_queue.put(frame, block=False)
				except queue.Full:
					try:
						_ = self.frame_queue.get_nowait()
					except queue.Empty:
						pass
					try:
						self.frame_queue.put(frame, block=False)
					except queue.Full:
						pass
		finally:
			cap.release()

