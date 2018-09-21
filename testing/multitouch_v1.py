from library import ft5406
ts=ft5406.Touchscreen()

def pressed(event, touch):
	print("pressed: ",touch.id,", ",touch.position)
	
def released(event,touch):
	print("released: ",touch.id,", ",touch.position)
	
def moved(event,touch):
	print("moved: ",touch.id,", ",touch.position)

for touch in ts.touches:
	touch.on_press=pressed
	touch.on_release=released
	touch.on_move=moved

ts.run()

import time
while(True):
	#for touch in ts.poll():
	time.sleep(0.01)
	#print(touch.slot, touch.id, touch.valid, touch.x, touch.y)
