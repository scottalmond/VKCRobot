import numpy as np

class Touchable:
	def __init__(self,shape,x,y,w,h,button_color,label,font_color,pygame,screen,font,is_enabled=True):
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
		self.is_enabled=is_enabled
		self.mark=None
		
	def draw(self):
		#if(self.label=="Light1"):
		#	print("DRAW LED 1")
		fill_color=self.button_color if self.is_enabled else (100,100,100) #gray if not active
		if(self.shape=="CIRCLE"):
			self.pygame.draw.ellipse(self.screen,fill_color,(self.x,self.y,self.w,self.h),0)
		elif(self.shape=="RECTANGLE"):
			self.pygame.draw.rect(self.screen,fill_color,(self.x,self.y,self.w,self.h))
		if(not self.label is None and len(self.label)>0):
			string_list=self.label.split("\n")
			line_offset=0
			PX_BETWEEN_VERTICAL_LINES=20
			for string_line in string_list:
				rendered_string=self.font.render(string_line,False,self.font_color)
				self.screen.blit(rendered_string,(self.x,self.y+line_offset))
				line_offset+=PX_BETWEEN_VERTICAL_LINES #magic number: px between lines with this font/font_size
		self.drawMark()
	
	#position is 1d list of [x,y]
	def drawMark(self):
		if(not self.mark is None):
			mark_radius=5 #px
			x=self.mark[0]
			y=self.mark[1]
			fill_color=(255,255,255)
			self.pygame.draw.ellipse(self.screen,fill_color,(x-mark_radius,y-mark_radius,mark_radius*2,mark_radius*2),0)
	
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
		
	#reverse pf scale_to_bounds: takes range -1 to 1 and maps it back to the pixles of this object
	def range_to_px(self,ratio_loc,x_range,y_range):
		out_list=[]
		for is_y in [False,True]:
			scaled=int(np.interp(ratio_loc[is_y],y_range if is_y else x_range,[self.y,self.y+self.h] if is_y else [self.x,self.x+self.w]))
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
