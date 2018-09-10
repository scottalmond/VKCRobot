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
Queries LIDAR Lite v3 for distance measurement

Usage:


run main program:
python3 lidar.py

Connections:
VCC (red) to 5V
GND (black) to RTN
Power Enable (Orange) to float
Mode (Yellow) to float
SCL (green) to: BCM 3, wPi 9, Pys 5
SDA (blue) to: BCM 2, wPi 8, Phys 3



"""

class Lidar:

	SAMPLING_FREQUENCY_HZ=10
	I2C_ADDRESS=0x62
	I2C_REGISTER_ACQ_COMMAND=0x00
	I2C_REGISTER_STATUS=0x01
	I2C_REGISTER_FULL_DELAY_HIGH=0x0F
	I2C_REGISTER_FULL_DELAY_LOW=0x10
	I2C_REGISTER_TRIGGER_COUNT=0x11
	I2C_REGSITER_UNIT_ID_HIGH=0x16
	I2C_REGSITER_UNIT_ID_LOW=0x17
	I2C_REGISTER_SAMPLING_DELAY=0x45
	
	def __init__(self):
		import wiringpi as wpi
		self.wpi=wpi
		self.file_descriptor=self.initInterface(self.SAMPLING_FREQUENCY_HZ)
	
	def initInterface(self,sampling_freqeuncy_hz):
		wpi=self.wpi
		file_descriptor=wpi.wiringPiI2CSetup(self.I2C_ADDRESS)
		#configure device to capture continuously
		wpi.wiringPiI2CWriteReg8(file_descriptor,self.I2C_REGISTER_TRIGGER_COUNT, 0xFF)
		#configure triggering rate
		wpi.wiringPiI2CWriteReg8(file_descriptor,self.I2C_REGISTER_SAMPLING_DELAY, int(2000 / sampling_freqeuncy_hz))
		return file_descriptor
		
	#returns device unique identifier
	def whoAmI(self):
		return self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGSITER_UNIT_ID_HIGH)
		
	#returns distance measurement in centimeters
	#returns -1 on error
	def measure(self):
		byte_high=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_FULL_DELAY_HIGH)
		byte_low=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_FULL_DELAY_LOW)
		#print("HIGH: ",hex(byte_high))
		#print("LOW: ",hex(byte_low))
		measurement=byte_high<<8 | byte_low
		return measurement
		
	#per Garmin spec sheet for bare-bones measurement collection
	def simple_measure(self):
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_ACQ_COMMAND, 0x04)
		lsb=0x00
		status=-1
		while(lsb==0x00 or status==-1):
			status=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_STATUS)
			lsb=0x01&status
			#print("STATUS: ",hex(status))
		return self.measure()
		
	def scan(self):
		reg=0x00
		for rep in range(0x66):
			value=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,reg)
			print("Contents: REGISTER: ",hex(reg)," VALUE (HEX): ",hex(value)) #", VALUE (BIN): ",format(value,'#010b'),
			reg+=0x01
	
	@staticmethod
	def build_test(is_stream):
		print("LIDAR Build Test...")
		print("Instantiate Lidar class...")
		lidar=Lidar()
		print("Lidar Unique Identifier: ",lidar.whoAmI())
		#lidar.scan()
		print("Collect measurement...")
		measurement=lidar.simple_measure()
		print("Measurement: ",measurement," cm, PASS" if measurement>0 else " cm, FAIL")
		import time
		while(is_stream):
			measurement=lidar.simple_measure()
			print("Measurement: ",measurement," cm")
			time.sleep(1.0/lidar.SAMPLING_FREQUENCY_HZ)
		
if __name__ == "__main__":
	print("START")
	is_loop=True
	Lidar.build_test(is_loop)
	print("DONE")
