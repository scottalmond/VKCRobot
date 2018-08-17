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
Queries magnetometer for heading

Usage:
print all i/o from rpi:
gpio readall

print i2c devices:
gpio i2cd

run main program:
python3 magnetometer.py




VCC to 5V
GND
SDA blue/white to: BCM 2, wPi 8, Phys 3
SCL yellow to: BCM 3, wPi 9, Pys 5


"""

class IMU:

	#class constants
	IMU_ADDRESS_I2C=0x68
	IMU_REGISTER_WHO_AM_I=0x75

	def __init__(self):
		import wiringpi as wpi
		self.wpi=wpi
		self.file_descriptor=self.initInterface()
		
	#configure the IMU with default settings
	#returns wiringpi pointer to IMU device
	#returns None if device fails to initialize
	def initInterface(self):
		wpi=self.wpi
		file_descriptor=wpi.wiringPiI2CSetup(self.IMU_ADDRESS_I2C)
		#TODO, configure magnetomter...
		return file_descriptor

	#queries WHO AM I register
	def whoAmI(self):
		return self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.IMU_REGISTER_WHO_AM_I)

	#queries the MPU-9250A I2C device for magnetic field measurements
	#combines the measurements from the horizontal plane into a
	#singular DOUBLE measuring degrees [0-360) clockwise from magnetic North
	def getHeading(self):
		wpi=self.wpi
		imu_pointer=self.file_descriptor
		#TODO, implement code to fetch reading and convert to degrees CW from north
		return -1.0
		
	@staticmethod
	def build_test():
		print("IMU Build Test...")
		imu=IMU()
		print("File Descriptor Opened: ","PASS" if imu.file_descriptor>=0 else "FAIL")
		print("Who am I Test: ","PASS" if 0x71==imu.whoAmI() else "FAIL")
		print("Magnetic Heading: ",imu.getHeading())

if __name__ == "__main__":
	print("START")
	IMU.build_test()
	print("DONE")
