import time

from drivers.periphreals.pwm import PWM
from drivers.periphreals.discrete import Discrete

pwm=PWM()

if(True):
	pwm.dispose()
else:
	servo_list=[6,7,0,1,2,3,4,5,6,7]
	for servo_channel in servo_list:
		for angle_degrees in [80,100,90]:
			print('PWM set servo: ',servo_channel,' to ',angle_degrees,' degrees')
			pwm.set_servo(servo_channel,angle_degrees)
			time.sleep(2)


	discrete=Discrete()
	wheel_list=[Discrete.FRONT_LEFT,Discrete.REAR_LEFT,Discrete.FRONT_RIGHT,Discrete.REAR_RIGHT]
	dimmer_list=[8,9,10,11]
	dim_level_list=[1.0,0.9,0.3,0.1,0.0]
	full_run=[{"speed":1.0,"level":dim_level_list},
			  {"speed":0.0,"level":[1.0]},
			  {"speed":-1.0,"level":dim_level_list},
			  {"speed":0.0,"level":[0.0]}]
	for rep in range(6):
		for idx in range(4):
			wheel_name=wheel_list[idx]
			dimmer_channel=dimmer_list[idx]
			for line in full_run:
				speed=line["speed"]
				discrete.setState(wheel_name,speed)
				for dim_level in line["level"]:#3.3V, 2.97V, 0.99V, 0.33V, 0.0V
					print('PWM set channel: ',dimmer_channel,' to ',int(dim_level*1000)/10.0,' %')
					discrete.setState(wheel_name,speed)
					pwm.set_dimmer(dimmer_channel,dim_level)
					time.sleep(2)

	pwm.dispose()
