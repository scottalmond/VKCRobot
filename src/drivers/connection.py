"""
   Copyright 2018 Scott Almond

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Purpose:
This class as a kind of virtual mail sorter.  Messages from other PCs, 
 both servers and clients, come into this class through TCP connections.
 Inbound messages are queued for when the program is ready to read them.
 Conversely, outbound messages are sent immediately

Assumptions:


Usage:
python3 connection.py SERVER
python3 connection.py CLIENT

PRECON: all connections are point-to-point (one client per server)

"""

import json
from enum import Enum

from connection_core import ConnectionCore

class SERVER_DEFINITION(Enum):
	ROBOT={"ip_address":"192.168.1.113","port":7003}
	CONTROLLER={"ip_address":"192.168.1.112","port":7002}

class Connection:
	
	
	def __init__(self,is_server,ip_address,port_number):
		self.core=ConnectionCore(is_server,ip_address,port_number)
		
	def is_connected(self):
		return self.core.is_connected()
	
	def connect(self):
		self.core.start()
		
	def disconnect(self):
		self.core.disconnect()
		#self.core.join() #wait for helper class to finish multi-threaded application
		
	#given an object (dict, list, string, int, etc), push to the outbound message queue
	def send(self,message_obj):
		return self.core.send(message_obj)
		
	#return the oldest message from the incoming queue
	#returned the same as was sent: dict, list, string, int, etc
	def pop(self):
		return self.core.pop()
		
	#True if incoming message queue is empty
	def is_inbound_queue_empty(self):
		return self.core.is_inbound_queue_empty()
		
	#False for fully-functional link
	#True anything else
	def is_error(self):
		return self.is_error
		
	@staticmethod
	def getOwnAddress():
		return ConnectionCore.getOwnAddress()

	@staticmethod
	def build_test(is_loopback,is_robot):
		print("Connection Build Test...")
		import time
		
		print("JSON Check...")
		
		print("Decode garbage...")
		decoder = json.JSONDecoder()
		garbage_list=["FA\nIL","[{\"alpha\": 1}, {\"b"]
		for garbage in garbage_list:
			try:
				decompressed,end_index=decoder.raw_decode(garbage)
				print("Decompressed garbage: ",decompressed,", ",end_index)
			except json.decoder.JSONDecodeError:
				print("Garbage parse test: PASS from ",garbage)
		
		print("Multi-message JSON parse...")
		message_1=[{"alpha":1},{"beta":[2,3,4]},{"epsilon":{"bravo":5,"elix":6}}]
		message_2={"thing":"kind","igloo":[7,8]}
		print("Outbound message 1: ",message_1)
		print("Outbound message 2: ",message_2)
		compressed_1=json.dumps(message_1)
		compressed_2=json.dumps(message_2)
		compressed=compressed_1+compressed_2
		print("Merged json: ",compressed)
		decompressed,end_index=decoder.raw_decode(compressed)
		print("Decompressed 1: ",decompressed,", ",end_index)
		compressed=compressed[end_index:]
		print("Remainder merged json compressed: "+compressed)
		decompressed,end_index=decoder.raw_decode(compressed)
		print("Decompressed 2: ",decompressed,", ",end_index)
		
		
		if(is_robot):
			server_def=SERVER_DEFINITION.ROBOT.value #if is robot, setup server as robot
			client_def=SERVER_DEFINITION.CONTROLLER.value #try to connect to controller as client
		else:
			server_def=SERVER_DEFINITION.CONTROLLER.value #if is controller, setup server as controller
			client_def=SERVER_DEFINITION.ROBOT.value #try to connect to robot server as client
		if(is_loopback):# test only locally on one computer
			print("Run loopback test on local machine...")
			my_address=Connection.getOwnAddress()
			print("My IP Address: "+my_address)
			print("If not a valid IP address, run: ")
			print("  sudo ifdown wlan0 && sudo ifdown eth0 && sudo ifup wlan0")
			
			server_conn=Connection(True,server_def["ip_address"],server_def["port"])
			client_conn=Connection(False,server_def["ip_address"],server_def["port"])
			print("Create server...")
			server_conn.connect()
			print("Create client...")
			client_conn.connect()
			
			print("Wait for connection to be established...")
			time.sleep(0.5)
			print("Server connected? ","PASS" if server_conn.is_connected() else "FAIL")
			print("Server address: ",server_conn.core.socket)
			print("Server view of client address: ",server_conn.core.connection)
			print("Client connected? ","PASS" if client_conn.is_connected() else "FAIL")
			print("Client view of server address: ",client_conn.core.socket)
			
			print("Wait for link to settle...")
			time.sleep(2.5)
			
			print("Send message from client to server...")
			client_to_server_message={"payload":"ALPHA"}
			server_to_client_response="BETA"
			client_conn.send(client_to_server_message)
			for rep in range(10):
				if(not server_conn.is_inbound_queue_empty()):
					server_to_client_response=server_conn.pop()
				else:
					time.sleep(0.1)
			print("Response server to client: ","PASS" if server_to_client_response==client_to_server_message else "FAIL")
			
			print("Send message from server to client...")
			server_to_client_message={"payload":"DELTA"}
			client_to_server_response="GAMMA"
			server_conn.send(server_to_client_message)
			for rep in range(10):
				if(not client_conn.is_inbound_queue_empty()):
					client_to_server_response=client_conn.pop()
				else:
					time.sleep(0.1)
			print("Response server to client: ","PASS" if client_to_server_response==server_to_client_message else "FAIL")
			
			print("Send multiple messages from client to server...")
			for rep in range(10):
				server_to_client_message="PASS_"+str(rep)
			
			print("Dispose client...")
			client_conn.disconnect()
			print("Dispose server...")
			server_conn.disconnect()
			
		#print("Create...")
		#server_conn=Connection(server_def,True)
		#client_conn=Connection(client_def,False)
		#server_conn.connect()
		#client_conn.connect()
		

if __name__ == "__main__":
	print("START")
	is_loopback=True #test communication on local port?
	is_robot=True #test communication between multiple computers as is_robot
	Connection.build_test(is_loopback,is_robot)
	print("DONE")

