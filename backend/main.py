import argparse
import queue
import threading
import atexit
from retrieval.retrieval import WebcamProducer
from face_detection.face_detection import run as face_detection_run
from computation.computation import Computation
from commands.commands import initialize_controller, send_command, get_controller


def computation_thread(bounding_box_queue, computation):
	"""Process bounding boxes through computation module and send commands to hardware"""
	
	while True:
		try:
			face_data = bounding_box_queue.get(timeout=0.1)
			if face_data is not None:
				face_box, frame_width, frame_height = face_data
				result = computation.compute(face_box, frame_width, frame_height)
				if result is not None:
					horizontal_degrees_delta, vertical_degrees_delta, actuator_inches_delta = result
					print(f"Movement: H={horizontal_degrees_delta:+.2f}°, V={vertical_degrees_delta:+.2f}°, Actuator={actuator_inches_delta:+.2f} in")
					# Send command to hardware
					send_command(horizontal_degrees_delta, vertical_degrees_delta, actuator_inches_delta)
		except queue.Empty:
			continue


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--host", default="0.0.0.0")
	parser.add_argument("--port", default=8080, type=int)
	parser.add_argument("--device", default=0, type=int)
	parser.add_argument("--horizontal-pin", default=18, type=int, help="GPIO pin for horizontal servo")
	parser.add_argument("--vertical-pin", default=19, type=int, help="GPIO pin for vertical servo")
	parser.add_argument("--actuator-pin", default=20, type=int, help="GPIO pin for linear actuator")
	parser.add_argument("--horizontal-sensitivity", default=0.5, type=float, help="Horizontal movement sensitivity (0.0-1.0)")
	parser.add_argument("--vertical-sensitivity", default=0.5, type=float, help="Vertical movement sensitivity (0.0-1.0)")
	parser.add_argument("--dead-zone", default=10.0, type=float, help="Dead zone in pixels to prevent jitter")
	parser.add_argument("--pixels-per-degree-h", default=10.0, type=float, help="Pixels per degree for horizontal servo")
	parser.add_argument("--pixels-per-degree-v", default=10.0, type=float, help="Pixels per degree for vertical servo")
	parser.add_argument("--pixels-per-inch", default=20.0, type=float, help="Pixels per inch for linear actuator")
	args = parser.parse_args()
	
	# Initialize hardware controller
	controller = initialize_controller(
		horizontal_servo_pin=args.horizontal_pin,
		vertical_servo_pin=args.vertical_pin,
		actuator_pin=args.actuator_pin
	)
	
	# Register cleanup function
	def cleanup():
		controller.cleanup()
	atexit.register(cleanup)
	
	# Create queues
	frame_queue = queue.Queue(maxsize=2)
	bounding_box_queue = queue.Queue(maxsize=2)
	
	# Create WebcamProducer from retrieval module
	producer = WebcamProducer(frame_queue, device=args.device)
	producer.start()
	
	# Create Computation instance with configuration
	computation = Computation(
		horizontal_sensitivity=args.horizontal_sensitivity,
		vertical_sensitivity=args.vertical_sensitivity,
		dead_zone=args.dead_zone,
		pixels_per_degree_horizontal=args.pixels_per_degree_h,
		pixels_per_degree_vertical=args.pixels_per_degree_v,
		pixels_per_inch=args.pixels_per_inch
	)
	
	# Start computation thread to process bounding boxes
	comp_thread = threading.Thread(
		target=lambda: computation_thread(bounding_box_queue, computation),
		daemon=True
	)
	comp_thread.start()
	
	# Start face detection with frame queue and bounding box queue
	# This will also start the HTTP server
	try:
		face_detection_run(
			host=args.host,
			port=args.port,
			device=args.device,
			frame_queue=frame_queue,
			bounding_box_queue=bounding_box_queue
		)
	except KeyboardInterrupt:
		print("\nShutting down...")
		cleanup()


if __name__ == '__main__':
	main()
