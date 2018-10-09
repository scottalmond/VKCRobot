#CONOPS:
# cycle through all sensors very fast ~200-300 Hz ideally
# for PWM/Lidar/IMU, pull commands from a task list for the PWM/Lidar
#   so standard operation is to have a back-and-forth auto-populating scan queue except when
#   user command depth map, at which point standad queue is flushed, map queue is populated.
#   following completion of map queue, revert back to standard sweepa
#also, note to self: check eather: implement GPS if forecast is sunny b/c will be outdoor competition

#rc-local exception:
# ImportError: No module named 'pyzbar'
# /src/drivers/periphreals/camera_server.py
import os
os.system("cd /home/pi/Documents/VKCRobot/src/drivers")

from connection import Connection,SERVER_DEFINITION
#from periphreals.camera import Camera
from periphreals.camera_server import CameraManager
from contention_manager import ContentionManager
import time
import numpy as np

print("START")

MIN_STATE_DELAY_SECONDS=0.1 #only send state updates so frequently

server_def=SERVER_DEFINITION.ROBOT.value
is_server=True
this_conn=Connection(is_server,server_def["ip_address"],server_def["port"])

iteration_counter=0

print("Init Camera Server...")
camera_server=CameraManager()
camera_server.start()

print("Pause to form connection...")
this_conn.start() #NOT blocking, execution will continue past here even if link is not established
while(not this_conn.is_connected()):
	time.sleep(0.1) #wait for opposite end of connection to appear
	print("RobotCore waiting to form connection: ",iteration_counter)
	#print("QR: ",camera_server.popStatus())

print("Connection formed")

print("Init Contention Manager...")
contention_manager=ContentionManager()

print("Start state loop...");
state_count=0
last_state_send_time=0 #last status packet
while(True):
	#time.sleep(0.03)#optional throttle
	print("RobotCore iteration: ",iteration_counter)
	iteration_counter+=1
	
	command_list=[]
	
	while(not this_conn.is_inbound_queue_empty()):
		command=this_conn.pop()
		if(command["target"]=="WATCHDOG"):
			pass
		else:
			command_list.append(command)
			print("RobotCore command: ",command)
	
	if(True):
	#try:
		contention_manager.update(command_list)
	#except: pass #attempt to keep robot running by silencing errors operationally
	#try:
		camera_server.update(command_list)
	#except: pass
	
	status_packet_sensors=contention_manager.popStatus() #wheel state, pwm state, is looping pwm, pwm queue length, is homing
	status_packet_camera=camera_server.popStatus() #led state, exposure, qr codes
	#packet id
	
	is_recently_sent_state=(time.time()-last_state_send_time)<MIN_STATE_DELAY_SECONDS
	if(not is_recently_sent_state):#if been a while since last state sent, then send one
		state={"target":"state","counter":state_count,**status_packet_sensors,**status_packet_camera}
			   #"led":status_packet_sensors["led"],
			   #"wheels":status_packet_sensors["wheels"],
			   #"pwm":status_packet_sensors["pwm"],
			   #"qr_list":status_packet_camera["qr_list"]}
		state_count+=1
		this_conn.send(state)
		last_state_send_time=time.time()
	

contention_manager.dispose()
camera_server.dipose()
