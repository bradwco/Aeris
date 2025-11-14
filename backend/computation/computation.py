

class Computation:
	def __init__(self):
		pass

	def compute(self, old_box, new_box):
		if old_box is None or new_box is None:
			return None
		old_x, old_y, old_w, old_h = old_box
		new_x, new_y, new_w, new_h = new_box
		old_center_x = old_x + old_w / 2
		old_center_y = old_y + old_h / 2
		new_center_x = new_x + new_w / 2
		new_center_y = new_y + new_h / 2
		delta_coords = (new_center_x - old_center_x, new_center_y - old_center_y)
		return delta_coords
    
    
		
    