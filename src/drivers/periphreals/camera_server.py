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

import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
from pyzbar import pyzbar

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
            cv2.putText(image, qrText, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # save (unique) QR text
            if qrText not in self.qrFound:
                self.qrFound.append(qrText)
                        
        image = self.addQrTextToCorner(image)
        return image


# Web Server
class StreamingHandler(server.BaseHTTPRequestHandler):

    def do_GET(self):
        
        global detection

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

        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                
                while True:

                    # wait for new image frame
                    with streamVideo.condition:
                        streamVideo.condition.wait()
                        image = streamVideo.read()

                    image = detection.getQr(image)
                    if streamVideo.isEdgeDetection():
                        image = detection.getDimension(image)

                    if streamVideo.isShowCv():
                        cv2.imshow("Image", image)
                    
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
    def __init__(self, resolution=(640, 480), framerate=24):
        # initialize the camera and stream
        self.condition = Condition()
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
        self.showCvFlag = False
        self.edgeDetectionFlag = False

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
        

# main

streamVideo = VideoStream().start()

streamVideo.setShowCvFlag(False)
streamVideo.setEdgeDetectionFlag(False)

time.sleep(2)

detection = Detection()

# web streaming is on another thread
try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    streamVideo.stop()
