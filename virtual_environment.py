from operator import xor
import os.path
from os import path
import BlynkLib
from statemachine import StateMachine,State
import time

auth = "aJuDFfbAernE8QQw4pJjyHOJT96Qcaw_"
blynk = BlynkLib.Blynk(auth)
class Full_Assembly_Outside(StateMachine):
	search = State("Searching For Dog", initial = True)
	detect = State("Detected Pet")
	open_door = State("Opening Door")
	close_door = State("closing Door")

	found = search.to(detect)
	lost = detect.to(search)
	recognized = detect.to(open_door)
	open_door_lost = open_door.to(close_door)
	door_closed = close_door.to(search)

class Full_Assembly_Inside(StateMachine):
	search = State("Searching For Dog", initial = True)
	detect = State("Detected Pet")
	open_door = State("Opening Door")
	close_door = State("closing Door")

	found = search.to(detect)
	lost = detect.to(search)
	recognized = detect.to(open_door)
	open_door_lost = open_door.to(close_door)
	door_closed = close_door.to(search)



class Door:
	position = 0 # the door is initially closed
	size = 11 # the size of the door

	def up(self):
		while self.position < self.size:
			self.position += 1
			print(self.position)
			time.sleep(.5)
	def down(self):
		while self.position > 0:
			self.position -= 1
			print(self.position)
			time.sleep(.5)

class Motor:
	motor = 0
	def forward(self):
		self.motor = 1
		Door().down()
	def backward(self):
		self.motor = -1
        	Door().up()
	def stop(self):
		self.motor = 0

class Event:
	event = 0
	def toggle(self,input):
		if input == 1:
			self.event = 1
		else:
			self.event = 0

class Timer:
	trigger = 1
	start_time = [0,0,0]
	stop_time = [0,0,0]
	clock_time = [time.localtime().tm_hour,time.localtime().tm_min, time.localtime().tm_sec]
	def compare(self):
#		print(xor(self.clock_time >= self.start_time, self.clock_time >= self.stop_time))
		if xor(self.clock_time >= self.start_time, self.clock_time >= self.stop_time):
			self.trigger = 1
		else:
			self.trigger = 0

class Tag:
	value = None
	program = False
	def record_tag(self,input_tag):
		if self.program == True:
        		self.value = input_tag


trigger = 0
button = Event()
override = Event()
timer = Timer()
motor = Motor()
hall_top = Event()
hall_bottom = Event()
RFID_in = Event()
RFID_out = Event()
prox_in = Event()
prox_out = Event()
reader = Tag()
portal_out = Full_Assembly_Outside()
portal_in = Full_Assembly_Inside()

"""
Setting initial values
"""
if path.exists("timer.txt"):
	timer_set = open("timer.txt", 'r')
	line = timer_set.readline()
	split_line = line.split(",")
	for i in range(int(len(split_line)/2)):
		timer.start_time[i] = int(split_line[i])
	for j in range(int(len(split_line)/2),len(split_line)):
		timer.stop_time[j-int(len(split_line)/2)] = int(split_line[j])
hall_top.event = 1
hall_bottom.event = 1
RF_tag = 543210987654321
RF_tag2 = 123456789012345

@blynk.VIRTUAL_WRITE(1)
def manual_override(value):
	button.toggle(int(value[0]))

@blynk.ON('readV0')
def v0_read_handler():
	blynk.virtual_write(0,'Sets the time to shutdown inside door')

@blynk.VIRTUAL_WRITE(2)
def programmable_timer(value):
	timer.start_time[0] = int((int(value[0])-int(value[0])%3600)/3600)
	timer.start_time[1] = int((int(value[0])%3600-int(value[0])%3600%60)/60)
	timer.start_time[2] = int((int(value[0])%3600%60))
	timer.stop_time[0] = int((int(value[1])-int(value[1])%3600)/3600)
	timer.stop_time[1] = int((int(value[1])%3600-int(value[1])%3600%60)/60)
	timer.stop_time[2] = int((int(value[1])%3600%60))
	if path.exists("timer.txt"):
		timer_setter = open("timer.txt", 'r+')
		timer_setter.truncate(0)
		timer_setter.close()
	timer_setter = open("timer.txt", 'w')
	for i in range(len(timer.start_time)):
		timer_setter.write(str(timer.start_time[i])+',')
	for j in range(len(timer.stop_time)):
		if j < len(timer.stop_time)-1:
			timer_setter.write(str(timer.stop_time[j])+',')
		else:
			timer_setter.write(str(timer.stop_time[j]))

@blynk.VIRTUAL_WRITE(3)
def record_RFID_tag(value):
	if int(value[0]) == 1:
		if path.exists("tags.txt"):
			tag = open("tags.txt", 'r')
			check = True
			line = tag.readline()
			while line:
				print(line)
				if line == str(reader.value)+"\n" or line == str(reader.value):
					check = False
					break
				line = tag.readline()
			tag.close()
			if check == True:
				print("printing tag")
				tag = open("tags.txt",'a')
				tag.write(str("\n"+str(reader.value)))
				tag.close()
		else:
			tag = open("tags.txt",'w')
			print("saving tag")
			tag.write(str(reader.value))
			tag.close()

