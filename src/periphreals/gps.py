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
reads GPS data stream to determine latest solution fix

Usage:

run main program:
python3 gps.py



Parallax 565K GPS:
VCC to 5V
GND
SIO to TBCM 15, wPi 16, RXD, Physical 10
/RAW to GND

"""

class GPS:
	
	#GPS_ADDRESS_UART='/dev/ttyAMA0'
	GPS_ADDRESS_UART='/dev/ttyS0'
	UART_BAUD_RATE=4800
	
	def __init__(self):
		import serial
		self.serial=serial
		self.file_descriptor=self.initInterface()
		
	def initInterface(self):
		#wpi=self.wpi
		#file_descriptor=wpi.serialOpen(self.GPS_ADDRESS_UART,self.UART_BAUD)
		file_descriptor=self.serial.Serial(self.GPS_ADDRESS_UART,self.UART_BAUD_RATE,timeout=0.1)
		return file_descriptor
		
	def clean(self):
		#self.wpi.serialClose(self.file_descriptor)
		pass
		
	#given a string line, determine the type
	#if of the form $GPRMC http://aprs.gids.nl/nmea/
	#then ensure checksum is correct
	#ensure "Navigation" is A for Ok
	#returns two doubles: latitude and longitude
	#latitude is between TODO
	#longitude is between TODO
	#return None on Error
	@staticmethod
	def parsePositionFix(line):
		latitude=-91
		longitude=-181
		if(len(line.strip())<=0): return None,None
		#TODO
		#look online: there may already be a python library out there that parses these data lines, if not:
		#break string by commas
		#is of type GPRMC? if not return None,None
		#get checksum
		#compare checksum with string
		#get position fix is "A" ok, if not return None,None
		#for element in [latitude,longitude]:
		#break "12311.12,W" into ["123","11.12","W"]
		#convert strings to numbers: [123,11.12]
		#change minutes from base 60 to 100: 11.12/60 = .1853
		#combine with integer latitude/longitude: 123 + 0.183=123.1853
		#negate if West or South: -123.1853
		#correctness check: https://www.latlong.net/Show-Latitude-Longitude.html
		return latitude,longitude
		
	#return True on successful build test
	@staticmethod
	def build_test(is_loopback):
		print("GPS Build Test...")
		static_gps_sentence="$GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68"
		print("Static GPS Fix Sentence: ",static_gps_sentence)
		latitude,longitude=GPS.parsePositionFix(static_gps_sentence)
		latitude_pass=abs(latitude-49.2741)<=0.0001
		longitude_pass=abs(longitude-(-123.1853))<=0.0001
		print("Instantiate GPS class...")
		gps=GPS()
		is_file_descriptor_open=not gps.file_descriptor is None
		print("UART File Descriptor Opened: ","PASS" if is_file_descriptor_open else "FAIL")
		print("Visualization: https://www.latlong.net/c/?lat="+str(latitude)+"&long="+str(longitude)) #Vancouver
		print("Parse static position fix: ","PASS" if (latitude_pass and longitude_pass) else "FAIL")
		if(is_file_descriptor_open):
			print("UART Loopback write...")
			bytes_sent=gps.file_descriptor.write("PASS".encode('utf-8'))
			print("UART Loopback read...")
			received=gps.file_descriptor.read(bytes_sent).decode('utf-8').strip()
			print("UART Loopback test: ",received if len(received)>0 else "FAIL")
			print("Fetch live GPS fix...")
			max_attempts=20
			is_live_fix_found=False
			for attempt in range(max_attempts):
				received=gps.file_descriptor.readline().decode('utf-8').strip()
				latitude,longitude=gps.parsePositionFix(received)
				if(not latitude is None):
					print("Live GPS Fix Sentence: ",received)
					print("Latitude, Longitude fix: ",latitude,", ",longitude)
					print("Visualization: https://www.latlong.net/c/?lat="+str(latitude)+"&long="+str(longitude))
					is_live_fix_found=True
					break;
			if(not is_live_fix_found):
				print("Live GPS Fix Sentence: FAIL")
				print("Latitude, Longitude fix: FAIL")
				print("Visualization: FAIL")
		
if __name__ == "__main__":
	print("START")
	is_loopback=False #is UART configured with TX connected to RX?
	GPS.build_test(is_loopback)
	print("DONE")
