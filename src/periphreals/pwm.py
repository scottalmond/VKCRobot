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
Command LittleArm Big, and camera mount, servos

Usage:

troubleshoot i2c device addresses:
i2cdetect -y 1

run main program:
python3 pwm.py



Connections:
servos on channels 0 and 1 on PWM Adafruit HAT
brown wire is GND
red is VCC
orange is signal

connect signal pin from PWM channel 3 to ENABLE pin on h-bride
other h-bridge connections are per wheels.py


"""

class PWM:
	
	PWM_FREQUENCY_HZ=60 #frequency at which updates are sent to servo
	I2C_ADDRESS=0x40
	I2C_REGISTER_MODE1=0x00
	I2C_REGISTER_PRESCALE=0xFE
	I2C_REGISTER_LED0_ON_L = 0x06
	I2C_REGISTER_LED0_ON_H = 0x07
	I2C_REGISTER_LED0_OFF_L = 0x08
	I2C_REGISTER_LED0_OFF_H = 0x09
	
	def __init__(self):
		self.initInterface()
		
	def initInterface(self):
		import wiringpi as wpi
		self.wpi=wpi
		self.wpi.wiringPiSetupPhys()
		self.file_descriptor=wpi.wiringPiI2CSetup(self.I2C_ADDRESS)
		self.set_pwm_freq(self.PWM_FREQUENCY_HZ)
		
	def set_pwm_freq(self, freq_hz):
		import math
		import time
		#paragraph 7.3.5, PCA9685.pdf
		prescaleval = 25000000.0    # 25MHz
		prescaleval /= 4096.0       # 12-bit
		prescaleval /= float(freq_hz)
		prescaleval -= 1.0
		prescale = int(math.floor(prescaleval + 0.5))
		#paragraph 7.3.1.1, PCA9685.pdf
		#put to sleep so prescale can be written
		oldmode=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_MODE1)
		newmode_3=oldmode | 0x10
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_MODE1, newmode_3)
		#set prescale
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_PRESCALE, prescale)
		#1. read MODE1 register
		oldmode=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_MODE1)
		print("PWM.set_pwm_freq: oldmode: ",bin(oldmode))
		#2. check that bit 7 (RESTART) is a logic 1
		#If it is clear bit 4 (SLEEP)
		newmode = oldmode & 0xEF #1110 1111 --> clear bit 4
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_MODE1, newmode)
		#Allow time for oscillator to stabalize (500 us)
		time.sleep(500.0e-6) #500 us
		#3. write logic 1 to bit 7 of MODE1 register.  All PWM channels will restart and the RESTART bit will clear
		newmode_2 = newmode | 0x80 #1000 0000 --> set bit 4 HIGH
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_MODE1, newmode_2)
		nowmode=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_MODE1)
		print("PWM.set_pwm_freq: now mode: ",bin(nowmode))
		
	def set_pwm_freq_legacy(self, freq_hz): #from adafruit PCA9685.py, modified for wpi
        #"""Set the PWM frequency to the provided value in hertz."""
		import math
		import time
		prescaleval = 25000000.0    # 25MHz
		prescaleval /= 4096.0       # 12-bit
		prescaleval /= float(freq_hz)
		prescaleval -= 1.0
        #logger.debug('Setting PWM frequency to {0} Hz'.format(freq_hz))
        #logger.debug('Estimated pre-scale: {0}'.format(prescaleval))
		prescale = int(math.floor(prescaleval + 0.5))
        #logger.debug('Final pre-scale: {0}'.format(prescale))
        #oldmode = self._device.readU8(MODE1);
		oldmode=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_MODE1)
		print("PWM.set_pwm_freq: oldmode: ",bin(oldmode))
		newmode = (oldmode & 0x7F) | 0x10    # restart
        #self._device.write8(MODE1, newmode)  # go to sleep
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_MODE1, newmode)
        #self._device.write8(PRESCALE, prescale)
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_PRESCALE, prescale)
        #self._device.write8(MODE1, oldmode)
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_MODE1, oldmode)
		time.sleep(0.005) #5 ms wait
        #self._device.write8(MODE1, oldmode | 0x80)
		print("PWM.set_pwm_freq: set mode: ",bin(oldmode | 0x80))
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_MODE1, oldmode | 0x80)
		debugA=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_MODE1)
		print("PWM.set_pwm_freq: newmode: ",bin(debugA))
		
	def set_pwm(self, channel, on_counts, off_counts): #from adafruit PCA9685.py, modified for wpi
		print('PWM.set_pwm: channel ',channel,' set to ON_counts: ',on_counts,', OFF_counts: ',off_counts)
		print('PWM.set_pwm: register ',hex(self.I2C_REGISTER_LED0_ON_L+4*channel),', value: ',hex(on_counts & 0xFF))
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_LED0_ON_L+4*channel, on_counts & 0xFF)
		print('PWM.set_pwm: register ',hex(self.I2C_REGISTER_LED0_ON_H+4*channel),', value: ',hex(on_counts >> 8))
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_LED0_ON_H+4*channel, on_counts >> 8)
		print('PWM.set_pwm: register ',hex(self.I2C_REGISTER_LED0_OFF_L+4*channel),', value: ',hex(off_counts & 0xFF))
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_LED0_OFF_L+4*channel, off_counts & 0xFF)
		print('PWM.set_pwm: register ',hex(self.I2C_REGISTER_LED0_OFF_H+4*channel),', value: ',hex(off_counts >> 8))
		self.wpi.wiringPiI2CWriteReg8(self.file_descriptor,self.I2C_REGISTER_LED0_OFF_H+4*channel, off_counts >> 8)
		#debug=self.wpi.wiringPiI2CReadReg8(self.file_descriptor,self.I2C_REGISTER_LED0_OFF_H+4*channel)
		#print("PWM.set_pwm: debug: ",hex(debug))
		
	#given an angle between 0 and 180, set the PWM control for the servo
	# equates to 150 to 600 ON out of 4096 OFF, with 4096 running at ~50 Hz
	def set_servo(self,channel,angle_degrees):
		ratio=angle_degrees/180.0
		servo_min=150
		servo_max=600
		counts=int(ratio*(servo_max-servo_min)+servo_min)
		self.set_pwm(channel,0,counts)
	
	#given a ratio between 0 and 1, set the PWM output to
	# some fraction of 4096
	def set_dimmer(self,channel,ratio):
		if(ratio<=0.0): #special values when ALL ON or ALL OFF
			self.set_pwm(channel,0,4096)
		elif(ratio>=1.0):
			self.set_pwm(channel,4096,0)
		else:
			self.set_pwm(channel,0,int(4096*ratio))#int varies between [0,4096)
	
	@staticmethod
	def build_test(loop_count):
		print("PWM Build Test...")
		print("Instantiate PWM class...")
		pwm=PWM()
		print("PWM file_descriptor: ",pwm.file_descriptor)
		print("Run movement test...")
		import time
		servo_list=[0,1]
		dimmer_list=[2,3]
		while(not loop_count==0):
			for servo_channel in servo_list:
				for angle_degrees in [0,180,90]:
					print('PWM actuate channel: ',servo_channel,' to ',angle_degrees,' degrees')
					pwm.set_servo(servo_channel,angle_degrees)
					time.sleep(2)
			for dimmer_channel in dimmer_list:
				for dim_level in [1.0,0.9,0.3,0.1,0.0]:#3.3V, 2.97V, 0.99V, 0.33V, 0.0V
					pwm.set_dimmer(dimmer_channel,dim_level)
					time.sleep(2)
			loop_count-=1


if __name__ == "__main__":
	print("START")
	loop_count=1
	PWM.build_test(loop_count)
	print("DONE")
