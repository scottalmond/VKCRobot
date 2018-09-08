TEST_VIDEO_IN=False;
TEST_SINGLE_CAPTURE=False
TEST_CONTINUOUS=True

if(TEST_VIDEO_IN):
	from picamera import PiCamera
	from time import sleep
	camera = PiCamera()
	camera.start_preview(alpha=200)
	camera.start_preview()
	sleep(10)
	camera.stop_preview()

if(TEST_SINGLE_CAPTURE): #https://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
	# import the necessary packages
	from picamera.array import PiRGBArray
	from picamera import PiCamera
	import time
	import cv2
	 
	# initialize the camera and grab a reference to the raw camera capture
	camera = PiCamera()
	rawCapture = PiRGBArray(camera)
	 
	# allow the camera to warmup
	time.sleep(0.1)
	 
	# grab an image from the camera
	camera.capture(rawCapture, format="bgr")
	image = rawCapture.array
	 
	# display the image on screen and wait for a keypress
	cv2.imshow("Image", image)
	cv2.waitKey(0)

	#/usr/lib/python3/dist-packages/picamera/encoders.py:544: PiCameraResolutionRounded: frame size rounded up from 1920x1080 to 1920x1088
	#  width, height, fwidth, fheight)))

	#** (Image:3971): WARNING **: Error retrieving accessibility bus address: org.freedesktop.DBus.Error.ServiceUnknown: The name org.a11y.Bus was not provided by any .service files

if(TEST_CONTINUOUS):
	# import the necessary packages
	from picamera.array import PiRGBArray
	from picamera import PiCamera
	import time
	import cv2
	 
	# initialize the camera and grab a reference to the raw camera capture
	camera = PiCamera()
	camera.resolution = (640, 480) #(320, 240)
	camera.framerate = 32
	#rawCapture = PiRGBArray(camera, size=(640, 480))
	rawCapture = PiRGBArray(camera, size=camera.resolution)
	 
	# allow the camera to warmup
	time.sleep(0.1)
	 
	# capture frames from the camera
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):#yuv
		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		image = frame.array
	 
		# show the frame
		cv2.imshow("Frame", image)
		key = cv2.waitKey(1) & 0xFF
	 
		# clear the stream in preparation for the next frame
		rawCapture.truncate(0)
	 
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
