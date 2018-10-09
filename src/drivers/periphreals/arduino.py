import serial



class Arduino:
	USB_ADDRESS="/dev/ttyUSB0"#'/dev/ttyACM0'
	USB_BAUD=115200
	USB_TIMEOUT_SECONDS=1

	def __init__(self,usb_address=None,usb_baud=None):
		self.serial_queue="" #string holding the latest partial data line
		if(usb_address is None):
			usb_address=self.USB_ADDRESS
		if(usb_baud is None):
			usb_baud=self.USB_BAUD
		self.usb_address=usb_address
		self.usb_baud=usb_baud
		self.serial=serial.Serial(self.usb_address,self.usb_baud,timeout=self.USB_TIMEOUT_SECONDS)
		
	#returns None on error
	#returns dictionary:
	#{"encoders":[{"rotation":X1,"subposition":Y1,"errors":Z1},{"rotation":X2,"subposition":Y2,"errors":Z2}],"leds":[True,True,False,False]}
	def getLine(self):
		line=self.serial.readline()#10 numbers, comma separated
		line=str(line,'utf-8') #convert binary to string
		return line
		
	#flush the buffer and return only the last line found
	def getLastLine(self):
		while(self.serial.inWaiting()):
			this_char=str(self.serial.read(),'utf-8')
			self.serial_queue+=this_char
		split_status=self.serial_queue.split('\n')
		if(len(split_status)>1):
			self.serial_queue=split_status[-1]
			return split_status[-2]
		
		
	#take incoming string Arduino -> RPi and convert to dictionary
	#precon: input line is a String
	#return None on errro
	@staticmethod
	def parseLine(line):
		if(line is None): return None
		split=line.strip().split(",")
		if(not len(split)==11):
			return None
		val=[]
		for rep in range(len(split)):
			val.append(int(split[rep]))
		out_dict={"packet_id":val[0],
				  "encoder_right":{"rotation":val[1],"subposition":val[2],"errors":val[3]},
				  "encoder_left":{"rotation":val[4],"subposition":val[5],"errors":val[6]},
				  #"encoders":[{"rotation":val[1],"subposition":val[2],"errors":val[3]},
					#		  {"rotation":val[4],"subposition":val[5],"errors":val[6]}],
				  "leds":[val[7]==1,val[8]==1,val[9]==1,val[10]==1]}
		return out_dict
		
	#list of four boolean values
	def writeLED(self,leds):
		string_out=self.__get_led_string(leds)
		self.serial.write(string_out)
	
	#take outgoing status RPi -> Arduino and convert to string
	@staticmethod
	def __get_led_string(leds):
		string_out=""
		for led_index in range(len(leds)):
			string_out+="1" if leds[led_index]==True else "0"
			if(led_index==(len(leds)-1)):
				string_out+="\n"
			else:
				string_out+=","
		return string_out
			
	@staticmethod
	def build_test(is_infinite_loop=False):
		print("Arduino build test")
		print("format command to turn on LEDs 0 and 1")
		cmd_binary=[True,True,False,False]
		string_expectation="1,1,0,0\n"
		cmd_string=Arduino.__get_led_string(cmd_binary)
		print("Format LED command: ",("PASS" if cmd_string==string_expectation else "FAIL"))#,", Expectation: ",string_expectation,", Reality: ",cmd_string)
		cmd_string="99,1,2,3,4,5,6,1,1,0,0"
		expectation_dict={"packet_id":99,"encoders":[{"rotation":1,"subposition":2,"errors":3},{"rotation":4,"subposition":5,"errors":6}],"leds":[True,True,False,False]}
		cmd_dict=Arduino.parseLine(cmd_string)
		print("Format status packet: ",("PASS" if (expectation_dict==cmd_dict) else "FAIL"))
		if(not expectation_dict==cmd_dict):
			print("WAS: ",expectation_dict)
			print("IS: ",cmd_dict)
		
		arduino=Arduino()
		rep=-1 if is_infinite_loop else 30
		while((rep<=-1 and is_infinite_loop) or rep>=0):
			line=arduino.getLine()
			print("Line: ",line)
			print("Parsed: ",Arduino.parseLine(line))
			rep-=1

	@staticmethod
	def build_test2(is_infinite_loop=False):
		print("Arduino build test")
		import time
		arduino=Arduino()
		rep=-1 if is_infinite_loop else 30
		while((rep<=-1 and is_infinite_loop) or rep>=0):
			line=arduino.getLastLine()
			if(not line is None):
				print("Line: ",line)
				print("Parsed: ",Arduino.parseLine(line))
			rep-=1
			time.sleep(0.01)
		
	
if __name__ == "__main__":
	print("START")
	Arduino.build_test2(True)
	print("DONE")
