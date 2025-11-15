"""
Hardware control module for Raspberry Pi.
Controls horizontal servo, vertical servo, and linear actuator based on face tracking errors.
"""
import time
import threading
from typing import Optional, Tuple

try:
	from gpiozero import Servo, OutputDevice
	from gpiozero.pins.pigpio import PiGPIOFactory
	GPIO_AVAILABLE = True
except ImportError:
	# Fallback for development/testing without Raspberry Pi hardware
	GPIO_AVAILABLE = False
	print("Warning: gpiozero not available. Hardware control will be simulated.")


class FanController:
	"""
	Controls the fan's servos and linear actuator based on face tracking coordinates.
	"""
	
	def __init__(
		self,
		horizontal_servo_pin: int = 18,
		vertical_servo_pin: int = 19,
		actuator_pin: int = 20,
		min_pulse_width: float = 1.0 / 1000,  # 1ms
		max_pulse_width: float = 2.0 / 1000,   # 2ms
	):
		"""
		Initialize the fan controller.
		
		Args:
			horizontal_servo_pin: GPIO pin for horizontal servo (default: 18)
			vertical_servo_pin: GPIO pin for vertical servo (default: 19)
			actuator_pin: GPIO pin for linear actuator (default: 20)
			min_pulse_width: Minimum PWM pulse width for servos (seconds)
			max_pulse_width: Maximum PWM pulse width for servos (seconds)
		"""
		self.horizontal_servo_pin = horizontal_servo_pin
		self.vertical_servo_pin = vertical_servo_pin
		self.actuator_pin = actuator_pin
		
		# Current positions (0-180 degrees for servos, inches from center for actuator)
		self.current_horizontal_angle = 90.0  # Center position
		self.current_vertical_angle = 90.0    # Center position
		self.current_actuator_position = 0.0   # Center position (inches from center)
		
		# Thread lock for thread-safe updates
		self.lock = threading.Lock()
		
		# Initialize hardware if available
		if GPIO_AVAILABLE:
			try:
				# Use pigpio factory for better servo control (requires pigpio daemon)
				# If pigpio is not available, gpiozero will fall back to default
				factory = PiGPIOFactory()
			except Exception:
				factory = None
			
			try:
				self.horizontal_servo = Servo(
					horizontal_servo_pin,
					min_pulse_width=min_pulse_width,
					max_pulse_width=max_pulse_width,
					pin_factory=factory
				)
				self.vertical_servo = Servo(
					vertical_servo_pin,
					min_pulse_width=min_pulse_width,
					max_pulse_width=max_pulse_width,
					pin_factory=factory
				)
				
				# Linear actuator control (assuming simple on/off or PWM control)
				# Adjust based on your actuator type
				self.actuator = OutputDevice(actuator_pin)
				
				# Initialize to center positions
				self._set_horizontal_angle(90.0)
				self._set_vertical_angle(90.0)
				
				print(f"Hardware initialized: H-servo={horizontal_servo_pin}, V-servo={vertical_servo_pin}, Actuator={actuator_pin}")
			except Exception as e:
				print(f"Error initializing hardware: {e}")
				print("Falling back to simulation mode.")
				self.horizontal_servo = None
				self.vertical_servo = None
				self.actuator = None
		else:
			self.horizontal_servo = None
			self.vertical_servo = None
			self.actuator = None
			print("Running in simulation mode (no hardware).")
	
	def _set_horizontal_angle(self, angle: float):
		"""
		Set horizontal servo angle (0-180 degrees).
		
		Args:
			angle: Target angle in degrees (0-180)
		"""
		angle = max(0.0, min(180.0, angle))
		self.current_horizontal_angle = angle
		
		if self.horizontal_servo is not None:
			try:
				# Convert angle (0-180) to servo value (-1 to 1)
				# 0° = -1, 90° = 0, 180° = 1
				servo_value = (angle - 90.0) / 90.0
				self.horizontal_servo.value = servo_value
			except Exception as e:
				print(f"Error setting horizontal servo: {e}")
		else:
			print(f"[SIM] Horizontal servo angle: {angle:.1f}°")
	
	def _set_vertical_angle(self, angle: float):
		"""
		Set vertical servo angle (0-180 degrees).
		
		Args:
			angle: Target angle in degrees (0-180)
		"""
		angle = max(0.0, min(180.0, angle))
		self.current_vertical_angle = angle
		
		if self.vertical_servo is not None:
			try:
				# Convert angle (0-180) to servo value (-1 to 1)
				servo_value = (angle - 90.0) / 90.0
				self.vertical_servo.value = servo_value
			except Exception as e:
				print(f"Error setting vertical servo: {e}")
		else:
			print(f"[SIM] Vertical servo angle: {angle:.1f}°")
	
	def _set_actuator_inches(self, inches_delta: float):
		"""
		Move linear actuator by a delta in inches.
		
		Args:
			inches_delta: Change in position in inches (positive = extend/up, negative = retract/down)
		"""
		self.current_actuator_position += inches_delta
		
		if self.actuator is not None:
			try:
				# Simple on/off control based on direction
				# Adjust based on your actuator type - you may need PWM or more sophisticated control
				if inches_delta > 0:
					# Move up/extend
					self.actuator.on()
					time.sleep(0.1)  # Adjust timing based on your actuator speed
					self.actuator.off()
				elif inches_delta < 0:
					# Move down/retract - you may need a second pin or reverse polarity
					# For now, this is a placeholder - adjust based on your hardware
					self.actuator.off()
			except Exception as e:
				print(f"Error setting actuator: {e}")
		else:
			print(f"[SIM] Actuator move: {inches_delta:+.2f} inches (current: {self.current_actuator_position:.2f} inches)")
	
	def update_from_computation(
		self,
		horizontal_degrees_delta: float,
		vertical_degrees_delta: float,
		actuator_inches_delta: float
	):
		"""
		Update fan position based on computed degrees and inches from computation module.
		
		Args:
			horizontal_degrees_delta: Change in degrees for horizontal servo
			vertical_degrees_delta: Change in degrees for vertical servo
			actuator_inches_delta: Change in inches for linear actuator
		"""
		with self.lock:
			# Update horizontal servo
			new_horizontal_angle = self.current_horizontal_angle + horizontal_degrees_delta
			self._set_horizontal_angle(new_horizontal_angle)
			
			# Update vertical servo
			new_vertical_angle = self.current_vertical_angle + vertical_degrees_delta
			self._set_vertical_angle(new_vertical_angle)
			
			# Update linear actuator
			self._set_actuator_inches(actuator_inches_delta)
	
	def reset_to_center(self):
		"""Reset all servos and actuator to center positions."""
		with self.lock:
			self._set_horizontal_angle(90.0)
			self._set_vertical_angle(90.0)
			self.current_actuator_position = 0.0
	
	def cleanup(self):
		"""Clean up hardware resources."""
		if self.horizontal_servo is not None:
			try:
				self.horizontal_servo.close()
			except Exception:
				pass
		
		if self.vertical_servo is not None:
			try:
				self.vertical_servo.close()
			except Exception:
				pass
		
		if self.actuator is not None:
			try:
				self.actuator.close()
			except Exception:
				pass
		
		print("Hardware resources cleaned up.")


# Global controller instance (initialized in main)
_controller: Optional[FanController] = None


def initialize_controller(**kwargs) -> FanController:
	"""
	Initialize the global fan controller.
	
	Args:
		**kwargs: Arguments to pass to FanController constructor
		
	Returns:
		Initialized FanController instance
	"""
	global _controller
	_controller = FanController(**kwargs)
	return _controller


def get_controller() -> Optional[FanController]:
	"""Get the global fan controller instance."""
	return _controller


def send_command(horizontal_degrees_delta: float, vertical_degrees_delta: float, actuator_inches_delta: float):
	"""
	Send movement command based on computed degrees and inches.
	
	Args:
		horizontal_degrees_delta: Change in degrees for horizontal servo
		vertical_degrees_delta: Change in degrees for vertical servo
		actuator_inches_delta: Change in inches for linear actuator
	"""
	global _controller
	if _controller is not None:
		_controller.update_from_computation(horizontal_degrees_delta, vertical_degrees_delta, actuator_inches_delta)
	else:
		print(f"Warning: Controller not initialized. Command: H={horizontal_degrees_delta:.2f}°, V={vertical_degrees_delta:.2f}°, A={actuator_inches_delta:.2f} in")