@blynk.VIRTUAL_WRITE(8)
def timer_override(value):
	override.toggle(int(value[0]))

"""
The following functions are to be removed for the operation of the physical device 
since these will no longer be button inputs but sensor inputs
"""

@blynk.VIRTUAL_WRITE(4)
def hall_top_toggle(value):
	hall_top.toggle(int(value[0]))

@blynk.VIRTUAL_WRITE(5)
def hall_bottom_toggle(value):
	hall_bottom.toggle(int(value[0]))

@blynk.VIRTUAL_WRITE(6)
def dog1(value):
	reader.value = RF_tag

@blynk.VIRTUAL_WRITE(7)
def dog1(value):
	reader.value = RF_tag2

while(True):
	blynk.run()
	timer.clock_time = [time.localtime().tm_hour,time.localtime().tm_min, time.localtime().tm_sec]
	if override.event == 0:
		timer.compare()
	else:
		timer.trigger = 1
#	print(timer.trigger)
	reader.program = False
	#time.sleep(.5)
        if( button.event == 1 and 
	    hall_top.event == 1):
		motor.backward()
		trigger = 1
		print(0)
        elif( button.event == 1 and 
	      hall_top.event == 0 and 
	      motor.motor == -1):
		motor.stop()
		print(1)
        elif (button.event == 0 and 
		hall_top.event == 0 and 
		motor.motor == -1 and 
		trigger == 1):
            motor.stop()
            time.sleep(2)
            print(3)
        elif( button.event == 0 and 
		hall_top.event == 0 and
		motor.motor == 0 and 
		trigger == 1):
            motor.forward()
            print(4)
	elif (motor.motor == 1 and 
		hall_bottom.event == 0 and 
		trigger == 1):
		motor.stop()
		trigger = 0
		print(5)
	elif (motor.motor == 0 and 
		hall_bottom.event == 0 and 
		button.event == 0 and 
		trigger == 0):
		print("base")
		if (prox_out.event == 1 and 
		   (portal_out.current_state == portal_out.search or 
		    portal_out.current_state == portal_out.close_door)):
			portal_out.found()
			RFID_out.event = 1
			database = open("tags.txt",'r')
			print("object found")
		elif (prox_out.event == 1 and 
		      RFID_out.event == 1 and 
		      reader.program == False and 
		      portal_out.current_state == portal_out.detect and 
		      reader.value in database.readline()):
			portal_out.recognized()
			motor.backward()
			database.close()
			print("Pet recognized")
		elif (prox_out.event == 0 and 
		      portal_out.current_state == portal_out.detect):
			portal_out.lost()
			print("lost")
		elif ((prox_out.event == 1 or 
		       prox_in.event == 1) and 
		       portal_out.current_state == portal_out.open_door):
			portal_out.recognized()
			if hall_top.event == 0 and motor.motor == 0:
				motor.stop()
			print("opening door")
		elif (prox_in.event == 0 and 
		      prox_out.event == 0 and 
		      portal_out.current_state == portal_out.open_door):
			portal_out.open_door_lost()
			print("door closing")
		elif (prox_out.event == 0 and 
		      portal_out.current_state == portal_out.close_door):
			if (hall_top.event == 0 and 
			    motor.motor == 0):
				motor.forward()
			elif (hall_bottom.event == 0 and 
			      motor.motor == 1):
				motor.stop()
				portal_out.door_closed()
			print("door closed")


		if timer.trigger == 1:
			if (prox_in.event == 1 and 
			   (portal_out.current_state == portal_out.search or 
			    portal_out.current_state == portal_out.close_door)):
				portal_out.found()
				RFID_in.event = 1
				database = open("tags.txt",'r')
			elif (prox_in.event == 1 and 
			      RFID_in.event == 1 and 
			      reader.program == False and 
			      portal_out.current_state == portal_out.detect and 
			      reader.value in database.read()):
				portal_out.recognized()
				motor.backward()
				database.close()
			elif (prox_in.event == 0 and 
			      portal_out.current_state == portal_out.detect):
				portal_out.lost()

			elif ((prox_in.event == 1 or
			       prox_out.event == 1) and 
			       portal_out.current_state == portal_out.open_door):
				portal_out.recognized()
				if (hall_top == 0 and 
				    motor.motor == 0):
					motor.stop()
			elif (prox_in.event == 0 and 
			      prox_out.event == 0 and 
			      portal_out.current_state == portal_out.open_door):
				portal_out.open_door_lost()
			elif (prox_in.event == 0 and 
			      portal_out.current_state == portal_out.close_door):
				if (hall_top.event == 0 and 
				    motor.motor == 0):
					motor.forward()
				elif (hall_bottom.event == 0 and 
				      motor.motor == 1):
					motor.stop()
					portal_out.door_closed()

		


    
