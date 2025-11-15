class Computation:
	def __init__(
		self,
		horizontal_sensitivity: float = 0.5,
		vertical_sensitivity: float = 0.5,
		dead_zone: float = 10.0,
		pixels_per_degree_horizontal: float = 10.0,
		pixels_per_degree_vertical: float = 10.0,
		pixels_per_inch: float = 20.0,
	):
		"""
		Initialize the computation module.
		
		Args:
			horizontal_sensitivity: Sensitivity multiplier for horizontal movement (0.0-1.0)
			vertical_sensitivity: Sensitivity multiplier for vertical movement (0.0-1.0)
			dead_zone: Pixel threshold below which no movement occurs (prevents jitter)
			pixels_per_degree_horizontal: Conversion factor from pixels to degrees for horizontal servo
			pixels_per_degree_vertical: Conversion factor from pixels to degrees for vertical servo
			pixels_per_inch: Conversion factor from pixels to inches for linear actuator
		"""
		self.horizontal_sensitivity = horizontal_sensitivity
		self.vertical_sensitivity = vertical_sensitivity
		self.dead_zone = dead_zone
		self.pixels_per_degree_horizontal = pixels_per_degree_horizontal
		self.pixels_per_degree_vertical = pixels_per_degree_vertical
		self.pixels_per_inch = pixels_per_inch
		
		# Track current positions for incremental updates
		self.current_horizontal_angle = 90.0  # Center position (0-180 degrees)
		self.current_vertical_angle = 90.0    # Center position (0-180 degrees)
		self.current_actuator_position = 0.0    # Current position in inches from center

	def compute(self, face_box, frame_width, frame_height):
		"""
		Calculate error between frame center and face center, then convert to hardware commands.
		
		Returns:
			Tuple of (horizontal_degrees_delta, vertical_degrees_delta, actuator_inches_delta)
			or None if no face detected.
			- horizontal_degrees_delta: Change in degrees for horizontal servo
			- vertical_degrees_delta: Change in degrees for vertical servo
			- actuator_inches_delta: Change in inches for linear actuator (positive = up, negative = down)
		"""
		if face_box is None:
			return None
		
		face_x, face_y, face_w, face_h = face_box
		
		# Calculate frame center
		frame_center_x = frame_width / 2
		frame_center_y = frame_height / 2
		
		# Calculate face center
		face_center_x = face_x + face_w / 2
		face_center_y = face_y + face_h / 2
		
		# Calculate error in pixels (difference between frame center and face center)
		error_x = face_center_x - frame_center_x  # Positive = face right of center
		error_y = face_center_y - frame_center_y  # Positive = face below center
		
		# Apply dead zone to prevent jitter
		if abs(error_x) < self.dead_zone:
			error_x = 0.0
		if abs(error_y) < self.dead_zone:
			error_y = 0.0
		
		# Normalize errors based on frame dimensions (convert to -1 to 1 range)
		if frame_width > 0:
			normalized_error_x = error_x / (frame_width / 2.0)
		else:
			normalized_error_x = 0.0
		
		if frame_height > 0:
			normalized_error_y = error_y / (frame_height / 2.0)
		else:
			normalized_error_y = 0.0
		
		# Apply sensitivity
		normalized_error_x *= self.horizontal_sensitivity
		normalized_error_y *= self.vertical_sensitivity
		
		# Convert normalized errors back to pixel errors for conversion
		# (after sensitivity has been applied)
		adjusted_error_x = normalized_error_x * (frame_width / 2.0) if frame_width > 0 else 0.0
		adjusted_error_y = normalized_error_y * (frame_height / 2.0) if frame_height > 0 else 0.0
		
		# Convert to degrees for horizontal servo
		# Negative error_x means face is left, so we need to rotate left (negative delta)
		horizontal_degrees_delta = -adjusted_error_x / self.pixels_per_degree_horizontal
		
		# Convert to degrees for vertical servo
		# Negative error_y means face is up, so we need to tilt up (negative delta)
		vertical_degrees_delta = -adjusted_error_y / self.pixels_per_degree_vertical
		
		# Convert to inches for linear actuator
		# Negative error_y means face is up, so we need to move up (positive delta)
		actuator_inches_delta = -adjusted_error_y / self.pixels_per_inch
		
		# Update current positions (for tracking, not used in return value)
		self.current_horizontal_angle = max(0.0, min(180.0, self.current_horizontal_angle + horizontal_degrees_delta))
		self.current_vertical_angle = max(0.0, min(180.0, self.current_vertical_angle + vertical_degrees_delta))
		self.current_actuator_position += actuator_inches_delta
		
		return (horizontal_degrees_delta, vertical_degrees_delta, actuator_inches_delta)


    
    
		
    