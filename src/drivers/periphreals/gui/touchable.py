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
		
	#detemrine if coordinates (of mouse click/drag) is in bounds of button
	def is_in_bounds(self,in_x,in_y):
		if( ( self.x < in_x < (self.x + self.w) ) and
		    ( self.y < in_y < (self.y + self.h) ) ):
		    return True
		return False
