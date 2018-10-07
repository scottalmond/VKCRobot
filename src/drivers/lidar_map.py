#collects data in two modes:
#1. basic left-right scan back and forth (pan servo only: done while roving around play field)
#2. 2D scan using pan-tilt servos

import numpy as np
import cv2
from periphreals.pwm import PWM
from periphreals.lidar import Lidar
import time

PAN_SERVO_CHANNEL=6
TILT_SERVO_CHANNEL=7

PAN_LIMIT_DEGREES=[50,150] #37
TILT_LIMIT_DEGREES=[60,120] #30
#can do about 275 steps per second (3.6 ms per measurement with no delay, just rpi overhead)
#so 4 seconds is 1100 measurements
PAN_STEP_DEGREES=2 #horizontal, cols
TILT_STEP_DEGREES=1 #vertical, rows

pan_list=np.arange(PAN_LIMIT_DEGREES[0],PAN_LIMIT_DEGREES[1],PAN_STEP_DEGREES)
tilt_list=np.arange(TILT_LIMIT_DEGREES[0],TILT_LIMIT_DEGREES[1],TILT_STEP_DEGREES)

pwm=PWM()
lidar=Lidar()

raw_measurement_slew_list=np.zeros((len(pan_list)*len(tilt_list),3))
slew_index=0

start_time=time.time()

is_reverse_tilt=False
for pan_index in range(len(pan_list)):
	pan_degrees=pan_list[pan_index]
	pwm.set_servo(PAN_SERVO_CHANNEL,pan_degrees)
	tilt_index_list=np.arange(0,len(tilt_list))
	if(is_reverse_tilt):
		tilt_index_list=tilt_index_list[::-1]
	for tilt_id in range(len(tilt_list)):
		tilt_index=tilt_index_list[tilt_id]
		tilt_degrees=tilt_list[tilt_index]
		pwm.set_servo(TILT_SERVO_CHANNEL,tilt_degrees)
		lidar_measure=lidar.simple_measure()
		print(pan_degrees,", ",tilt_degrees,", ",lidar_measure)
		#raw_measurement_array[pan_index,tilt_index]=lidar_measure
		raw_measurement_slew_list[slew_index,:]=[pan_index,tilt_index,lidar_measure]
		slew_index+=1
		#time.sleep(0.01)
	is_reverse_tilt=not is_reverse_tilt
		
end_time=time.time()

	
pwm.dispose()
SLEW_PADDING=-12#allow for latency in slew operation by sapling x times extra at edges

raw_measurement_array=np.zeros((len(tilt_list),len(pan_list)))
for slew_iter in range(len(raw_measurement_slew_list)):
	slew_iter_inner=slew_iter+SLEW_PADDING
	slew_iter_inner=np.clip(slew_iter_inner,0,len(raw_measurement_slew_list)-1)
	slew_row_target=raw_measurement_slew_list[slew_iter_inner,:]
	slew_row=raw_measurement_slew_list[slew_iter,:]
	#print(slew_row)
	#print(int(slew_row[0]))
	#print(int(slew_row[1]))
	#print(slew_row[2])
	raw_measurement_array[int(slew_row_target[1])][int(slew_row_target[0])]=slew_row[2]

#refactor from various distance measurements into a full-range scaled (+/- limits are 3 sigma)
measurement_list=raw_measurement_array.tolist()
low_percentile=np.percentile(measurement_list,16)
median=np.percentile(measurement_list,50)
high_percentile=np.percentile(measurement_list,84)

print("Lower percentile: ",low_percentile)
print("median: ",median)
print("Higher percentile: ",high_percentile)
sigma=((median-low_percentile)+(high_percentile-median))/2
image=np.zeros((len(raw_measurement_array),len(raw_measurement_array[0]),3),np.uint8)

image_shape=image.shape
full_range=255/(6*sigma)
for row in range(image_shape[0]):
	for col in range(image_shape[1]):
		measurement=raw_measurement_array[row,image_shape[1]-1-col]
		color=128-(measurement-median)*full_range #0 sigma (mean) is at 128, +3 sigma is at 255, -3 sigma at 0
		color=np.uint8(np.clip(color,0,255))
		red=64-(measurement-median)*full_range/2
		blue=128+red
		red=np.uint8(np.clip(red,0,255))
		blue=np.uint8(np.clip(blue,0,255))
		image[row,col,:]=[red,color,blue]
		#print(row,", ",col,", ",color)

blurred = cv2.GaussianBlur(image, (3, 3), 0)
#image_bigger=cv2.resize(blurred,(0,0),fx=8.0,fy=4.0)
image_bigger=cv2.resize(blurred,(400,480))

print("run time seconds: ",(end_time-start_time))

cv2.imshow(str(SLEW_PADDING),image_bigger)
cv2.waitKey(0)
#cv2.destroyAllWindows()

