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
provide human interface to WiFi connection to robot

Usage:

run main program:
python3 .py



Connections:
7" touchscreen 


"""

from periphreals.multitouch.library import ft5406
from periphreals.discrete import Discrete
from periphreals.gui.touchable import Touchable
#from periphreals.camera import Camera
import numpy as np
import copy
#import pygame

class GUI:
	def __init__(self,is_windowed):
		self.__create2Dgraphics(is_windowed)
		self.__createEvents()
		self.outbound_message_queue=[] #packets being sent to robot
		self.is_small_scale=False #pwm step size
		self.SMALL_SCALE_DEGREES=1 #degrees of rotation in one delta move
		self.BIG_SCALE_DEGREES=10
		self.pwm_index=0
		self.pwm = 1
		self.pwm_state=[0,1,2,3,4,5,6,7]
		self.led_state=[False,False,False,False]
		self.MAX_PWM_INDEX=7 #shall be no more than 7
		self.wheels_x=0.0
		self.wheels_y=0.0
		self.link_counter=0
		self.robot_pic_count=0
		self.controller_pic_count=0
		self.__is_alive=True
		self.__createButtons()
		self.tab = 1.0 #Start on view 1
		#print("Create Camera...")
		#self.camera=Camera()
		
	def __createButtons(self):
		self.button_listS={ #Static buttons
			"CLOSE":		 Touchable("RECTANGLE", 590,  20, 20, 20,(255,0,0),"X",(255,255,255),self.pygame,self.screen_2d,self.font),
			#"LINK_STATUS":   Touchable("RECTANGLE",140,  0,100, 40,(0,0,0),"0",(255,255,255),self.pygame,self.screen_2d,self.font),
			"NEXT":         Touchable("RECTANGLE", 700,20,100,50,(255,0,0),"Next -->",(255,255,255),self.pygame,self.screen_2d,self.font),			
			"PREV":         Touchable("RECTANGLE", 400,20, 100,50,(255,0,0),"<-- Prev",(255,255,255),self.pygame,self.screen_2d,self.font),
			#"CAM_COUNT":     Touchable("RECTANGLE",240,340,100,100,(0,0,0),"C#:0 R#:0",(255,255,255),self.pygame,self.screen_2d,self.font)		
			"LEFT_TOP":         Touchable("RECTANGLE", 0,0, 400,240,(100,100,100),"",(255,0,255),self.pygame,self.screen_2d,self.font),
			"LEFT_BOT":         Touchable("RECTANGLE", 0,240, 400,240,(100,100,100),"",(255,0,255),self.pygame,self.screen_2d,self.font),

		}
			
		self.button_list1={ #GUI View 1
			#"CAM_CONTROLLER":Touchable("RECTANGLE", 40,340,100,100,(255,0,0),"PIC C",(255,255,255),self.pygame,self.screen_2d,self.font),
			#"CAM_ROBOT":     Touchable("RECTANGLE",140,340,100,100,(255,0,0),"PIC R",(255,255,255),self.pygame,self.screen_2d,self.font),
			"WHEEL":         Touchable("CIRCLE",   450,90,300,300,(255,0,0),"Motor Controller",(255,255,255),self.pygame,self.screen_2d,self.font),
			#"HOME":			  Touchable("RECTANGLE",420,300,50,50,(0,255,0),"Home",(255,255,255),self.pygame,self.screen_2d,self.font)

			}
			
		self.button_list2={ #GUI View 2
			"PWM_PREV":		Touchable("RECTANGLE", 700,75,100,50,(255,0,0),"PWM Next",(255,255,255),self.pygame,self.screen_2d,self.font),
			"PWM_NEXT":		Touchable("RECTANGLE", 400,75,100,50,(255,0,0),"PWM Prev",(255,255,255),self.pygame,self.screen_2d,self.font),
			"CLEAR":         Touchable("RECTANGLE",   400,130,50,50,(0,0,255),"clear",(255,255,255),self.pygame,self.screen_2d,self.font),
			"HOME":			  Touchable("RECTANGLE",400,190,50,50,(0,255,0),"Home",(255,255,255),self.pygame,self.screen_2d,self.font),
			"LOOP":         Touchable("RECTANGLE",   400,250,50,50,(0,0,255),"loop",(255,255,255),self.pygame,self.screen_2d,self.font),
			"SAVE":         Touchable("RECTANGLE",   400,310,50,50,(0,0,255),"save",(255,255,255),self.pygame,self.screen_2d,self.font)

			}
			
		self.button_list3={ #GUI View 3
			"LED1":         Touchable("RECTANGLE",400,80,50,50,(255,0,0),"LED1",(255,255,255),self.pygame,self.screen_2d,self.font),
			"LED2":         Touchable("RECTANGLE",400,155,50,50,(255,0,0),"LED2",(255,255,255),self.pygame,self.screen_2d,self.font),
			"LED3":         Touchable("RECTANGLE",400,230,50,50,(255,0,0),"LED3",(255,255,255),self.pygame,self.screen_2d,self.font),
			"LED4":         Touchable("RECTANGLE",400,305,50,50,(255,0,0),"LED4",(255,255,255),self.pygame,self.screen_2d,self.font),
			"DEPTH":        Touchable("RECTANGLE",400,360,50,50,(255,0,0),"MAP",(255,255,255),self.pygame,self.screen_2d,self.font),
			"HOLD":         Touchable("RECTANGLE",400,430,50,50,(255,0,0),"HOLD",(255,255,255),self.pygame,self.screen_2d,self.font),
			"QRtext":       Touchable("RECTANGLE",470,170,400,300,(255,0,0),"QR text",(255,255,255),self.pygame,self.screen_2d,self.font),		
			"EXPOSURE":     Touchable("RECTANGLE",470,90,210,70,(255,0,0),"Exposure",(255,255,255),self.pygame,self.screen_2d,self.font),		
			"AUTO":         Touchable("RECTANGLE",690,90,50,70,(255,0,0),"Auto",(255,255,255),self.pygame,self.screen_2d,self.font),		
			"INVERT":          Touchable("RECTANGLE",750,90,50,70,(255,0,0),"Inv",(255,255,255),self.pygame,self.screen_2d,self.font)		

			}
			
		self.pwm_list = {
			"PWM1":         Touchable("RECTANGLE",   480,140,300,300,(0,0,255),"Arm Controller1",(255,255,255),self.pygame,self.screen_2d,self.font),
			"PWM2":         Touchable("RECTANGLE",   480,140,300,300,(0,255,0),"Arm Controller2",(255,255,255),self.pygame,self.screen_2d,self.font),
			"PWM3":         Touchable("RECTANGLE",   480,140,300,300,(255,0,0),"Arm Controller3",(255,255,255),self.pygame,self.screen_2d,self.font),
			}
		for pwm_index in [1,2,3]:
			pwm_string="PWM"+str(pwm_index)
			handle=self.pwm_list[pwm_string]
			self.pwm_list[pwm_string].mark=self.pwm_list[pwm_string].range_to_px([0.5,0.5],[0,1],[0,1])
		
	def __createEvents(self):
		self.touchscreen=ft5406.Touchscreen()
		for touch in self.touchscreen.touches:
			touch.on_press=self.event_press
			touch.on_release=self.event_release
			touch.on_move=self.event_move
		
	def event_press(self,event,touch):
		print("event_release: ",touch.id,", ",touch.position, ", ",self.tab)
		
	def event_release(self,event,touch):
		print("event_release: ",touch.id,", ",touch.position, ", ",self.tab)
		
		for button_name,button_object in self.button_listS.items():
			if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
				print("In bounds of buttons of static view")
				if(button_name=="CLOSE"):
					print("Closing...")
					self.__is_alive=False
				elif(button_name =="NEXT"): #Change to the next tab view
					self.tab_next()	
					button_object.screen.fill(self.pygame.Color("black"))
				elif(button_name=="PREV"): #Change to the prev tab view
					self.tab_prev()
					button_object.screen.fill(self.pygame.Color("black"))
				elif(button_name =="LEFT_TOP"): #gives previous screen
					self.prev_view()	
					button_object.screen.fill(self.pygame.Color("black"))
				elif(button_name=="LEFT_BOT"): #gives next screen 
					self.next_view()
					button_object.screen.fill(self.pygame.Color("black"))	
					
		if(self.tab == 1.0):
			for button_name,button_object in self.button_list1.items():
				if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					if(button_name == "HOME"):
						self.robot_home()
					#if(button_name=="INDEX_DEC"):
					#	self.pwm_change_index(False)
					#elif(button_name=="INDEX_INC"): #look at a different PWM channel
					#	self.pwm_change_index(True)
					#elif(button_name=="PWM_DEG_DEC"): #dec position
					#	self.pwm_change_position(False,False)
					#elif(button_name=="PWM_DEG_INC"): #inc position of pwm
					#	self.pwm_change_position(False,True)
					#elif(button_name=="PWM_DEG_CNTR"): #center
					#	self.pwm_change_position(True,False)
					#elif(button_name=="SCALE_SMALL"): #set step to small size
					#	self.pwm_change_scale(True)
					#elif(button_name=="SCALE_BIG"):
					#	self.pwm_change_scale(False)
					#elif(button_name=="CAM_CONTROLLER"):
					#	self.take_picture(False)
					#elif(button_name=="CAM_ROBOT"):
					#	self.take_picture(True)
					elif(button_name=="WHEEL"):
						self.set_velocity(0,0)
						
		if(self.tab == 2.0):	
			for button_name,button_object in self.button_list2.items():
				if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					if(button_name == "CLEAR"):
						self.clear_arm()
					if(button_name == "SAVE"):
						self.save_arm()
					if(button_name == "LOOP"):
						self.loop_arm()
					if(button_name == "HOME"):
						self.home_arm()
					if(button_name == "PWM_PREV"):
						button_object.screen.fill(self.pygame.Color("black"))
						self.next_pwm()
					if(button_name == "PWM_NEXT"):
						button_object.screen.fill(self.pygame.Color("black"))
						self.prev_pwm()
						
			#for button_name,button_object in self.pwm_list.items():
				#if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					#if(button_name == "PWM1" and self.pwm == 1):
						#print("Send packets for PWM 0 & 1")
						#self.send_pwm01(touch.position[0],touch.position[1])
					#if(button_name == "PWM2" and self.pwm == 2):
						#print("Send packets for PWM 1 & 2")
						#self.send_pwm23(touch.position[0],touch.position[1])
					#if(button_name == "PWM3" and self.pwm == 3):
						#print("Send packets for PWM 3 & 4")	
						#self.send_pwm45(touch.position[0],touch.position[1])
						
		if(self.tab == 3.0):			
			for button_name,button_object in self.button_list3.items():
				if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					if(button_name=="LED1"):
						#self.light1_on()
						self.led_toggle(0)
					elif(button_name == "LED2"):
						#self.light2_on()
						self.led_toggle(1)
					elif(button_name == "LED3"):
						#self.light3_on()
						self.led_toggle(2)
					elif(button_name == "LED4"):
						#self.light4_on()
						self.led_toggle(3)
					elif(button_name == "DEPTH"):
						self.lidar_depth_map()
					elif(button_name == "HOLD"):
						self.lidar_hold()
					elif(button_name == "EXPOSURE"):
						ratio=button_object.scale_to_bounds(touch.position,[0.0,1.0],[0.0,1.0])
						print("EXPOSURE: touch: ",touch.position,", ratio: ",ratio)
						self.set_exposure(ratio[0])
					elif(button_name == "AUTO"):
						self.auto_light()
					elif(button_name == "INVERT"):
						self.invert_image()
					
	def event_move(self,event,touch):
		print("event_release: ",touch.id,", ",touch.position, ", ",self.tab)
		if(self.tab == 1):
			for button_name,button_object in self.button_list1.items():
				if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					if(button_name=="WHEEL"):
						x_ratio=(touch.position[0]-(button_object.x+button_object.w/2))/(button_object.w/2)
						y_ratio=(touch.position[1]-(button_object.y+button_object.h/2))/(button_object.h/2)
						self.set_velocity(x_ratio,y_ratio)
						
		if(self.tab == 2):
			for button_name,button_object in self.button_list2.items():
				if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					if(button_name =="PWM1"):
						print("ARM")
						
			for button_name,button_object in self.pwm_list.items():
				if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					scaled_coords=button_object.scale_to_bounds(touch.position,[0.0,1.0],[0.0,1.0])
					if(button_name == "PWM1" and self.pwm == 1):
						print("Send packets for PWM 0 & 1")
						self.send_pwm01(scaled_coords[0],scaled_coords[1])
					if(button_name == "PWM2" and self.pwm == 2):
						print("Send packets for PWM 2 & 3")
						self.send_pwm23(scaled_coords[0],scaled_coords[1])
					if(button_name == "PWM3" and self.pwm == 3):
						print("Send packets for PWM 4 & 5")	
						self.send_pwm45(scaled_coords[0],scaled_coords[1])
		if(self.tab == 3):
			for button_name,button_object in self.button_list3.items():
				if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
					if(button_name =="EXPOSURE"):
						print("EXPOSURE")
			
	def tab_next(self):
		if(self.tab  == 3.0):
			self.tab = 1.0
		else:
			self.tab += 1.0
		print("Next Tab: ",self.tab)

	def tab_prev(self):
		if(self.tab == 1.0):
			self.tab = 3.0
		else:
			self.tab -= 1.0
		print("Prev Tab: ",self.tab)
		
	def next_view(self):
		command = {"target":"VIEW","is_inc":True}
		self.outbound_message_queue.append(command)
		
	def prev_view(self):
		command = {"target":"VIEW","is_inc":False}
		self.outbound_message_queue.append(command)
		
	def getBasePWM_Command(self):
		return {"target":"PWM"}
		
	def getBaseCameraCommand(self):
		return {"target":"CAMERA"}
		
	def getBaseWheelCommand(self):
		return {"target":"WHEELS"}
		
	def next_pwm(self):
		if(self.pwm == 3.0):
			self.pwm = 1.0
		else:
			self.pwm += 1.0
	
	def prev_pwm(self):
		if(self.pwm == 1.0):
			self.pwm = 3.0
		else:
			self.pwm -= 1.0
	
	def send_pwm01(self, x, y):
		command1 = {"target":"PWM","command":"set","index":0,"value":x}
		command2 = {"target":"PWM","command":"set","index":1,"value":y}
		self.outbound_message_queue.append(command1)
		self.outbound_message_queue.append(command2)
		
	def send_pwm23(self, x, y):
		command1 = {"target":"PWM","command":"set","index":2,"value":x}
		command2 = {"target":"PWM","command":"set","index":3,"value":y}
		self.outbound_message_queue.append(command1)
		self.outbound_message_queue.append(command2)
		
	#def send_pwm34(self, x, y):
	def send_pwm45(self, x, y):
		command1 = {"target":"PWM","command":"set","index":4,"value":x}
		command2 = {"target":"PWM","command":"set","index":5,"value":y}
		self.outbound_message_queue.append(command1)
		self.outbound_message_queue.append(command2)
		
	def robot_home(self):
		command = {"target": "WHEEL", "command": "home"}
		self.outbound_message_queue.append(command)
	
	def clear_arm(self):
		command = {"target":"PWM","command":"clear"}
		self.outbound_message_queue.append(command)
		
	def save_arm(self):
		command = {"target":"PWM","command":"save"}
		self.outbound_message_queue.append(command)
	
	def loop_arm(self):
		command = {"target":"PWM","command":"loop"}
		self.outbound_message_queue.append(command)
	
	def home_arm(self):
		command = {"target":"PWM","command":"home"}
		self.outbound_message_queue.append(command)
		
	def lidar_hold(self):
		command={"target":"LIDAR","command":"static"}
		self.outbound_message_queue.append(command)
		
	def lidar_depth_map(self):
		command={"target":"LIDAR","command":"depth_map"}
		self.outbound_message_queue.append(command)
		
	def led_toggle(self,index):
		print("LED_",index," toggle")
		next_led_state=copy.deepcopy(self.led_state)
		next_led_state[index]=not next_led_state[index]
		command = {"target":"CAMERA", "command":"leds","value":next_led_state}
		self.outbound_message_queue.append(command)	
		
	#def light1_on(self):
		#command = {"target":"camera", "command":"leds","value":[True, False, False, False]}
		#self.outbound_message_queue.append(command)	

	#def light2_on(self):
		#command = {"target":"camera", "command":"leds","value":[False, True, False, False]}
		#self.outbound_message_queue.append(command)	
	
	#def light3_on(self):
		#command = {"target":"camera", "command":"leds","value":[False, False, True, False]}
		#self.outbound_message_queue.append(command)
	
	#def light4_on(self):
		#print("L4 on")
		#command = {"target":"camera", "command":"leds","value":[False, False, False, True]}
		#self.outbound_message_queue.append(command)
	
	def set_exposure(self, x):
		command = {"target":"CAMERA","command":"exposure","value": x }
		self.outbound_message_queue.append(command)
		
	def auto_light(self):
		command = {"target":"CAMERA","command":"exposure","value": "auto" }
		self.outbound_message_queue.append(command)
		
	def invert_image(self):
		command = {"target":"CAMERA","command":"invert" }
		self.outbound_message_queue.append(command)
		
	#+/- button on PWM selection
	def pwm_change_index(self,is_plus):
		if(is_plus):
			self.pwm_index+=1
		else:
			self.pwm_index-=1
		if(self.pwm_index>self.MAX_PWM_INDEX): self.pwm_index=0
		if(self.pwm_index<0): self.pwm_index=self.MAX_PWM_INDEX
		
	def pwm_change_scale(self,is_small):
		self.is_small_scale=is_small
		
	def pwm_change_position(self,is_reset,is_plus):
		command=self.getBasePWM_Command()
		command["index"]=self.pwm_index
		if(is_reset):
			command["scope"]="reset"
		else:
			command["scope"]="delta"
			command["value"]=(+1 if is_plus else -1)*(self.SMALL_SCALE_DEGREES if self.is_small_scale else self.BIG_SCALE_DEGREES)
		self.outbound_message_queue.append(command)
		
	#def take_picture(self,is_robot):
		#if(is_robot):
			#command=self.getBaseCameraCommand()
			#command["scope"]="ROBOT"
			#self.outbound_message_queue.append(command)
		#else:
			#self.camera.snapshot()
			#self.controller_pic_count+=1
			##pass #placeholder to take picture locally on controller
		
	#given a user input x [-1.0 (down),+1.0 (up/forward)] and y [-1.0 (left) to +1.0 (right)]
	#get motor commands
	def set_velocity(self,x,y):
		command=self.getBaseWheelCommand()
		y=-y #flip so value closest to neagtive infinity is up (forward)
		if(x==0 and y==0):
			left_speed=0
			right_speed=0
		else:
			#print("WHEEL: ",x,", ",y)
			angle=np.arctan2(y,x)#radians
			left_angle=angle+np.pi/4 #left wheels "max speed" at Q1 (+45 deg) user input
			right_angle=angle-np.pi/4 #right wheels "max speed" at Q2 (+135 deg) user input
			scale=np.clip(np.sqrt(x*x+y*y),0,1)
			left_speed=scale*np.clip(2*np.sin(left_angle),-1,1)
			right_speed=scale*np.clip(2*np.sin(right_angle),-1,1)
			#if(scale<0.12): #dead zone in center
			#	left_speed=0
			#	right_speed=0
		command[Discrete.FRONT_LEFT]=left_speed
		command[Discrete.REAR_LEFT]=left_speed
		command[Discrete.FRONT_RIGHT]=right_speed
		command[Discrete.REAR_RIGHT]=right_speed
		self.outbound_message_queue.append(command)
		self.wheels_x=x
		self.wheels_y=y
		
	#ingest packet from robot about robot state
	def setStatus(self,status):
		if(not status is None):# and type(status)==type({})):
			#self.robot_pic_count=status["camera"]
			self.pwm_state=status["pwm"]
			self.button_list2["LOOP"].is_enabled=status["pwm"]["is_looping"]
			self.button_list2["SAVE"].label="SV "+str(status["pwm"]["loop_state_count"])
			#begin paragraph of janky one-off code to draw dot of current pwm location on GUI
			for pwm_index in range(3):
				pwm_name="PWM"+str(pwm_index+1)#1-3
				ratio_list=[status["pwm"]["state"][pwm_index*2],status["pwm"]["state"][pwm_index*2+1]]
				px=self.pwm_list[pwm_name].range_to_px(ratio_list,[0.0,1.0],[0.0,1.0])
				for channel_offset in [0,1]:#0-1
					channel_index=pwm_index*2+channel_offset#0-5
					self.pwm_list[pwm_name].mark[channel_offset]=px[channel_offset]
			
			#global status
			self.link_counter=status["counter"]
			#qr_count=len(status["camera"]["qr_list"])
			
			#camera
			if(status["camera"]["exposure"]==0):
				self.button_list3["EXPOSURE"].is_enabled=False
				self.button_list3["AUTO"].is_enabled=True
			else:
				self.button_list3["EXPOSURE"].is_enabled=True
				self.button_list3["AUTO"].is_enabled=False
			self.button_list3["INVERT"].is_enabled=status["camera"]["is_invert"]
				
			#Lidar
			self.button_list3["DEPTH"].is_enabled=status["lidar"]["is_depth_map"]
			self.button_list3["HOLD"].is_enabled=status["lidar"]["is_lidar_static"]
			
			#LED
			self.led_state=status["leds"]
			self.button_list3["LED1"].is_enabled=self.led_state[0]
			self.button_list3["LED2"].is_enabled=self.led_state[1]
			self.button_list3["LED3"].is_enabled=self.led_state[2]
			self.button_list3["LED4"].is_enabled=self.led_state[3]
			
			#QR
			qr_list=status["camera"]["qr_list"]
			qr_string=""
			QR_BOX_LINE_LENGTH=29 #number of characters
			for qr_line in qr_list:
				qr_clip="*"+qr_line["string"]
				while(len(qr_clip)>QR_BOX_LINE_LENGTH):
					qr_string+=qr_clip[0:QR_BOX_LINE_LENGTH]+"\n"
					qr_clip=qr_clip[QR_BOX_LINE_LENGTH:]
				qr_string+=qr_clip+"\n"
			self.button_list3["QRtext"].label=qr_string
		
	def __create2Dgraphics(self,is_windowed):
		import pygame
		self.pygame=pygame
		self.pygame.init()
		self.pygame.font.init()
		self.pygame.mouse.set_visible(False)
		screen_dimensions=self.getScreenDimensions()
		#print(screen_dimensions)
		if(is_windowed):
			self.screen_2d=self.pygame.display.set_mode(screen_dimensions)
		else:
			self.screen_2d=self.pygame.display.set_mode(screen_dimensions,self.pygame.FULLSCREEN)
		self.FONT_SIZE_2D=30
		self.font=self.pygame.font.SysFont('Comic Sans MS',self.FONT_SIZE_2D)
		self.font_color=(0,255,0)
		self.pygame.display.flip()
		

	#800 x 480 for 7" touchscreen
	def getScreenDimensions(self):
		display_info=self.pygame.display.Info()
		return (int(display_info.current_w),int(display_info.current_h))
		
	#return a list of messages to send to the robot
	def update(self):
		self.touchscreen.poll() #fetch events:
		#events have hooks (on-press),
		# which call helper functions (pwm_change_position), which
		# add commands ("Set PWM to pos 0") to the outbound queue
		#for event in self.pygame.event.get(): #does nto appear to work, may be conflight with MultiTouch event processing
		#	if(event.type==self.pygame.QUIT or
		#	 ( event.type==self.pygame==KEYDOWN and event.key==self.pygame.K_ESCAPE ) ):
		#		self.__is_alive=False
		color_selected=(0,0,255)
		color_deselected=(50,50,50)
		for button_name,button_object in self.button_listS.items():#Always Draw Static Buttons
			if(button_name=="CAM_COUNT"):
				button_object.label="C#:"+str(self.controller_pic_count)+" R#:"+str(self.robot_pic_count)
			elif(button_name=="LINK_STATUS"):
				button_object.label=str(self.link_counter)
			button_object.draw()
				
		if(self.tab == 1.0):
			for button_name,button_object in self.button_list1.items():
				#if(button_name =="INDEX_PWM"):
				#	button_object.label=str(self.pwm_index)
				#elif(button_name=="SCALE_SMALL"):
				#	button_object.button_color=color_selected if self.is_small_scale else color_deselected
				#elif(button_name=="SCALE_BIG"):
				#	button_object.button_color=color_deselected if self.is_small_scale else color_selected
				#elif(button_name=="PWM_DEG_VAL"):
				#	button_object.label=str(self.pwm_state[self.pwm_index])
				button_object.draw()
				
		if(self.tab == 2.0):
			for button_name,button_object in self.button_list2.items():
				button_object.draw()
			for button_name,button_object in self.pwm_list.items():
				if(self.pwm == 1 and button_name == "PWM1"):
					button_object.draw()
				elif(self.pwm == 2 and button_name == "PWM2"):
					button_object.draw()
				elif(self.pwm == 3 and button_name == "PWM3"):
					button_object.draw()
				
				
		if(self.tab == 3.0):
			for button_name,button_object in self.button_list3.items():
				button_object.draw()	
					
		self.pygame.display.flip()
		
	def popCommands(self):
		temp=self.outbound_message_queue
		self.outbound_message_queue=[]
		return temp
		
	def dispose(self):
		self.pygame.quit()
	
	def is_alive(self):
		return self.__is_alive
	
	@staticmethod
	def build_test():
		print("GUI Build test...")
		import time
		print("Instatiate GUI object...")
		is_windowed=True
		gui=GUI(is_windowed)
		#TODO
		gui.dispose()
		

if __name__ == "__main__":
	print("START")
	GUI.build_test()
	print("DONE")
		
		


