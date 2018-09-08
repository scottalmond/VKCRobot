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
send commands to and reads response from LittleArm Big

Usage:

run main program:
python3 discrete.py

gpio readall

Connections:

+5V @ module to +3.3V @ Rpi (needed because +5V source will make the smitt trigger not work or something)
GND to GND
52pi.cn IO17 (yellow), wpi 0, bcm 17, phys 11 --> INA
52pi.cn IO18 (green), wpi 1, bcm 18, pyhs 12 --> INB


"""

class Discrete:

	FRONT_LEFT="front-left"
	REAR_LEFT="rear-left"
	FRONT_RIGHT="front-right"
	REAR_RIGHT="rear-right"
	#note: must not use I2C pins to avoid conflicts with other devices:
	#https://raspberrypi.stackexchange.com/questions/53326/problem-using-i2c-with-ioctl-and-gpios-with-wiringpi-simultaneously/53330#53330
	#setting wiringpi i2c pins as GPIOs will lock up the interface and require a reboot to clear
	#[forward,reverse] physical pins: 1 is ON/True, 0/False is stop
	WHEEL_PINS={FRONT_LEFT:[7,11], #physcial pin numbers
				REAR_LEFT:[13,15],
				FRONT_RIGHT:[12,16],
				REAR_RIGHT:[18,22],
				}

	def __init__(self):
		import wiringpi as wpi
		self.wpi=wpi 
		self.initInterface()

	def initInterface(self):
		self.wpi.wiringPiSetupPhys()
		for wheel_name,wheel_pins in self.WHEEL_PINS.items():
			for pin in wheel_pins:
				self.wpi.pinMode(pin,self.wpi.OUTPUT)

	#speed >0 is forward, speed <0 is negative, 0 is stop
	# speed units are 0 (stop) to 1.0 (full speed)
	def setState(self,wheel_name,speed):
		#TODO check if wheel name value
		#TODO check if speed value, units, PWM...
		#print("SET ",self.WHEEL_PINS[wheel_name][0]," to ",1 if speed>0 else 0)
		#print("SET ",self.WHEEL_PINS[wheel_name][1]," to ",1 if speed<0 else 0)
		self.wpi.digitalWrite(self.WHEEL_PINS[wheel_name][0],1 if speed>0 else 0)
		self.wpi.digitalWrite(self.WHEEL_PINS[wheel_name][1],1 if speed<0 else 0)

	def dispose(self):
		pass

	@staticmethod
	def build_test(loop_count):
		print("Discrete Build Test...")
		import time
		print("Init Discrete...")
		discrete=Discrete()
		speed_list=[-1.0,0,1.0,0,1.0]
		while(not loop_count==0):
			for wheel_name in [Discrete.FRONT_LEFT,
							   Discrete.REAR_LEFT,
							   Discrete.FRONT_RIGHT,
							   Discrete.REAR_RIGHT
							   ]:
				for speed in speed_list:
					print("Set ",wheel_name," to speed: ",speed)
					discrete.setState(wheel_name,speed)
					time.sleep(2)
			loop_count-=1
		
		
if __name__ == "__main__":
	print("START")
	loop_count=1
	Discrete.build_test(loop_count)
	print("DONE")
