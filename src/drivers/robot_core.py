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

server_def=SERVER_DEFINITION.ROBOT.value
is_server=True
this_conn=Connection(is_server,server_def["ip_address"],server_def["port"])

iteration_counter=0

print("Pause to form connection...")
this_conn.start() #NOT blocking, execution will continue past here even if link is not established
while(not this_conn.is_connected()):
	time.sleep(0.1) #wait for opposite end of connection to appear
	print("RobotCore waiting to form connection: ",iteration_counter)

print("Connection formed")

print("Init Contention Manager...")
contention_manager=ContentionManager()

print("Init Camera Server...")
camera_server=CameraManager()

print("Start state loop...");

while(True):
	time.sleep(0.1)
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
		
	
	contention_manager.update(command_list)
	camera_server.update(command_list)
	
	status_packet_contention=contention_manager.popStatus()
	status_packet_camera=camera_server.popStatus()
	
	

contention_manager.dispose()
camera_server.dipose()
