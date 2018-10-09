#manages all PWM/Lidar/IMU/Discrete/Encoder operations
# lidar-pwm has a scheduler (back-forth or depth map), no interrupt
# arm servos has a scheduler (sequece of command states), interrupt with pwm arm servo command and/or pwm home
# wheels/imu/encoder has a scheduler (go to home), interrupt with wheel command

from periphreals.pwm import PWM
from periphreals.discrete import Discrete
from periphreals.imu import IMU
from periphreals.lidar import Lidar
from periphreals.arduino import Arduino
from periphreals.gps import GPS
import time
import copy

class ContentionManager:
	WHEEL_LIST=[Discrete.FRONT_LEFT,Discrete.REAR_LEFT,Discrete.FRONT_RIGHT,Discrete.REAR_RIGHT]
	WHEEL_PWM_CHANNELS={#speed control of wheels
				 Discrete.FRONT_LEFT:9,#8,
				 Discrete.REAR_LEFT:8,#9,
				 Discrete.FRONT_RIGHT:10,
				 Discrete.REAR_RIGHT:11
				 }
	ARM_PWM_CHANNELS=[0,1,2,3,4,5] #user-controlled channels
	ARM_DELAY_BETWEEN_SWEEP_STATES_SECONDS=0.5 #wait X seconds between each sweep command to allow arm to physcially move to commanded position
	LIDAR_PWM_CHANNELS={"pan":6,"tilt":7} #pan, tilt
	PWM_LIMITS={"minimum":[  0,  0,  0,  0,  0,  0,  0,  0],#angular range of servos before hitting something
				"maximum":[180,180,180,180,180,180,180,180]}
	WHEEL_CIRCUMFERNECE_INCH=15
	
	def __init__(self):
		self.pwm_state_ratio=[0,0,0,0,0,0,0,0]#channels 0 to 7, where 0 to 5 are user controlled (arm) and last two are tasked (pan-tilt lidar)
		self.pwm_queue=[]
		self.pwm_queue_state={"is_looping":False,"last_state_command_seconds":time.time(),"last_state_index":0}
		self.wheel_state={}#current state
		self.encoder_state=None
		self.pwm_lidar_schedule=[]
		
		self.discrete=Discrete()
		self.pwm=PWM()
		self.imu=IMU()
		self.lidar=Lidar()
		self.arduino=Arduino()
		self.gps=GPS()
		
		self.command_wheel_state({Discrete.FRONT_LEFT:0,Discrete.REAR_LEFT:0,Discrete.FRONT_RIGHT:0,Discrete.REAR_RIGHT:0})
		self.command_pwm_home()
		self.command_led_state([False,False,False,False])
		
	def update(self,command_list):
		for command in command_list:
			if(command["target"]=="WHEELS"):
				self.command_wheel_state(command)
			if(command["target"]=="PWM"):
				if(command["command"]=="clear"): self.command_clear_pwm_list()
				elif(command["command"]=="save"): self.command_append_pwm_to_list()
				elif(command["command"]=="loop"): self.command_loop_pwm_list()
				elif(command["command"]=="home"): self.command_pwm_home()
				elif(command["command"]=="set"):
					self.command_pwm_set(command["index"],command["value"])
			if(command["target"]=="CAMERA"):
				if(command["command"]=="leds"):
					self.command_led_state(command["value"])
		self.auto_lidar_pwm_scheduler()
		self.auto_lidar_pwm_hook()
		self.auto_arm_sweep_hook()
		self.auto_wheel_hook()
		self.map_hook() #read imu/gps, update robot/obstacle state, generate field/depth maps, but do it quickly...
			
	def popStatus(self):
		return {"status":"demo"}
		
	def dispose(self):
		self.pwm.dispose()
		
	#create pre-scheduled tasks on pan-tilt servos and read lidar distance
	# if no tasks in queue, schedule side-side motion
	def auto_lidar_pwm_scheduler(self):
		pass
		
	#execute queued tasks from scheduler for lidar sweep/map
	def auto_lidar_pwm_hook(self):
		pass
		
	#go to next arm state, if one is available
	#only do arm servos though
	def auto_arm_sweep_hook(self):
		if(self.pwm_queue_state["is_looping"] and len(self.pwm_queue)>0):
			time_now_seconds=time.time()
			last_command_seconds=self.pwm_queue_state["last_state_command_seconds"]
			is_ready_for_next_position=time_now_seconds>(self.ARM_DELAY_BETWEEN_SWEEP_STATES_SECONDS+last_command_seconds)
			if(is_ready_for_next_position):
				next_state_index=self.pwm_queue_state["last_state_index"]+1
				if(next_state_index>=len(self.pwm_queue)):
					next_state_index=0
				for channel in self.ARM_PWM_CHANNELS:
					angle_ratio=self.pwm_queue[next_state_index][channel]
					self.set_raw_pwm(channel,angle_ratio)
				self.pwm_queue_state["last_state_index"]=next_state_index
				self.pwm_queue_state["last_state_command_seconds"]=time_now_seconds
		
	#go to next wheel state, if one is available
	def auto_wheel_hook(self):
		pass
		
	#user command, will flush any internal auto-queue (go home)
	# dict keys (string): Discrete.FRONT_LEFT,Discrete.REAR_LEFT,Discrete.FRONT_RIGHT,Discrete.REAR_RIGHT
	# with values -1.0 to 1.0
	def command_wheel_state(self,command):
		#print("ContentionManager.command_wheel_state not implemented")
		#TODO: flush command queue...
		self.set_raw_wheel_state(command)
	
	#lowest level tasking, generates event log
	def set_raw_wheel_state(self,command):
		#print("ContentionManager.set_raw_wheel_state not implemented")
		for wheel_name in self.WHEEL_LIST:
			self.wheel_state[wheel_name]=command[wheel_name]
			self.discrete.setState(wheel_name,self.wheel_state[wheel_name])
			dimmer_channel=self.WHEEL_PWM_CHANNELS[wheel_name]
			dim_level=abs(self.wheel_state[wheel_name])
			self.pwm.set_dimmer(dimmer_channel,dim_level)
		
	def command_wheel_stop(self):
		self.command_wheel_state({Discrete.FRONT_LEFT:0,Discrete.REAR_LEFT:0,Discrete.FRONT_RIGHT:0,Discrete.REAR_RIGHT:0})
		
	#create task list for wheels
	# states: ROTATE_TO_HOME, DRIVE_FORWARD_UNTIL_ONE_ENCODER_PAST_TARGET
	def command_wheel_home(self):
		print("ContentionManager.command_wheel_home not implemented")
		
	#user command to clear list of pwm (arm) saved states
	def command_clear_pwm_list(self):
		self.pwm_queue=[]
		self.pwm_queue_state["last_state_index"]=0
		self.pwm_queue_state["is_looping"]=False
		
	#user command to save the current pwm (arm) state of the 6 servos
	def command_append_pwm_to_list(self):
		print("ContentionManager.command_save_pwm_list not implemented")
		self.pwm_queue.append(copy.deepcopy(self.pwm_state_ratio))
		
	#user command to loop the list of pwm (arm) states 1,2,3,4,1,2,3,4... style
	#kicks off the state machine
	def command_loop_pwm_list(self):
		self.pwm_queue_state["is_looping"]=not self.pwm_queue_state["is_looping"]
		#print("ContentionManager.command_loop_pwm_list not implemented")
		
	#user command to set the arm to a mid-range position
	def command_pwm_home(self):
		for channel in self.ARM_PWM_CHANNELS:
			#angle_degrees=(self.PWM_LIMITS["minimum"][channel] + self.PWM_LIMITS["maximum"][channel])/2
			#self.pwm.set_servo(channel,angle_degrees)
			self.command_pwm_set(channel,0.5)
		
	#min_max_ratio=0 for minimum degrees, 1 for maximum angle
	def command_pwm_set(self,channel,min_max_ratio):
		self.pwm_queue_state["is_looping"]=False
		if(min_max_ratio<-0.2 or min_max_ratio>1.2):
			print("ContentionManager.command_pwm_set, command PWM out of range: channel: ",channel,", ratio: ",min_max_ratio)
		else:
			self.set_raw_pwm(channel,min_max_ratio)
			
	def set_raw_pwm(self,channel,min_max_ratio):
		angle_degrees=min_max_ratio*(self.PWM_LIMITS["maximum"][channel]-self.PWM_LIMITS["minimum"][channel])+self.PWM_LIMITS["minimum"][channel]
		self.pwm.set_servo(channel,angle_degrees)
		self.pwm_state_ratio[channel]=min_max_ratio
		
	#enabled list is four element boolean list
	def command_led_state(self,enabled_list):
		#print("ContentionManager.command_led_state not implemented")
		if(not len(enabled_list)==4):
			print("ContentionManager.command_led_state, invalid led command input: ",enabled_list)
		else:
			print("ContentionManager.command_led_state, set leds: ",enabled_list)
			self.arduino.writeLED(enabled_list)
	
	def map_hook(self):
		#read imu/gps/encoder
		#update robot state
		#generate images if not tasked with other things
		pass
	
	@staticmethod
	def build_test():
		print("ContentionManager build test")
		import time
		contention_manager=ContentionManager()
		#move wheels forward at a low speed for 4 seconds, printing encoder readings
		time_stop_seconds=time.time()+4
		left_speed=0.0
		right_speed=0.1
		contention_manager.command_wheel_state({Discrete.FRONT_LEFT:left_speed,Discrete.REAR_LEFT:left_speed,Discrete.FRONT_RIGHT:right_speed,Discrete.REAR_RIGHT:right_speed})
		try:
			while(time.time()<time_stop_seconds):
				arduino_dict=Arduino.parseLine(contention_manager.arduino.getLastLine())
				if(not arduino_dict is None):
					print("Reading: ",arduino_dict)
				time.sleep(0.01)
		except Exception as exp:
			print("Exception: ",exp)
		contention_manager.command_wheel_stop()
		#22 packets at 10%, with 50 ms delays on Arduino
		#moved delay to 20 ms
		
		#move arm to home, then +-10 degrees on each channel
		
		
		#contention_manager.imu.build_test()
		#contention_manager.lidar.build_test()
		#contention_manager.discrete.build_test()
		#contention_manager.pwm.build_test()
		
		
if __name__ == "__main__":
	
	print("START")
	ContentionManager.build_test()
	print("DONE")
