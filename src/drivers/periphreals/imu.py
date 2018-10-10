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
IMU: MPU-9250

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
import time
import numpy as np
import math

class IMU:

	#class constants
	ADDRESS_I2C_MPU=0x68
	ADDRESS_I2C_AK=0x0C
	REGISTER_INT_PIN_CFG=0x37 #bypass register
	REGISTER_INT_ENABLE = 0x38

	AK8963_14BIT = 0x00
	AK8963_16BIT = (0x01 << 4)
	REGISTER_AK8963_CNTL1=0x0A
	
	REGISTER_WHO_AM_I_MPU=0x75
	REGISTER_WHO_AM_I_AK=0x00
	REGISTER_AK8963_ASAX=0x10
	#REGISTER_AK8963_ASAY=0x11
	#REGISTER_AK8963_ASAZ=0x12
	REGISTER_PWR_MGMT_1=0x6B
	REGISTER_MAGNET_DATA  = 0x03
	AK8963_BIT_14=0x00
	AK8963_BIT_16=0x01
	AK8963_8HZ   = 0x02
	AK8963_100HZ = 0x06
	## Continous data output 100Hz
	AK8963_MODE_C100HZ = 0x06
	DECLINATION_DEGREES=11.8 #magnetic reading - (declination with East as positive) = true north

	def __init__(self):
		import wiringpi as wpi
		self.wpi=wpi
		self.scale=[0,0,0]
		self.file_descriptor=self.initInterface()
		self.configure()
		
	#configure the IMU with default settings
	#returns wiringpi pointer to IMU device
	#returns None if device fails to initialize
	def initInterface(self):
		wpi=self.wpi
		self.file_descriptor_mpu=wpi.wiringPiI2CSetup(self.ADDRESS_I2C_MPU)
		#self.wpi.wiringPiI2CWriteReg8(self.file_descriptor_mpu,self.REGISTER_PWR_MGMT_1, 0x00)  # turn sleep mode off
		#time.sleep(0.2)
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor_mpu,self.REGISTER_INT_PIN_CFG, 0x02)
		#self.wpi.wiringPiI2CWriteReg8(self.file_descriptor_mpu,self.REGISTER_INT_ENABLE, 0x01)
		time.sleep(0.1)
		#without setting the bypass, the magnetometer appears to not exists
		# ... because reasons ...
		
		file_descriptor_ak=wpi.wiringPiI2CSetup(self.ADDRESS_I2C_AK)
		return file_descriptor_ak

	def configure(self): #init registers
		for rep in range(8):
			self.wpi.wiringPiI2CWriteReg8(self.file_descriptor, self.REGISTER_AK8963_CNTL1, 0x00)
		time.sleep(0.1)
		for rep in range(3):
			data = self.wpi.wiringPiI2CReadReg8(self.file_descriptor, self.REGISTER_AK8963_ASAX+rep)
			self.scale[rep]=(data - 128) / 256.0 + 1.0
			print("scale ",rep,": ",self.scale[rep])
			
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor, self.REGISTER_AK8963_CNTL1, 0x16) #0x12

	#queries WHO AM I register, a static value that is the same for every IMU of this model
	def whoAmI(self):
		return self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.REGISTER_WHO_AM_I_AK)

	#queries the MPU-9250A I2C device for magnetic field measurements
	#combines the measurements from the horizontal plane into a
	#singular DOUBLE measuring degrees [0-360) clockwise from magnetic North
	def getHeading(self):
		wpi=self.wpi
		imu_pointer=self.file_descriptor
		#TODO, implement code to fetch reading and convert to degrees CW from north
		
		#print("Status1: ",hex(self.wpi.wiringPiI2CReadReg8(self.file_descriptor,0x02)))
		#print("Status2: ",hex(self.wpi.wiringPiI2CReadReg8(self.file_descriptor,0x09)))
		#print("Control1: ",hex(self.wpi.wiringPiI2CReadReg8(self.file_descriptor,0x0A)))
		#print("Control2: ",hex(self.wpi.wiringPiI2CReadReg8(self.file_descriptor,0x0B)))
		for reg in [0x09]:#[0x02,0x09,0x0A,0x0B]:
			discard=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,reg)
			discard=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,reg)
		
		data=np.zeros(3)
		reg_offset=0
		for dim in range(3):
			reg=self.REGISTER_MAGNET_DATA+2*dim
			low=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,reg)
			high=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,reg+1)
			combo=high<<8|low
			if(combo>=(1<<15)):
				combo-=(1<<16)
			#low=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,reg)
			#temp=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,reg)
			#print(hex(reg),": ",combo)
			data[dim]=combo
		#print("Control1: ",hex(self.wpi.wiringPiI2CReadReg8(self.file_descriptor,0x0A)))
		discard=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,0x0A)
		
		#x = self.conv(data[1], data[0]) * self.scale[0]
		#y = self.conv(data[3], data[2]) * self.scale[1]
		#z = self.conv(data[5], data[4]) * self.scale[2]
		x = data[0] * self.scale[0]
		y = data[1] * self.scale[1]
		z = data[2] * self.scale[2]
		
		#angle=math.atan2(x,y)*180/3.1415
		
		return [x,y,z]
		
	def conv(self, msb, lsb):
		"""
		http://stackoverflow.com/questions/26641664/twos-complement-of-hex-number-in-python
		"""
		value=msb*(1<<8)+lsb
		if(value>=(1<<15)):
			value-=(1<<15)
		#print("value: ",value," < ",(1<<15))
		#value = lsb | (msb << 8)
		# if value >= (1 << 15):
		# 	value -= (1 << 15)
		# print(lsb, msb, value)
		return value
		
	@staticmethod
	def build_test():
		print("IMU Build Test...")
		imu=IMU()
		print("File Descriptor Opened: ","PASS" if imu.file_descriptor>=0 else "FAIL")
		print("Who am I Test: ",hex(imu.whoAmI()),", PASS" if 0x48==imu.whoAmI() else ", FAIL")#71
		while(True):
		#for rep in range(50):
			print("Magnetic Heading: ",imu.getHeading())
			time.sleep(0.1)

if __name__ == "__main__":
	print("START")
	IMU.build_test()
	print("DONE")
