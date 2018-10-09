#manages the map
# including visual representation, how to get back to home, etc

class MapManager:
	def __init__(self):
		pass
		
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
	def append_lidar_reading(self,pan_angle_degrees,tilt_angle_degrees,distance_cm,is_field_scan):
		pass

	#if not building 3d map
	def generate_field_map_image(self):
		pass
		
	#3d map
	def generate_depth_map_image(self):
		pass
