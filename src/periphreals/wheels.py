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
python3 wheels.py

gpio readall

Connections:

+5V @ module to +3.3V @ Rpi (needed because +5V source will make the smitt trigger not work or something)
GND to GND
52pi.cn IO17 (yellow), wpi 0, bcm 17, phys 11 --> INA
52pi.cn IO18 (green), wpi 1, bcm 18, pyhs 12 --> INB


"""

class Wheels:

	WHEEL_PINS={"front_right":[0,1]} #forward,reverse pins, 1 is ON/enabled, 0/False is stop

	def __init__(self):
		import wiringpi as wpi
		self.wpi=wpi 
		self.initInterface()

	def initInterface(self):
		self.wpi.wiringPiSetup()
		for wheel_name,wheel_pins in self.WHEEL_PINS.items():
			for pin in wheel_pins:
				self.wpi.pinMode(pin,self.wpi.OUTPUT)

	#speed >0 is forward, speed <0 is negative, 0 is stop
	# speed units...
	def setState(self,wheel_name,speed):
		#TODO check if wheel name value
		#TODO check if speed value, units, PWM...
		print("SET ",self.WHEEL_PINS[wheel_name][0]," to ",1 if speed>0 else 0)
		print("SET ",self.WHEEL_PINS[wheel_name][1]," to ",1 if speed<0 else 0)
		self.wpi.digitalWrite(self.WHEEL_PINS[wheel_name][0],1 if speed>0 else 0)
		self.wpi.digitalWrite(self.WHEEL_PINS[wheel_name][1],1 if speed<0 else 0)

	@staticmethod
	def build_test(is_loop):
		print("Wheels Build Test...")
		import time
		print("Init Wheels...")
		wheels=Wheels()
		speed_list=[-1,0,1,0]
		while(is_loop):
			for speed in speed_list:
				wheel_name="front_right"
				print("Set ",wheel_name," to speed: ",speed)
				wheels.setState("front_right",speed)
				time.sleep(2)
		
		
if __name__ == "__main__":
	print("START")
	is_loop=True
	Wheels.build_test(is_loop)
	print("DONE")
