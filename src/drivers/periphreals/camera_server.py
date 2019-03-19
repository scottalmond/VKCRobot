#important URLs:
#http://192.168.1.113:8000/stream.mjpg
#http://192.168.1.113:8000/prev_view.html
#http://192.168.1.113:8000/next_view.html
#http://192.168.1.113:8000/brighter.html
#http://192.168.1.113:8000/dimmer.html

# in virtual env, python qr.py
# on browser, http://192.168.1.100:8000

# Overview
# Read from picamera, capture video and frames in CV arrays and byte strings
# CV array is used in QR detection and dimension detection
# byte string is used in updating web page

# Development Environment
# Raspian Stretch
# Python version 3.5.3

# Additional libraries
# sudo apt-get install libzbar
# pip install requirements.txt
# scipy
# numpy
# imutils
# picamera[array]
# pyzbar

# may have to uninstall current picamera
# sudo apt-get remove python-picamera python3-picamera
# pip install "picamera[array]"

# References
# QR detection:
# https://www.pyimagesearch.com/2018/05/21/an-opencv-barcode-and-qr-code-scanner-with-zbar/
# Dimension and shape detection:
# https://www.pyimagesearch.com/2016/03/28/measuring-size-of-objects-in-an-image-with-opencv/
# Web Server:
# https://picamera.readthedocs.io/en/release-1.13/recipes2.html#web-streaming

import io
import time
import logging
import socketserver
from threading import Thread
from threading import Condition
from http import server
import copy

import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
from pyzbar import pyzbar #10/13 temp fix, need to SUDO install pyzbar...

import numpy as np
import imutils
from imutils import perspective
from imutils import contours
from scipy.spatial import distance as dist


