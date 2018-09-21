from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

class Camera:
	PICTURE_PATH='/home/pi/Documents/pics/'
	
	def __init__(self):
			self.camera = PiCamera()
			self.camera.resolution=(1640,1232)
			#self.rawCapture = PiRGBArray(self.camera)
			 
			# allow the camera to warmup
			#time.sleep(0.1)
		
	def snapshot(self):
		#self.camera.capture(self.rawCapture, format="bgr")
		#image = self.rawCapture.array
		filename=self.PICTURE_PATH+str(int(time.time()))+".jpg"
		#cv2.imwrite(filename,image)
		self.camera.capture(filename)
		

if __name__ == "__main__":
	print("START")
	cam=Camera()
	cam.snapshot()
	print("DONE")
