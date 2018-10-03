import numpy as np

class Touchable:
	def __init__(self,shape,x,y,w,h,button_color,label,font_color,pygame,screen,font):
		self.shape=shape
		self.x=x
		self.y=y
		self.w=w
		self.h=h
		self.button_color=button_color
		self.label=label
		self.font_color=font_color
		self.pygame=pygame
		self.screen=screen
		self.font=font
		
	def draw(self):
		if(self.shape=="CIRCLE"):
			self.pygame.draw.ellipse(self.screen,self.button_color,(self.x,self.y,self.w,self.h),0)
		elif(self.shape=="RECTANGLE"):
			self.pygame.draw.rect(self.screen,self.button_color,(self.x,self.y,self.w,self.h))
		if(not self.label is None and len(self.label)>0):
			rendered_string=self.font.render(self.label,False,self.font_color)
			self.screen.blit(rendered_string,(self.x,self.y))
	
	#def remove(self):
	#	if(self.shape=="CIRCLE"):
	#		self.pygame.clear.ellipse(self.screen,self.button_color,(self.x,self.y,self.w,self.h),0)
	#	elif(self.shape=="RECTANGLE"):
	#		self.pygame.clear.rect(self.screen,self.button_color,(self.x,self.y,self.w,self.h))
	#	if(not self.label is None and len(self.label)>0):
	#		rendered_string=self.font.render(self.label,False,self.font_color)
	#		self.screen.blit(rendered_string,(self.x,self.y))
			
	#detemrine if coordinates (of mouse click/drag) is in bounds of button
	def is_in_bounds(self,in_x,in_y):
		if( ( self.x < in_x < (self.x + self.w) ) and
		    ( self.y < in_y < (self.y + self.h) ) ):
		    return True
		return False
		
	#given a touch location [x,y], and a x_range [min,max] and y range [min,max]
	# generate the corresponding linear fit betweenn the min and max
	def scale_to_bounds(self,touch_loc,x_range,y_range):
		out_list=[]
		for is_y in [False,True]:
			scaled=np.interp(int(touch_loc[is_y]),[self.y,self.y+self.h] if is_y else [self.x,self.x+self.w],y_range if is_y else x_range)
			out_list.append(scaled)
		return out_list
		
	@staticmethod
	def build_test():
		print("Touchable build test")
		touchable=Touchable("SQUARE",100,200,10,20,None,None,None,None,None,None)
		pos=[101,210]
		print("Position input: ",pos);
		scaled=touchable.scale_to_bounds(pos,[-10,10],[0,1])
		print("Scaled: ",scaled)

if __name__ == "__main__":
	print("START")
	Touchable.build_test()
	print("DONE")
