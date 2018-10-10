#manages the map
# including visual representation, how to get back to home, etc

import numpy as np
import cv2
import time

class MapManager:
	#limit of pan degrees
	#limit of tilt degrees
	def __init__(self,camera_server):
		self.ANGLE_DEFINITION={"pan":{"minimum":65,"maximum":135,"step_depth":1,"step_sweep":1}, #degrees, step is for depth map step size
							   "tilt":{"minimum":40,"maximum":110,"step_depth":1,"sweep":90}} #sweep is setting for when sweeping left/right at fixed tilt angle degrees
		self.DEPTH_MAP_INDEX_OFFSET=6 #readings come in later than reported, so they're processed with an offset
		self.FIELD_MAP_DELAY_SECONDS=2 #seconds between map generations
		self.last_field_map_generation_seconds=0
		self.view_manager=None if camera_server is None else camera_server.view_manager
		self.image_field_map=self.get_template_image("Field Map")
		self.image_depth_map=self.get_template_image("Depth Map")
		self.push_field_map_image()
		self.push_depth_map_image()
		self.clean_depth_list()
		timestamp=int(time.time())
		path='/home/pi/Documents/log/'+str(timestamp)
		self.log_gps=open(path+"_gps.csv","a")
		self.log_gps.write("time_seconds,latitude,longitude\n")
		self.log_imu=open(path+"_imu.csv","a")
		self.log_imu.write("time_seconds,x_uT,y_uT,z_uT\n")
		self.log_encoder=open(path+"_encoder.csv","a")
		self.log_encoder.write("time_seconds,encoder_left,encoder_right\n")
		self.log_wheel=open(path+"_wheel.csv","a")
		self.log_wheel.write("time_seconds,front-left,rear-left,front-right,rear-right\n")
		self.log_lidar=open(path+"_lidar.csv","a")
		self.log_lidar.write("time_seconds,pan_degrees,tilt_degrees,distance_cm,index,is_map\n")
		
	def get_template_image(self,text):
		width=400
		height=480
		sizeColor = (0,255,0)
		blank_image = np.zeros((height,width,3), np.uint8)
		cv2.putText(blank_image, "{:s}".format(text),
			(int(width/2), int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, sizeColor, 2)
		#blank_image=cv2.flip(blank_image,1)
		return blank_image
		
	def append_gps_reading(self,latitude,longitude):
		line=str(time.time())+","+str(latitude)+","+str(longitude)+"\n"
		self.log_gps.write(line)
		
	#value is [x,y,z]
	def append_magnetic_reading(self,value):
		line=str(time.time())+","+str(value[0])+","+str(value[1])+","+str(value[2])+"\n"
		self.log_imu.write(line)
		
	def get_last_magnetic_heading(self):
		pass
		
	#reference Arduino.py for arduino_dict structure
	def append_encoder_reading(self,arduino_dict):
		line=str(time.time())+","+str(arduino_dict["encoder_left" ]["rotation"]+arduino_dict["encoder_left" ]["subposition"]/128.0)+","+ \
							      str(arduino_dict["encoder_right"]["rotation"]+arduino_dict["encoder_right"]["subposition"]/128.0)+"\n"
		self.log_encoder.write(line)
							      
	def get_last_encoder_reading(self):
		pass

	def append_wheel_control(self,command):
		line=str(time.time())+","+str(command["front-left"])+","+ \
								  str(command["rear-left"])+","+ \
								  str(command["front-right"])+","+ \
								  str(command["rear-right"])+"\n"
		self.log_wheel.write(line)
	
	#is_field_scan=True when sweeping left-right only
	#False is pat+tilt to build up 3d depth map
	def append_lidar_reading(self,pan_angle_degrees,tilt_angle_degrees,distance_cm,is_depth_map,index):
		#if last reading was depth map and this one isn't, build depth map image
		if(is_depth_map):
			self.depth_list.append({"pan":pan_angle_degrees,"tilt":tilt_angle_degrees,"distance":distance_cm})
		line=str(time.time())+","+str(pan_angle_degrees)+","+str(tilt_angle_degrees)+","+str(distance_cm)+","+str(index)+","+str(is_depth_map)+"\n"
		self.log_lidar.write(line)
		
	#if it's stale then will need to get a new one
	def is_field_map_stale(self):
		return time.time()>(self.last_field_map_generation_seconds+self.FIELD_MAP_DELAY_SECONDS)
		
	def get_depth_list(self,is_pan):
		if(is_pan):
			pan_min=self.ANGLE_DEFINITION["pan"]["minimum"]
			pan_max=self.ANGLE_DEFINITION["pan"]["maximum"]
			pan_step=self.ANGLE_DEFINITION["pan"]["step_depth"]
			pan_list=np.arange(pan_min,pan_max,pan_step)
			return pan_list
		else:
			tilt_min=self.ANGLE_DEFINITION["tilt"]["minimum"]
			tilt_max=self.ANGLE_DEFINITION["tilt"]["maximum"]
			tilt_step=self.ANGLE_DEFINITION["tilt"]["step_depth"]
			tilt_list=np.arange(tilt_min,tilt_max,tilt_step)
			return tilt_list
			
		
	#generate image, store locally for quick reference
	def get_depth_map_image(self):
		pan_list=self.get_depth_list(True)
		tilt_list=self.get_depth_list(False)
		image=np.zeros((len(tilt_list),len(pan_list),3),np.uint8)
		
		measurement_list=[]
		for measurement in self.depth_list:
			measurement_list.append(measurement["distance"])
		low_percentile=np.percentile(measurement_list,16)
		median=np.percentile(measurement_list,50)
		high_percentile=np.percentile(measurement_list,84)
		sigma=((median-low_percentile)+(high_percentile-median))/2
		full_range=255/(6*sigma)
		
		for index in range(len(self.depth_list)):
			row=self.depth_list[index]
			pan=row["pan"]
			tilt=row["tilt"]
			index_offset=np.clip(index+self.DEPTH_MAP_INDEX_OFFSET,0,len(self.depth_list)-1)
			measurement_offset=self.depth_list[index_offset]["distance"]
			green=128-(measurement_offset-median)*full_range #0 sigma (mean) is at 128, +3 sigma is at 255, -3 sigma at 0
			green=np.uint8(np.clip(green,0,255))
			red=64-(measurement_offset-median)*full_range/2
			blue=128+red
			red=np.uint8(np.clip(red,0,255))
			blue=np.uint8(np.clip(blue,0,255))
			pan_index=np.nonzero(pan_list==pan)[0][0]
			tilt_index=np.nonzero(tilt_list==tilt)[0][0]
			image[tilt_index,pan_index:]=[red,green,blue]
			
		image=cv2.flip(image,1)
		image=cv2.GaussianBlur(image, (3, 3), 0)
		image=cv2.resize(image,(400,480))
		self.image_depth_map=image

		
	def get_field_map_image(self):
		pass


	#if not building 3d map
	#400x480 px
	def push_field_map_image(self):
		if(self.view_manager is None): return
		#return image_field_map
		self.view_manager.push(2,self.image_field_map) #VIEW_TYPE.PLAYFIELD
		
	#3d map
	def push_depth_map_image(self):
		if(self.view_manager is None): return
		#don't have time to troubleshoot Python to figure out how to import Enums from super classes outside of current folder, so use static values
		self.view_manager.push(3,self.image_depth_map) #VIEW_TYPE.DEPTH_MAP

	#called at start of 10 minute competition to flush outstanding parameters
	def clean(self):
		pass
		
	def clean_depth_list(self):
		self.depth_list=[]

	@staticmethod
	def build_test():
		print("MapManager build test")
		import time
		map_manager=MapManager(None)
		cv2.imshow("Field", map_manager.image_field_map)
		cv2.imshow("Depth", map_manager.image_depth_map)
		cv2.waitKey(0)

if __name__ == "__main__":
	
	print("START")
	MapManager.build_test()
	print("DONE")