PAGE = """\
<html>
<head> <title>R2DAG Live Feed</title> </head>
<body>
<h1>R2DAG Live Feed</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

PAGE_LESS="""\
<html>
<head> <title>R2DAG Live Feed</title> </head>
<body>
<h1>R2DAG Live Feed</h1>
<h2>PLACEHOLDER</h2>
</body>
</html>
"""

REFERENCED_WIDTH = 1.0
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Contour:
	def __init__(self):
		pass
	
	def auto_canny(self, image, sigma=0.33):
	
		# compute the median of the single channel pixel intensities
		v = np.median(image)

		# apply automatic Canny edge detection using the computed median
		lower = int(max(0, (1.0 - sigma) * v))
		upper = int(min(255, (1.0 + sigma) * v))
		edged = cv2.Canny(image, lower, upper)

		return edged

	def getEdgeContours(self, image, sigma):

		# convert to grayscale and blur it slightly
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		# blurred = cv2.GaussianBlur(gray, (7, 7), 0)
		blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	

		# perform edge detection using Canny algorithm
	
		# example = cv2.Canny(blurred, 50, 100)
		# wide = cv2.Canny(blurred, 10, 200)
		# tight = cv2.Canny(blurred, 225, 250)
		edged = self.auto_canny(blurred, sigma)
	
		# perform a dilation + erosion to close gaps in between object edges
		edged = cv2.dilate(edged, None, iterations=1)
		edged = cv2.erode(edged, None, iterations=1)

		# find contours in the edge map
		edgeContours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		edgeContours = edgeContours[1] # if imutils.is_cv2() edgeContours[0] else edgeContours[1]

		# sort the contours from left-to-right
		(edgeContours, _) = contours.sort_contours(edgeContours)
	
		return edgeContours

class Box:
	
	def __init__(self, contour):
		
		self.box = None
		
		self.topPt = []
		self.rightPt =[]
		self.bottomPt = []
		self.leftPt = []

		self.dimA = None
		self.dimB = None
		
		# compute the rotated bounding box of the contour
		self.box = cv2.minAreaRect(contour)
		self.box = cv2.boxPoints(self.box) # if imutils.is_cv2() cv2.cv.BoxPoints(box) else cv2.boxPoints(box)
		self.box = np.array(self.box, dtype="int")

		# order the points in the contour such that they appear
		# in top-left, top-right, bottom-right, and bottom-left order
		self.box = perspective.order_points(self.box)
		
		# unpack the ordered bounding box
		(tl, tr, br, bl) = self.box
		
		self.topPt = self.midpoint(tl, tr) # clockwise side1, top left-right
		self.rightPt = self.midpoint(tr, br) # side2, top right-bottom right
		self.bottomPt = self.midpoint(bl, br) # side3, bottom left-right
		self.leftPt = self.midpoint(tl, bl) # side4, top left-bottom left
	  
	def midpoint(self, ptA, ptB):
		return ( int( (ptA[0] + ptB[0]) * 0.5 ), int( (ptA[1] + ptB[1]) * 0.5 ) )
	
		
	def setDimension(self, pixelRatio = None):
		
		# compute the Euclidean distance between the midpoints
		dA = dist.euclidean(self.topPt, self.bottomPt)
		dB = dist.euclidean(self.leftPt, self.rightPt)

		if pixelRatio == None:
			pixelRatio = dB / REFERENCED_WIDTH
		
		self.dimA = dA / pixelRatio
		self.dimB = dB / pixelRatio
		
		#return so all boxes will have the same pixel ratio as the referenced box
		return pixelRatio
	
	def draw(self, image, id):

		cv2.drawContours(image, [self.box.astype("int")], -1, GREEN, 2)

		if id == 1:
			lineColor = RED
			boxName = "(Ref"
			sizeColor = WHITE
		else:
			lineColor = GREEN
			boxName = "("
			sizeColor = BLACK
			
		cv2.line(image, self.topPt, self.bottomPt, GREEN, 2)
		cv2.line(image, self.leftPt, self.rightPt, lineColor, 2)

		(x, y) = self.topPt
		(x2,y2) = self.rightPt
		
		if self.dimA == None:
			print("need to call setDimension prior")
			return image
		
		cv2.putText(image, "({:d}) {:.1f}".format(id, self.dimA),
			(x - 15, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, BLACK, 2)
		cv2.putText(image, "{:s}{:d}) {:.1f}".format(boxName, id, self.dimB),
			(x2 + 10, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.65, sizeColor, 2)
		 
		return image
 
	
	def getBox(self):
		return self.box
	
	def getTopPt(self):
		return self.topPt
	
	def getBottomPt(self):
		return self.bottomPt
	
	def getLeftPt(self):
		return self.leftPt
		
	def getRightPt(self):
		return self.rightPt
	
	def getDimA(self):
		return self.dimA
	
	def getDimB(self):
		return self.dimB
	

class Detection:
	
	def __init__(self):
		self.qrFound = []
		self.qr_priority_queue=[]
	
	def getDimension(self, image):
		
		contour = Contour()
		edgeContours = contour.getEdgeContours(image, sigma = .50)
		
		id = 0
		pixelRatio = None
	
		# loop over the contours individually
		for c in edgeContours:
	
			# if the contour is not sufficiently large, ignore as noise
			if cv2.contourArea(c) < 1000:
				continue
		
			id = id + 1
		
			box = Box(c)
			
			# the first box, top left box, sets the reference pixel ratio for subsequent boxes
			# actual dimension = displayed dimension * actual width of reference box
			pixelRatio = box.setDimension(pixelRatio) 
			image = box.draw(image, id)

		return image

	# convenient wrapper for cv.putText
	def putText(self, str, image, x=400, y=30):

		bottomLeftCornerOfText = (x, y)
		font = cv2.FONT_HERSHEY_SIMPLEX
		fontScale = .5
		fontColor = BLACK
		lineType = 2

		cv2.putText(image, "{:>s}".format(str), bottomLeftCornerOfText,font,fontScale,fontColor,lineType)
		return image

	def addQrTextToCorner(self, image):
		image = self.putText(time.asctime(time.localtime()),image)
	
		x = 400
		y = 30
		counter = 0
		
		for qrText in self.qrFound:
			y = y + 30
			counter = counter + 1
			image = self.putText("{:d}: {:s}".format(counter, qrText), image, x, y)
			
		return image

	def getQr(self, image):

		# find all QRs in the frame
		qrs = pyzbar.decode(image)
		for qr in qrs:

			# extract the bounding box location of the QR
			(x, y, w, h) = qr.rect

			# draw the bounding box in the frame
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

			# convert binary to text string
			qrText = qr.data.decode("utf-8")

			# draw the QR text in the frame
			cv2.putText(image, qrText, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)

			# save (unique) QR text
			#if qrText not in self.qrFound:
			#	self.qrFound.append(qrText)
			self.foundQr(qrText)
						
		#image = self.addQrTextToCorner(image)
		return image
		
	#string, timestamp_seconds
	def foundQr(self,qrText):
		already_exists=False
		for qr_line in self.qr_priority_queue:
			if(qr_line["string"]==qrText):
				already_exists=True
				qr_line["time_seconds"]=time.time()
				#qr_line["live"]=True #is in view for the current frame, may not be used...
		if(not already_exists):
			self.qr_priority_queue.append({"string":qrText,"time_seconds":time.time()})#,"live":True
		
	#get Qrs with most recently found on top (index 0)
	def getQrList(self):
		deletable_copy=copy.deepcopy(self.qr_priority_queue)
		out_list=[]
		while(len(deletable_copy)>0):
			min_found=None
			for qr_entry in deletable_copy:
				if(min_found is None or qr_entry["time_seconds"]>min_found["time_seconds"]):
					min_found=qr_entry
			deletable_copy.remove(min_found)
			out_list.append(min_found)
		return out_list

# Web Server
class StreamingHandler(server.BaseHTTPRequestHandler):

	def do_GET(self):
		

		if self.path == '/':
			self.send_response(301)
			self.send_header('Location', '/index.html')
			self.end_headers()

		elif self.path =="/index.html":

			content = PAGE.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
			
		elif self.path =="/prev_view.html":

			streamVideo.view_manager.changeView(False)
			content = PAGE_LESS.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
			
		elif self.path =="/next_view.html":

			streamVideo.view_manager.changeView(True)
			content = PAGE_LESS.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)

		elif self.path =="/brighter.html":

			streamVideo.set_shutter(True)
			content = PAGE_LESS.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
			
		elif self.path =="/dimmer.html":

			streamVideo.set_shutter(False)
			content = PAGE_LESS.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
			
		elif self.path =="/invert.html":

			streamVideo.invert_colors=not streamVideo.invert_colors
			content = PAGE_LESS.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
		
			
		elif self.path == '/stream.mjpg':
			self.send_response(200)
			self.send_header('Age', 0)
			self.send_header('Cache-Control', 'no-cache, private')
			self.send_header('Pragma', 'no-cache')
			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
			self.end_headers()
			try:
				
				while True:
					
					#get image to show to controller
					streamVideo.view_manager.flush() #clear stale backlog of images
					view_selection=streamVideo.view_manager.get_view_selection()
					image=None #output image to video stream
					
					
					if(view_selection in [VIEW_TYPE.CAMERA_STANDARD,VIEW_TYPE.CAMERA_QR]):
					
						#logging.warning("A: "+str(view_selection))
					
						# wait for new image frame
						with streamVideo.condition:
							streamVideo.condition.wait()
							image = streamVideo.read()

						image=cv2.rotate(image,rotateCode=cv2.ROTATE_90_CLOCKWISE)
							
						if(streamVideo.invert_colors):
							image=cv2.bitwise_not(image)
							
						if(view_selection==VIEW_TYPE.CAMERA_QR):
							image = detection.getQr(image)
						#if streamVideo.isEdgeDetection():
						#	image = detection.getDimension(image)

						if(streamVideo.isShowCv()):
							cv2.imshow("Image", image)
							
						image=cv2.resize(image,streamVideo.output_resolution) #downconvert for transmission to controller
					else:
						#logging.warning("B: "+str(view_selection))
						
						image=streamVideo.view_manager.peek(view_selection)
						time.sleep(0.1)#rate limit FPS
						
					#if acquired image exists, show to user
					if(not image is None):
						# for web streaming, convert CV array to byte string
						imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
						img_str = cv2.imencode('.jpg', imgRGB)[1].tostring()

						self.wfile.write(b'--FRAME\r\n')
						self.send_header('Content-Type', 'image/jpeg')
						self.send_header('Content-Length', len(img_str))
						self.end_headers()
						self.wfile.write(img_str)
						self.wfile.write(b'\r\n')

					if streamVideo.isShowCv():
						# CV display won't stay up without this wait
						key = cv2.waitKey(1) & 0xFF
						if key == ord("q"):
							break

			except Exception as e:
				logging.warning('Removed streaming client %s: %s',self.client_address, str(e))
		else:
			self.send_error(404)
			self.end_headers()

# Web server thread
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
	allow_reuse_address = True
	daemon_threads = True

class VideoStream:
	#native resolution is the resolution of the raw camera feed
	#output_resolution is what gets braodcast out over wifi
	def __init__(self, native_resolution=(640,480),output_resolution=(400, 480), framerate=24):
		# initialize the camera and stream
		self.condition = Condition()
		self.camera = PiCamera()
		self.camera.resolution = native_resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera, size=native_resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)
		self.output_resolution=output_resolution
		self.view_manager=ViewManager()
		self.set_shutter_speed(0)

		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False
		self.showCvFlag = False
		self.edgeDetectionFlag = False
		self.invert_colors=False

	def set_shutter_speed(self,value):
		#150 to 1e6/fps
		#logging.warning("C: "+str(value))
		value=int(value)
		#print("SHUTTER: ",value)
		#print("SHUTTER: ",type(value))
		self.camera.shutter_speed=value
		
	def get_shutter_speed(self):
		return self.camera.shutter_speed
		
	def get_exposure_speed(self):
		return self.camera.exposure_speed
		
	#is_inc: boolean to set increase shutter delay to take longer exposure pics
	def set_shutter(self,is_inc):
		if(is_inc is None):
			self.set_shutter_speed(0)#reset to auto
		new_speed=self.get_exposure_speed()*(1.5 if is_inc else 0.5)
		self.set_shutter_speed(int(new_speed))
		#preset_list=[0]
		#latest_val=150
		#preset_scale=1.5
		#while(latest_val<100000):
		#	preset_list.append(latest_val)
		#	latest_val=int(latest_val*preset_scale)
		#if(is_inc):
		#	index=preset_list.index(self.get_shutter_speed())
		#	index+=1 if is_inc else -1
		#	index=np.clip(index,0,len(preset_list))
		#	new_shutter_speed=preset_list[index]
		#	self.set_shutter_speed(new_shutter_speed)

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# capture, clear the stream, then notify everyone to read
			with self.condition:
				self.frame = f.array
				self.rawCapture.truncate(0)
				self.condition.notify_all()

			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

	def setShowCvFlag(self, flag = True):
		self.showCvFlag = flag
	def isShowCv(self):
		return self.showCvFlag

	def setEdgeDetectionFlag(self, flag = True):
		self.edgeDetectionFlag = flag
	def isEdgeDetection(self):
		return self.edgeDetectionFlag
		
#given a user command, changes which view is displayed to the user:
#allows for query of latest image data for a given view
#allows allows input (un-sync multi-thread) of images from other threads
from enum import Enum #for View type
import queue as queue

class VIEW_TYPE(Enum):
	CAMERA_STANDARD=0 #simple pipe from camera to controller
	CAMERA_QR=1 #QR code parsing
	PLAYFIELD=2 #robot position, obstacle location
	DEPTH_MAP=3 #2D depth map from robot POV

class ViewManager:
	def __init__(self,default_view=None):
		self.curr_view=VIEW_TYPE.CAMERA_STANDARD if default_view is None else default_view
		self.queues={}
		for queue_pointer in list(VIEW_TYPE):
			self.queues[queue_pointer]=queue.Queue()#FIFO
		
	def get_view_selection(self):
		return self.curr_view
		
	#user command to increment view or decrement view
	#is_inc is boolean for is_increment
	def changeView(self,is_inc):
		enum_list=list(VIEW_TYPE)
		curr_index=enum_list.index(self.curr_view)
		curr_index+=1 if is_inc else -1
		if(curr_index<0):
			curr_index=len(enum_list)-1
		elif(curr_index>(len(enum_list)-1)):
			curr_index=0
		self.curr_view=enum_list[curr_index]
		
	def push(self,view_target,image):
		if(image is None):
			return
		if(type(view_target)==type(1)):
			view_target=VIEW_TYPE(view_target)
		self.queues[view_target].put(image)
		
	#returns image for the given view
	#if none avaialble, returns None
	def peek(self,view_target):
		this_queue=self.queues[view_target]
		if(this_queue.qsize()<=0):
			return None
		return this_queue.queue[0]
		
	#pop elements off the all queues so there is only one element at most in each (reduce RAM usage to store images...)
	def flush(self):
		for queue_pointer in list(VIEW_TYPE):
			this_queue=self.queues[queue_pointer]
			while(this_queue.qsize()>1):
				this_queue.get_nowait()#push oldest iamge to dev/null
		

# main
class CameraManager(Thread):
	def __init__(self):
		Thread.__init__(self)
		frames_per_second=10
		global streamVideo
		upscale=2
		streamVideo = VideoStream((int(480*upscale),int(400*upscale)),(480,400),frames_per_second).start()
		
		self.view_manager=streamVideo.view_manager
		
		streamVideo.setShowCvFlag(False)
		streamVideo.setEdgeDetectionFlag(False)
		#streamVideo.view_manager.changeView(False)#decrement backwards

		time.sleep(2)
		self.exposure_ui_setting=0#0 to 1 per user selection

		global detection
		detection = Detection()
		
		
	def run(self):
		# web streaming is on another thread
		try:
			address = ('192.168.1.113', 8000)
			server = StreamingServer(address, StreamingHandler)
			server.serve_forever()
		finally:
			streamVideo.stop()
		
	def update(self,command_list):
		for command in command_list:
			if(command["target"]=="VIEW"):
				self.command_change_video_feed(command["is_inc"])
			elif(command["target"]=="CAMERA"):
				if(command["command"]=="exposure"):
					if(command["value"]=="auto"):
						self.command_set_exposure(True,0)
					else:
						self.command_set_exposure(False,command["value"])
				elif(command["command"]=="invert"):
					streamVideo.invert_colors=not streamVideo.invert_colors
	
	#bool is_auto exposure
	#int value 0 to 1 for min to max exposure (may be parsed as logarithmic...)			
	def command_set_exposure(self,is_auto,value):
		if(is_auto):
			streamVideo.set_shutter_speed(0)
			self.exposure_ui_setting=0
		else:
			log_value=np.interp(value,[0,0.25,0.5,0.75,1.0],[150,1e3,1e4,1e5,1e6])
			streamVideo.set_shutter_speed(log_value)
			self.exposure_ui_setting=value
		
	#change which view is presented to the user
	def command_change_video_feed(self,is_increase):
		#print("CameraManager.command_change_video_feed not implemented")
		streamVideo.view_manager.changeView(is_increase)
		
	#qr codes found
	def popStatus(self):
		return {"camera":{"qr_list":detection.getQrList(),
						  "exposure":self.exposure_ui_setting,
						  "is_invert":streamVideo.invert_colors},
				"view":streamVideo.view_manager.curr_view.name
				}
	
	def dispose(self):
		pass
		



if __name__ == "__main__":
	
	print("START")
	
	camera_manager=CameraManager()
	camera_manager.start()
		
	print("DONE")

