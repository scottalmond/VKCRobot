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
import numpy as np

class GUI:
	def __init__(self,is_windowed):
		self.__create2Dgraphics(is_windowed)
		self.__createEvents()
		self.outbound_message_queue=[] #packets being sent to robot
		self.is_small_scale=False #pwm step size
		self.SMALL_SCALE_DEGREES=1 #degrees of rotation in one delta move
		self.BIG_SCALE_DEGREES=10
		self.pwm_index=0
		self.pwm_state=[0,1,2,3,4,5,6,7]
		self.MAX_PWM_INDEX=7 #shall be no more than 7
		self.wheels_x=0.0
		self.wheels_y=0.0
		self.link_counter=0
		self.robot_pic_count=0
		self.controller_pic_count=0
		self.__is_alive=True
		self.__createButtons()
		
	def __createButtons(self):
		self.button_list={
			"CLOSE":		 Touchable("RECTANGLE",  0,  0, 20, 20,(255,0,0),"X",(255,255,255),self.pygame,self.screen_2d,self.font),
			"LINK_STATUS":   Touchable("RECTANGLE",140,  0,100, 40,(0,0,0),"0",(255,255,255),self.pygame,self.screen_2d,self.font),
			"INDEX_DEC":     Touchable("RECTANGLE", 40, 40,100,100,(255,0,0),"<<",(255,255,255),self.pygame,self.screen_2d,self.font),
			"INDEX_PWM":     Touchable("RECTANGLE",140, 40,100,100,(0,0,0),"0",(255,255,255),self.pygame,self.screen_2d,self.font),
			"INDEX_INC":     Touchable("RECTANGLE",240, 40,100,100,(255,0,0),">>",(255,255,255),self.pygame,self.screen_2d,self.font),
			"PWM_DEG_DEC":   Touchable("RECTANGLE", 40,140,100,100,(255,0,0),"--",(255,255,255),self.pygame,self.screen_2d,self.font),
			"PWM_DEG_CNTR":  Touchable("RECTANGLE",140,140,100,100,(255,0,0),">|<",(255,255,255),self.pygame,self.screen_2d,self.font),
			"PWM_DEG_INC":   Touchable("RECTANGLE",240,140,100,100,(255,0,0),"++",(255,255,255),self.pygame,self.screen_2d,self.font),
			"SCALE_SMALL":   Touchable("RECTANGLE", 40,240,100,100,(100,100,100),"SMALL D",(255,255,255),self.pygame,self.screen_2d,self.font),
			"SCALE_BIG":     Touchable("RECTANGLE",140,240,100,100,(255,0,0),"BIG D",(255,255,255),self.pygame,self.screen_2d,self.font),
			"PWM_DEG_VAL":   Touchable("RECTANGLE",240,240,100,100,(0,0,0),"",(255,255,255),self.pygame,self.screen_2d,self.font),
			"CAM_CONTROLLER":Touchable("RECTANGLE", 40,340,100,100,(255,0,0),"PIC C",(255,255,255),self.pygame,self.screen_2d,self.font),
			"CAM_ROBOT":     Touchable("RECTANGLE",140,340,100,100,(255,0,0),"PIC R",(255,255,255),self.pygame,self.screen_2d,self.font),
			"CAM_COUNT":     Touchable("RECTANGLE",240,340,100,100,(0,0,0),"C#:0 R#:0",(255,255,255),self.pygame,self.screen_2d,self.font),
			"WHEEL":         Touchable("CIRCLE",   400,90,300,300,(255,0,0),"",(255,255,255),self.pygame,self.screen_2d,self.font)
			}
		
	def __createEvents(self):
		self.touchscreen=ft5406.Touchscreen()
		for touch in self.touchscreen.touches:
			touch.on_press=self.event_press
			touch.on_release=self.event_release
			touch.on_move=self.event_move
		
	def event_press(self,event,touch):
		print("event_press: ",touch.id,", ",touch.position)
		
	def event_release(self,event,touch):
		print("event_release: ",touch.id,", ",touch.position)
		for button_name,button_object in self.button_list.items():
			if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
				if(button_name=="INDEX_DEC"):
					self.pwm_change_index(False)
				elif(button_name=="INDEX_INC"): #look at a different PWM channel
					self.pwm_change_index(True)
				elif(button_name=="PWM_DEG_DEC"): #dec position
					self.pwm_change_position(False,False)
				elif(button_name=="PWM_DEG_INC"): #inc position of pwm
					self.pwm_change_position(False,True)
				elif(button_name=="PWM_DEG_CNTR"): #center
					self.pwm_change_position(True,False)
				elif(button_name=="SCALE_SMALL"): #set step to small size
					self.pwm_change_scale(True)
				elif(button_name=="SCALE_BIG"):
					self.pwm_change_scale(False)
				elif(button_name=="CAM_CONTROLLER"):
					self.take_picture(False)
				elif(button_name=="CAM_ROBOT"):
					self.take_picture(True)
				elif(button_name=="WHEEL"):
					self.set_velocity(0,0)
				elif(button_name=="CLOSE"):
					self.__is_alive=False
		
	def event_move(self,event,touch):
		print("event_move: ",touch.id,", ",touch.position)
		for button_name,button_object in self.button_list.items():
			if(button_object.is_in_bounds(touch.position[0],touch.position[1])):
				if(button_name=="WHEEL"):
					x_ratio=(touch.position[0]-(button_object.x+button_object.w/2))/(button_object.w/2)
					y_ratio=(touch.position[1]-(button_object.y+button_object.h/2))/(button_object.h/2)
					self.set_velocity(x_ratio,y_ratio)
			
	def getBasePWM_Command(self):
		return {"target":"PWM"}
		
	def getBaseCameraCommand(self):
		return {"target":"CAMERA"}
		
	def getBaseWheelCommand(self):
		return {"target":"WHEELS"}
		
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
		
	def take_picture(self,is_robot):
		if(is_robot):
			command=self.getBaseCameraCommand()
			command["scope"]="ROBOT"
			self.outbound_message_queue.append(command)
		else:
			self.controller_pic_count+=1
			pass #placeholder to take picture locally on controller
		
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
			scale=np.clip(np.sqrt(x*x+y*y)+.15,0,1)
			left_speed=scale*np.clip(2*np.sin(left_angle),-1,1)
			right_speed=scale*np.clip(2*np.sin(right_angle),-1,1)
			if(scale<0.3): #dead zone in center
				left_speed=0
				right_speed=0
		command[Discrete.FRONT_LEFT]=left_speed
		command[Discrete.REAR_LEFT]=left_speed
		command[Discrete.FRONT_RIGHT]=right_speed
		command[Discrete.REAR_RIGHT]=right_speed
		self.outbound_message_queue.append(command)
		self.wheels_x=x
		self.wheels_y=y
		
	#ingest packet from robot about robot state
	def setStatus(self,status):
		if(not status is None):
			self.pwm_state=status["pwm"]
			self.robot_pic_count=status["camera"]
			self.link_counter=status["counter"]
		
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
		for button_name,button_object in self.button_list.items():
			if(button_name=="INDEX_PWM"):
				button_object.label=str(self.pwm_index)
			elif(button_name=="SCALE_SMALL"):
				button_object.button_color=color_selected if self.is_small_scale else color_deselected
			elif(button_name=="SCALE_BIG"):
				button_object.button_color=color_deselected if self.is_small_scale else color_selected
			elif(button_name=="PWM_DEG_VAL"):
				button_object.label=str(self.pwm_state[self.pwm_index])
			elif(button_name=="CAM_COUNT"):
				button_object.label="C#:"+str(self.controller_pic_count)+" R#:"+str(self.robot_pic_count)
			elif(button_name=="LINK_STATUS"):
				button_object.label=str(self.link_counter)
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
		
		


