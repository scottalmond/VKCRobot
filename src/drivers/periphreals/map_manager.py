#manages the map
# including visual representation, how to get back to home, etc

class MapManager:
	#limit of pan degrees
	#limit of tilt degrees
	def __init__(self):
		self.ANGLE_DEFINITION={"pan":{"minimum":50,"maximum":150,"step_depth":1,"step_sweep":1}, #degrees, step is for depth map step size
							   "tilt":{"minimum":60,"maximum":120,"step_depth":1,"sweep":90}} #sweep is setting for when sweeping left/right at fixed tilt angle degrees
		
	def append_gps_reading(self,latitude,longitude):
		pass
		
	def append_magnetic_reading(self,value):
		pass
		
	def get_last_magnetic_heading(self):
		pass
		
	#reference Arduino.py for arduino_dict structure
	def append_encoder_reading(self,arduino_dict):
		pass
		
	def get_last_encoder_reading(self):
		pass

	#is_field_scan=True when sweeping left-right only
	#False is pat+tilt to build up 3d depth map
	def append_lidar_reading(self,pan_angle_degrees,tilt_angle_degrees,distance_cm,is_depth_map):
		pass #if last reading was depth map and this one isn't, build depth map image

	#if not building 3d map
	#400x480 px
	def get_field_map_image(self):
		pass
		
	#3d map
	def get_depth_map_image(self):
		pass
