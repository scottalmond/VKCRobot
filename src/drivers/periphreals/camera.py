from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

class Camera:
	PICTURE_PATH='/home/pi/Documents/pics/'
	
	def __init__(self):
		self.is_enabled=False
		if(self.is_enabled):
			self.camera = PiCamera()
			#self.camera.resolution=(1640,1232)
			self.camera.resolution=(3280,2464)
			#self.rawCapture = PiRGBArray(self.camera)
			 
			# allow the camera to warmup
			#time.sleep(0.1)
		
	def snapshot(self):
		if(self.is_enabled):
			#self.camera.capture(self.rawCapture, format="bgr")
			#image = self.rawCapture.array
			filename=self.PICTURE_PATH+str(int(time.time()))+".jpg"
			#cv2.imwrite(filename,image)
			self.camera.capture(filename)
		
	#def getFrame(self):#get an image from the camera, convert to 400x480 for display
		
		
	#def processFrame(self,frame,getQR):
	
	#@static_method
	#def build_test():
	#	self.rawCamera=PiRGBArray(self.camera
		

if __name__ == "__main__":
	print("START")
	cam=Camera()
	cam.snapshot()
	print("DONE")
