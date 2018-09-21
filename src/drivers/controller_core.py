#create client socket, wait for connection
#send commands
#receive status

from connection import Connection,SERVER_DEFINITION
import time
from gui import GUI

print("START")

server_def=SERVER_DEFINITION.ROBOT.value
is_server=False
this_conn=Connection(False,server_def["ip_address"],server_def["port"])

print("Pause to form connection...")
this_conn.connect()
while(not this_conn.is_connected()):
	time.sleep(0.1)
	
print("Create GUI...")#make GUI...
is_windowed=False
gui=GUI(is_windowed)
	
last_watchdog_time=0
MAX_WATCHDOG_TIME_SECONDS=0.5 #max delay between watchdog packets
packet_id=0
	
	
print("Start command loop...")
	
while(gui.is_alive()):
	if((time.time()-last_watchdog_time)>MAX_WATCHDOG_TIME_SECONDS):
		#print("COMMAND: Watchdog")
		last_watchdog_time=time.time()
		command={"target":"WATCHDOG","packet_id":packet_id}
		packet_id+=1
		this_conn.send(command)
	gui.update()
	commands=gui.popCommands()
	for command in commands:
		this_conn.send(command)
	status=None
	while(not this_conn.is_inbound_queue_empty()):
		status=this_conn.pop()
	if(not status is None): #only use last status for efficiency
		gui.setStatus(status)
	
gui.dispose()
		
	


print("DONE")
