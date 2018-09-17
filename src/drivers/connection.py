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

	#is_loopback performs IP packet ping between server and client on the same machine
	#is_wlan performs IP packet ping between server and client on different machines
	# this code must be run identically on two machines (machines will self-identify as robot
	# or controller based on their own IP addresses
	@staticmethod
	def build_test(is_robot,is_loopback,is_wlan):
		print("Connection Build Test...")
		import time
		
		print("Check own IP Address...")
		my_ip_address=Connection.getOwnAddress()
		found_node=None
		for node in SERVER_DEFINITION:
			node_ip_address=node.value["ip_address"]
			if(my_ip_address==node_ip_address): found_node=node
		print("Is the IP Address of this device valid? ","FAIL" if found_node is None else "PASS",": ",my_ip_address,", ",found_node)
		if(found_node is None):
			print("!! run the following command: sudo ifdown wlan0 && sudo ifdown eth0 && sudo ifup wlan0")
		if(is_robot is None):
			is_robot=found_node==SERVER_DEFINITION.ROBOT
			
		print("JSON Check...")
		
		print("Decode garbage...")
		decoder = json.JSONDecoder()
		garbage_list=["HA\nPPY","[{\"alpha\": 1}, {\"b"]
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
			
			server_conn=Connection(True,server_def["ip_address"],server_def["port"]) #this is server
			client_conn=Connection(False,server_def["ip_address"],server_def["port"]) #this is client
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
			time.sleep(0.5)
			
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
			num_messages=10
			for rep in range(num_messages):
				client_to_server_message={"payload":"PASS_"+str(rep)+"_of_"+str(num_messages)}
				client_conn.send(client_to_server_message)
			time.sleep(0.2)
			while(not server_conn.is_inbound_queue_empty()):
				print("Server received message: ",server_conn.pop())
			
			print("Dispose client...")
			client_conn.disconnect()
			print("Dispose server...")
			server_conn.disconnect()
			
		if(is_wlan):
			#robot is server, controller is client
			server_def=SERVER_DEFINITION.ROBOT.value #if is robot, setup server as robot
			if(is_robot):
				this_conn=Connection(True,server_def["ip_address"],server_def["port"])
			else:
				this_conn=Connection(False,server_def["ip_address"],server_def["port"])
			print("Pause to form connection...")
			this_conn.connect() #NOT blocking, exectuion will continue past here even if link is not established
			while(not this_conn.is_connected()):
				time.sleep(0.1) #wait for opposite end of connection to appear
			print("Connection established: ","PASS" if this_conn.is_connected() else "FAIL")
			packet_tennis=60 #send packets back and forth X times
			
			for packet_iter in range(packet_tennis):
				if(is_robot):
					this_packet="robot_"+str(packet_iter)
					print("Robot sending packet... ",this_packet)
					this_conn.send(this_packet)
				if(not is_robot):
					print("Controller wait for packet...")
					while(this_conn.is_inbound_queue_empty()):
						time.sleep(0.01)
					print("Controller received packet: ",this_conn.pop())
					this_packet="controller_"+str(packet_iter)
					print("Controller sending packet... ",this_packet)
					this_conn.send(this_packet)
				if(is_robot):
					print("Robot wait for packet...")
					while(this_conn.is_inbound_queue_empty()):
						time.sleep(0.01)
					print("Robot received packet: ",this_conn.pop())
					
			print("Dispose connection...")
			this_conn.disconnect()
					
					
			
			
		#print("Create...")
		#server_conn=Connection(server_def,True)
		#client_conn=Connection(client_def,False)
		#server_conn.connect()
		#client_conn.connect()
		

if __name__ == "__main__":
	print("START")
	is_robot=None #None: is_robot determined by IP address of computer
	is_loopback=False #test communication on local port?
	is_wlan=True #test communication between computers
	Connection.build_test(is_robot,is_loopback,is_wlan)
	print("DONE")

