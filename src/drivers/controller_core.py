#create client socket, wait for connection
#send commands
#receive status

from connection import Connection,SERVER_DEFINITION
import time
from gui_TS import GUI
#import omxplayer.player

print("START")

is_benchtop=False #True: no robot present
is_windowed=True
server_def=SERVER_DEFINITION.ROBOT.value
is_server=False
this_conn=Connection(False,server_def["ip_address"],server_def["port"])

print("Pause to form connection...")
if(not is_benchtop):
	this_conn.start()
	while(not this_conn.is_connected()):
		time.sleep(0.1)
	
#print("Start live video feed...")
#video_uri='http://192.168.1.113:8000/stream.mjpg'
##video_args=['--win','0,0,400,480','-r','--live','\'http://192.168.1.113:8000/stream.mjpg\'']
#video_player=omxplayer.player.OMXPlayer(video_uri)
#video_player.set_video_pos(0,0,400,480)
	
print("Create GUI...")#make GUI...
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
		packet_id +=1
		if(not is_benchtop):
			this_conn.send(command)
	gui.update()
	commands=gui.popCommands()
	for command in commands:
		if(not is_benchtop):
			this_conn.send(command)
		else:
			print("  ControllerCore.main: sending packet: ",command)
	status=None
	if(not is_benchtop):
		while(not this_conn.is_inbound_queue_empty()):
			status=this_conn.pop()
		if(not status is None): #only use last status for efficiency
			gui.setStatus(status)
			#state={"target":"state","counter":__counter_of_packetts_int__,"wheels":[1.0,-1.0,0.0,0.345],"pwm":[90,65,100,55,-20,0,180,50],"camera":0,"led":[True,True,False,False],"qr_code":[{"text":"Alpha","location":[x,y,w,h]},{"text":"Beta","location":[x,y,w,h]}]}
	time.sleep(0.01)
	
gui.dispose()
#video_player.quit()
	


print("DONE")
