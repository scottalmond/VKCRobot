#!/usr/bin/python
import struct
import time
import sys
import os

infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "0")

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode
fd = os.open(infile_path, os.O_RDONLY|os.O_NONBLOCK)
in_file = os.fdopen(fd, "rb")
#in_file = open(infile_path, "rb")

for rep in range(30):

	event = in_file.read(EVENT_SIZE)

	while event:
		(tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)

		if type != 0 or code != 0 or value != 0:
			print("Event type %u, code %u, value %u at %d.%d" % \
				(type, code, value, tv_sec, tv_usec))
		else:
			# Events with code, type and value == 0 are "separator" events
			print("===========================================")

		event = in_file.read(EVENT_SIZE)
	time.sleep(0.1)

in_file.close()
