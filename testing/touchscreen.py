# From pygamets
# https://github.com/olegv142/pygamets/blob/master/pygamets/events.py

"""
Input events reader.
Collect events reading raw events pipe /dev/input/event0
Motivation:
  The PS/2 emulated events available at /dev/input/mouse0 have
  wrong position information if touch screen is used. So the pygame
  relying on such events works incorrectly unless used under X-windows
  system which implements its own raw events processing routine.
"""

import os, struct
from collections import namedtuple

class Touchscreen:

	def __init__(self):
		self.EV_KEY = 1
		self.EV_ABS = 3
		self.ABS_X = 0
		self.ABS_Y = 1
		self.EV_FMT = 'QHHI'
		self.EV_SZ = struct.calcsize(self.EV_FMT)
		self.events_filename = '/dev/input/event0'
		self.events_file = None
		self.Event = namedtuple('Event', ('down', 'pos'))

	def open_events_file(self):
		"""Returns events file object open in non blocking mode"""
		if self.events_file is None:
			# Select does not work for whatever reason on events file
			# so we have to use non-blocking mode
			fd = os.open(self.events_filename, os.O_RDONLY|os.O_NONBLOCK)
			events_file = os.fdopen(fd, "r")
		return events_file

	def read_events(self):
		"""Returns the list of events collected as instances of Event objects"""
		events = []
		pos_x, pos_y = None, None
		f = self.open_events_file()

		while True:
			try:
				e = f.read(self.EV_SZ)
			except IOError:
				break
			if(len(e)==0): continue
			print("here: ",bytes(e,'utf-8'))
			ts, type, code, val = struct.unpack(self.EV_FMT, bytes(e,'utf-8'))
			if type == self.EV_KEY:
				down = val != 0
				events.append(self.Event(down, None))
			elif type == EV_ABS:
				if code == ABS_X:
					pos_x = val
				if code == ABS_Y:
					pos_y = val
				if pos_x is not None and pos_y is not None:
					events.append(self.Event(None, (pos_x, pos_y)))
					pos_x, pos_y = None, None

		return events
