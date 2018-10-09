#quit()

#create socket server, wait for connection
#receive commands
#transmit state
#shutdown if no command for too long (watchdog)

from connection import Connection,SERVER_DEFINITION
from periphreals.pwm import PWM
from periphreals.discrete import Discrete
from periphreals.camera import Camera
import time
import numpy as np

print("START")

server_def=SERVER_DEFINITION.ROBOT.value
is_server=True
this_conn=Connection(is_server,server_def["ip_address"],server_def["port"])

print("Pause to form connection...")
this_conn.start() #NOT blocking, exectuion will continue past here even if link is not established
while(not this_conn.is_connected()):
	time.sleep(0.1) #wait for opposite end of connection to appear

print("Connection formed")

print("Create camera")
cam=Camera()

print("Connect Servos...")
pwm=PWM()

print("Connect Discrete...")
discrete=Discrete()

wheel_list=[Discrete.FRONT_LEFT,Discrete.REAR_LEFT,Discrete.FRONT_RIGHT,Discrete.REAR_RIGHT]
dimmer_list={#speed control of wheels
			 Discrete.FRONT_LEFT:8,
			 Discrete.REAR_LEFT:9,
			 Discrete.FRONT_RIGHT:10,
			 Discrete.REAR_RIGHT:11
			 }

last_state_send_time=0
last_wheel_command_received_time=time.time()
MIN_STATE_DELAY_SECONDS=0.1 #only send state updates so frequently
MAX_AUTONOMUS_SECONDS=3 #how long robot will continue to move before self-terminating

wheel_state={Discrete.FRONT_LEFT:0,Discrete.REAR_LEFT:0,Discrete.FRONT_RIGHT:0,Discrete.REAR_RIGHT:0}
#		   0   1   2   3   4   5   6   7
pwm_min=[ 90,-20,-90, 22,  0,-90,  0, 20]
pwm_max=[205,200,210, 62,120,360,110,150]
pwm_state=[]
for index in range(len(pwm_max)):
	pwm_state.append((pwm_max[index]+pwm_min[index])/2)
	angle_degrees=pwm_state[index]
	pwm.set_servo(index,angle_degrees)

#TODO set servo state !!!!!!!!!!!!!!!!!!!

state_count=0
cam_pic_count=0

print("Start state loop...")

while(True):
	while(not this_conn.is_inbound_queue_empty()):
		command=this_conn.pop()
		if(command["target"]=="WATCHDOG"):
			#print("COMMAND: Watchdog")
			pass
		if(command["target"]=="WHEELS"):
			print(command)
			print("WHEELS HERE")
			last_wheel_command_received_time=time.time()
			#print("Wheel command ",Discrete.FRONT_LEFT,": ",command[Discrete.FRONT_LEFT])
			#print("Wheel command ",Discrete.FRONT_RIGHT,": ",command[Discrete.FRONT_RIGHT])
			#wheel_state[Discrete.FRONT_LEFT]=command[Discrete.FRONT_LEFT]
			for wheel_name in wheel_list:
				wheel_state[wheel_name]=command[wheel_name]
				discrete.setState(wheel_name,wheel_state[wheel_name])
				dimmer_channel=dimmer_list[wheel_name]
				dim_level=abs(wheel_state[wheel_name])
				pwm.set_dimmer(dimmer_channel,dim_level)
		elif(command["target"]=="PWM"):
			print(command)
			#reset (to center)
			channel_index=command["index"]
			pwm_scope=command["scope"]
			if(pwm_scope=="reset"):
				pwm_state[channel_index]=(pwm_max[channel_index]+pwm_min[channel_index])/2
				pwm.set_servo(channel_index,pwm_state[channel_index])
			elif(pwm_scope=="delta"):
				delta=command["value"]
				#print(pwm_state[channel_index],"+",delta,"=",pwm_state[channel_index]+delta)
				#print(pwm_min[channel_index],"<",pwm_state[channel_index]+delta
				pwm_state[channel_index]=np.clip(pwm_state[channel_index]+delta,pwm_min[channel_index],pwm_max[channel_index])
				pwm.set_servo(channel_index,pwm_state[channel_index])
			#skipping data sanitation for brevity...
			#delta (subject to limits)
			print("PWM HERE")
		elif(command["target"]=="CAMERA"):
			print("CAM HERE")
			cam.snapshot()
			cam_pic_count+=1
	is_recently_sent_state=(time.time()-last_state_send_time)<MIN_STATE_DELAY_SECONDS
	if(not is_recently_sent_state):#if been a while since last state sent, then send one
		state={"target":"state","counter":state_count,"wheels":wheel_state,"pwm":pwm_state,"camera":cam_pic_count}
		state_count+=1
		this_conn.send(state)
		last_state_send_time=time.time()
	if((time.time()-last_wheel_command_received_time)>MAX_AUTONOMUS_SECONDS):
		#watchdog execution, stop wheels
		for wheel_name in wheel_list:
			wheel_state[wheel_name]=0
			discrete.setState(wheel_name,wheel_state[wheel_name])
			dimmer_channel=dimmer_list[wheel_name]
			dim_level=abs(wheel_state[wheel_name])
			pwm.set_dimmer(dimmer_channel,0)
		
pwm.dispose()
	
print("DONE")
	
