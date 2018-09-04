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



"""

class SERVER_DEFINITION(Enum):
	ROBOT={"address":192.168.1.113,"port":7003}
	CONTROLLER={"address":192.168.1.112,"port":7002}

class Connection:
	
	
	def __init__(self,server_def,is_server):
		self.server_def=server_def
		self.is_server=is_server
		self.is_error=False
		
	def connect(self):
		pass
		
	def disconnect(self):
		pass
		
	def send(self,json):
		pass
		
	#False for fully-functional link
	#True anything else
	def is_error(self):
		return self.is_error

	@staticmethod
	def build_test(is_loopback,is_robot):
		print("Connection Build Test...")
		if(is_robot):
			server_def=SERVER_DEFINITION.ROBOT #if is robot, setup server as robot
			client_def=SERVER_DEFINITION.CONTROLLER #try to connect to controller as client
		else:
			server_def=SERVER_DEFINITION.CONTROLLER #if is controller, setup server as controller
			client_def=SERVER_DEFINITION.ROBOT #try to connect to robot server as client
		if(is_loopback):# test only locally on one computer
			print("Run loopback test on local machine...")
			server_conn=Connection(server_def,True)
			client_conn=Connection(server_def,False) #create client and server definitions for same port
			print("Create server...")
			server_conn.connect()
			print("Create client...")
			client_conn.connect()
			print("Send message from client to server...")
			
			print("Send message from server to client...")
			
			
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

