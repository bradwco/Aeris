import argparse
import queue
import threading
from retrieval.retrieval import WebcamProducer
from face_detection.face_detection import run as face_detection_run
from computation.computation import Computation


def computation_thread(bounding_box_queue, computation):
	"""Process bounding boxes through computation module"""
	old_box = None
	
	while True:
		try:
			new_box = bounding_box_queue.get(timeout=0.1)
			if new_box is not None:
				delta = computation.compute(old_box, new_box)
				if delta is not None:
					print(f"Delta coordinates: {delta}")
				old_box = new_box
		except queue.Empty:
			continue


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--host", default="0.0.0.0")
	parser.add_argument("--port", default=8080, type=int)
	parser.add_argument("--device", default=0, type=int)
	args = parser.parse_args()
	
	# Create queues
	frame_queue = queue.Queue(maxsize=2)
	bounding_box_queue = queue.Queue(maxsize=2)
	
	# Create WebcamProducer from retrieval module
	producer = WebcamProducer(frame_queue, device=args.device)
	producer.start()
	
	# Create Computation instance
	computation = Computation()
	
	# Start computation thread to process bounding boxes
	comp_thread = threading.Thread(
		target=lambda: computation_thread(bounding_box_queue, computation),
		daemon=True
	)
	comp_thread.start()
	
	# Start face detection with frame queue and bounding box queue
	# This will also start the HTTP server
	face_detection_run(
		host=args.host,
		port=args.port,
		device=args.device,
		frame_queue=frame_queue,
		bounding_box_queue=bounding_box_queue
	)


if __name__ == '__main__':
	main()
