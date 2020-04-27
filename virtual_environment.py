from operator import xor
import os.path
from os import path
import BlynkLib
import time

auth = "authentication token goes here"

blynk = BlynkLib.Blynk(auth)


class Door:
	position = 0 # the door is initially closed
	size = 11 # the size of the door

	def up(self):
		if self.position != self.size:
			while self.position < self.size:
				self.position += 1
				print(self.position)
				time.sleep(.5)
	def down(self):
		if self.position != 0:
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
#		print"start time: ",self.start_time
#		print "stop time: ",self.stop_time
#		print(xor(self.clock_time >= self.start_time, self.clock_time >= self.stop_time))
		if self.start_time < self.stop_time:
			if xor(self.clock_time<= self.start_time, self.clock_time >= self.stop_time):
				self.trigger = 1
			else:
				self.trigger = 0
		else:
                        if xor(self.clock_time>= self.start_time, self.clock_time >= self.stop_time):
                                self.trigger = 1
                        else:
                                self.trigger = 0


class Tag:
	value = None
	program = False
	def record_tag(self,input_tag):
		if self.program == True:
        		self.value = input_tag
	def read_tag(self):
		return self.value

count = 0
prev_state = 1
status = "door closed"
state = 0
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
	if timer.start_time[0]>12:
		print("Start time set to: "+str(timer.start_time[0]-12)+":"+str(timer.start_time[1])+" PM")
	elif timer.start_time[0] == 12:
		print("Start time set to: "+str(timer.start_time[0])+":"+str(timer.start_time[1])+" PM")
	else:
		print("Start time set to: "+str(timer.start_time[0])+":"+str(timer.start_time[1])+" AM")
	if timer.stop_time[0]>12:
		print("Stop time set to: "+str(timer.stop_time[0]-12)+":"+str(timer.stop_time[1])+" PM")
	elif timer.stop_time[0] == 12:
		print("Stop time set to: "+str(timer.stop_time[0])+":"+str(timer.stop_time[1])+" PM")
	else:
		print("Stop time set to: "+str(timer.stop_time[0])+":"+str(timer.stop_time[1])+" AM")

@blynk.VIRTUAL_WRITE(3)
def record_RFID_tag(value):
	if int(value[0]) == 1:
		if path.exists("tags.txt"):
			tag = open("tags.txt", 'r')
			check = True
			line = tag.readline()
			while line:
				#print(line)
				if line == str(reader.value)+"\n" or line == str(reader.value):
					check = False
					break
				line = tag.readline()
			tag.close()
			if check == True:
				print("saving tag")
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

@blynk.VIRTUAL_WRITE(9)
def Prox_in_toggle(value):
	prox_in.toggle(int(value[0]))

@blynk.VIRTUAL_WRITE(10)
def Prox_out_toggle(value):
        prox_out.toggle(int(value[0]))



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
#	if count == 0 and prev_state != 0:
#		print("state = "+status)
#		count += 1
	if state == 0:
#	Door is closed, and sensors are looking for object
		if count == 0:
			print("status = door closed")
			count += 1
		status = "door closed"
		if (timer.trigger == 1 and prox_in.event == 1) or prox_out.event == 1:
			state = 1
			prev_state = 0
			count = 0
		if button.event == 1:
			state = 2
			count = 0

	if state == 1:
#	RFID sensor searches for recognized tag
                if count == 0:
			print("status = verifying RFID tag")
			count += 1
		status = "verifying RFID tag"
		if path.exists("tags.txt"):
			ID = open("tags.txt", 'r')
			for line in ID:
				if line == str(reader.read_tag()) or line == str(reader.read_tag())+"\n":
					state = 2
					count = 0
					break
				state = prev_state
				count = 0
			ID.close()
		else:
			state = prev_state
			count = 0

	if state == 2:
#	Door opens
                if count == 0:
			print("status = opening door")
			count += 1
		status = "opening door"
		if hall_top.event == 1:
			#motor.backward()
			pass
		elif hall_top.event == 0:
			motor.stop()
			print("status = door open")
			time.sleep(2)
			state = 3
			count = 0

	if state == 3:
#	Door is open and is holding position
#		if count == 0:
#			print("status = door open")
#			count += 1
		prev_state = state
		status = "door open"
		if button.event == 0 and prox_in.event == 0 and prox_out.event == 0:
			state = 4
			count = 0

	if state == 4:
#	Door is closing
		if count == 0:
			print("status = closing door")
			count += 1
		if hall_bottom.event == 1:
			motor.forward()
			if (prox_in.event == 1 and timer.trigger == 1) or prox_out.event == 1:
				state = 1
				prev_state = 4
				count = 0
			elif button.event == 1:
				state = 2
				count = 0
		elif hall_bottom.event == 0:
			motor.stop()
			state = 0
			count = 0
