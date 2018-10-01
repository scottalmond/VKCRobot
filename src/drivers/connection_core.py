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
T
Assumptions:


Usage:


"""

import threading
import queue
import json
import socket
import time
import subprocess#only for determining own ip address
import re #regular expressions for ip address parsing

class ConnectionCore(threading.Thread):
	
	MAX_PACKET_SIZE_BYTES=54321 #presumed maximum size of a packet from an external PC
	CONNECTION_TIMEOUT_SECONDS=0.1 #how long to listen for new connections before doing something else
	RATE_LIMIT_SECONDS=0.1 #limit how often activity is queried over TCP connection
	MAX_CONNECTIONS=3 #max clients that can connect to this server
	
	def __init__(self,is_server,ip_address,port_number):
		threading.Thread.__init__(self)
		self.is_server=is_server
		self.ip_address=ip_address
		self.port_number=port_number
		self.inbound_queue=queue.Queue() #FIFO contains JSON objects received from external PC
		self.__is_alive=True
		self.__is_connected=False
		self.__is_error=False
		self.socket=None
		self.connection=None #connection to the client
		self.decoder = json.JSONDecoder() #use raw_decode to gain access to index
		# of end of json packet - important for end-to-end packets received
		
	def run(self):
		#step 1: connect
		self.connect()
		
		#step 2: receive messages
		while(self.__is_alive and self.__is_connected):
			previous_packet=""
			data=""
			try:
				#print("is_server: ",self.is_server)
				target=self.connection if self.is_server else self.socket
				data=target.recv(self.MAX_PACKET_SIZE_BYTES)
				#print("data: ",data)
				#self.inbound_queue.put(package)
				this_packet=previous_packet+data.decode()
				#print("this_packet A: ",this_packet)
				is_socket_empty=False
				while(not is_socket_empty):
					#print("this_packet B: ",this_packet)
					try:
						this_obj,json_end=self.decoder.raw_decode(this_packet)
						self.__enqueue(this_obj)
						this_packet=this_packet[json_end:]
						if(len(this_packet)==0):
							is_socket_empty=True
					except json.decoder.JSONDecodeError:
						previous_packet+=this_packet
						is_socket_empty=True
			except socket.timeout as err:
				#if no input received, then move on to next task
				pass#print("ConnectionCore.run socket.timeout: ",err)
			except AttributeError as err:
				print("ConnectionCore.run AttributeError: ",err)
				#pass #type changed to None during execution
			except ConnectionResetError as err:
				self.__is_error=True
				print("ConnectionCore.run ConnectionResetError: ",err)
			#if(self.RATE_LIMIT_SECONDS>0 and len(data)==0): #sleep if no data received this iteration
			#	time.sleep(self.RATE_LIMIT_SECONDS) #managed through CONNECTION_TIMEOUT_SECONDS
			if(self.__is_alive and self.__is_error):#attempt to reestablish connection after it is broken
				self.__is_error=False
				self.dispose()
				self.connect()
		self.dispose()
	
	#open the communication channel with the other comptuer
	#sets the socket and connection variables
	#halts execution until a connection is established
	def connect(self):
		if(self.is_server): #for servers, both create the server AND wait for a client to connect
			if(self.__is_alive):
				try:
					self.socket=self.__getServerSocket(self.ip_address,self.port_number)
					while(self.__is_alive and not self.__is_connected):
						try:
							self.connection, addr=self.socket.accept()
							self.connection.settimeout(self.CONNECTION_TIMEOUT_SECONDS)
							self.__is_connected=True
						except socket.timeout:
							pass #looking for new clients, if none found, move on
						except AttributeError:
							pass #server_socket is None
						except OSError:
							pass #[Errno 9] Bad file descriptor
						if(self.RATE_LIMIT_SECONDS>0 and not self.__is_connected):
							#print("Server wait for client to appear...")
							time.sleep(self.RATE_LIMIT_SECONDS)
				except socket.timeout:
					pass #looking for new clients, if none found, move on
				except AttributeError:
					pass #server_socket is None
				except OSError:
					pass #[Errno 9] Bad file descriptor
		else: #is_client, so wait for server to appear then connect to it...
			while(self.__is_alive and not self.__is_connected):
				self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				self.socket.settimeout(self.CONNECTION_TIMEOUT_SECONDS)
				try:
					self.socket.connect((self.ip_address,self.port_number))
					self.__is_connected=True
				except socket.error as msg:
					pass #silence connection errors
				if(self.RATE_LIMIT_SECONDS>0 and not self.__is_connected):
					#print("Client wait for server to appear...")
					time.sleep(self.RATE_LIMIT_SECONDS)
	
	def __getServerSocket(self,ip_address,port_number):
		skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		skt.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #allow back-to-back connections/build-tests
		#(otherwise there is a 60 second delay before the server can be recreated.  During this delay window
		#errno 98 will be created)
		skt.settimeout(self.CONNECTION_TIMEOUT_SECONDS)
		try:
			skt.bind((ip_address,port_number))
			skt.listen(self.MAX_CONNECTIONS)
			return skt
		except socket.error as msg:
			print("ConnectionCore.__getServerSocket error: ",msg)
			pass
		return None
	
	#super class send an item outbound immediately
	#input is an object: dict, list, string, int, etc
	def send(self,message_obj):
		target=self.connection if self.is_server else self.socket
		if(not self.__is_connected or target is None):
			return False#unable to send to a broken connection
		try:
			target.send(json.dumps(message_obj).encode())
			return True
		except AttributeError as err:
			print("ConnectionCore.send AttributeError:",err)
		except BrokenPipeError as err:
			self.__is_error=True
			print("ConnectionCore.send BrokenPipeError:",err)
		except socket.timeout as err:
			self.__is_error=True
			print("ConnectionCore.send socket.timeout:",err)
		return False
		
	#return pointer to latest queue JOSN object without removing it from the queue
	def peek(self):
		if(self.is_inbound_queue_empty()):
			return None
		return self.inbound_queue.queue[0]
		
	#remove and return the latest JOSN object in the queue
	def pop(self):
		if(self.is_inbound_queue_empty()):
			return None
		try:
			return self.inbound_queue.get(block=False)
		except queue.Empty:
			pass
		return None
		
	def is_inbound_queue_empty(self):
		return self.inbound_queue.empty()
	
	#internal processing method called when a complete json object is received
	def __enqueue(self,message_obj):
		self.inbound_queue.put(message_obj)
	
	def disconnect(self):
		self.__is_alive=False
		self.join()
		
	def is_connected(self):
		return self.__is_connected
	
	#called automatically by internal processes
	# use disconnect() instead
	def dispose(self):
		if(self.is_server and not self.connection is None):
			self.connection.close()
			self.connection=None
		if(not self.socket is None):
			self.socket.close()
			self.socket=None
		self.__is_connected=False
			
		
	#returns IP address String
	@staticmethod
	def getOwnAddress():
		ip_addr_hr=subprocess.check_output(['hostname', '--all-ip-addresses'])
		regex=re.compile(r"""[0-9]+(?:\.[0-9]+){3}""")
		return regex.findall( str(ip_addr_hr) )[0]
