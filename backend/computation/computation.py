import os
import dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

FRAME_WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
FRAME_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))

PIXELS_PER_DEG_X = 10
PIXELS_PER_DEG_Y = 10
DEG_PER_INCH = 10

def compute_rotation(bounding_box):
	box_x, box_y, box_w, box_h = bounding_box

	box_cx = x + (box_w / 2)
	box_cy = y + (box_h / 2)

	frame_cx = FRAME_WIDTH / 2
	frame_cy = FRAME_HEIGHT / 2

	error_x = box_cx - frame_cx
	error_y = box_cy - frame_cy

	delta_deg_x = error_x / PIXELS_PER_DEG_X
	delta_deg_y = error_y / PIXELS_PER_DEG_Y

	return delta_deg_x, delta_deg_y
	
def compute_linear(deg_y):
	delta_inches = deg_y / DEG_PER_INCH
	return delta_inches
