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
Streams readings from magnetometer to terminal

MPU-9250A magn is address 0x68

Usage:
print all i/o from rpi
gpio readall

print i2c devices
gpio i2cd

run main program
python3 magnetometer.py




VCC to 5V
GND
SDA blue/white to: BCM 2, wPi 8, Phys 3
SCL yellow to: BCM 3, wPi 9, Pys 5


"""

import wiringpi as wpi

if __name__ == "__main__":
	print("START")
	#wpi.wiringPiSetup()
	device=wpi.wiringPiI2CSetup(0x68)
	#wpi.wiringPiI2CWrite(device,0x75)
	print("Read: ",bin(wpi.wiringPiI2CReadReg8(device,0x75)))
	print("Read: ",hex(wpi.wiringPiI2CReadReg8(device,0x75)))
	
	
	print("DONE")
