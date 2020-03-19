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
			self.position += 1;time.sleep(.5)
	def down(self):
		while position > 0:
			self.position -= 1;time.sleep(.5)

class Motor:
	motor = 0
	def forward(self):
		self.motor = 1
	def backward(self):
		self.motor = -1
	def stop(self):
		self.motor = 0

class Event:
	event = 0
	def toggle(self,input):
		if input == 1:
			self.event = 1
		else:
			self.event = 0

class Tag:
	value = None
	program = False
	def record_tag(self,input_tag):
        	value = input_tag


button = Event()
trigger = 0
timer = Event()
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
hall_top.event = 1
hall_bottom.event = 1
reader.record_tag(123456789012345)

@blynk.VIRTUAL_WRITE(1)
def manual_override(value):
	button.toggle(int(value[0]))

@blynk.VIRTUAL_WRITE(2)
def programmable_timer(value):
	timer.toggle(int(value[0]))

@blynk.VIRTUAL_WRITE(3)
def record_RFID_tag(value):
	if int(value[0]) == 1:
		reader.program = True
		tag = open("tags.txt",w)
		tag.seek(-1)
		tag.write("\n")
		tag.write(str(reader.value+"\n")

# button = Event()
# timer = Event()
# motor = Motor()
# hall_top = Event()
# hall_bottom = Event()
# RFID_in = Event()
# RFID_out = Event()
# prox_in = Event()
# prox_out = Event()
# reader = Tag()

while(True):
	blynk.run()
	time.sleep(.5)
	reader.program = False
	if button.event == 1 and hall_top.event == 1:
        	motor.backward()
		trigger = 1
	elif button.event == 1 and hall_top.event == 0 and motor.motor == -1:
        	motor.stop()
	elif button.event == 0 and hall_top.event == 0 and motor.motor == -1 and trigger == 1:
        	motor.stop()
        	time.sleep(2)
	elif button.event == 0 and hall_top.event == 0 and motor.motor == 0 and trigger == 1:
        	motor.forward()
	elif motor.motor == 1 and hall_bottom.event == 0 and trigger == 1:
		motor.stop()
		trigger = 0
	elif motor.motor == 0 and hall_bottom.event == 0 and button.event == 0 and trigger == 0:
		if prox_out.event == 1 and (portal_out.current_state == portal_out.search or portal_out.current_state == portal_out.close_door):
			portal_out.found()
			RFID_out.event = 1
			database = open("tags.txt",r)
		elif prox_out.event == 1 and RFID_out.event == 1 and reader.program == False and portal_out.current_state == portal_out.detect and reader.value in database.read():
			portal_out.recognized()
			motor.backward()
			database.close()
		elif prox_out.event == 0 and portal_out.current_state == portal_out.detect:
			portal_out.lost()

		elif (prox_out.event == 1 or prox_in.event == 1) and portal_out.current_state == portal_out.open_door:
			portal_out.recognized()
			if hall_top.event == 0 and motor.motor == 0:
				motor.stop()
		elif prox_in.event == 0 and prox_out.event == 0 and portal_out.current_state == portal_out.open_door:
			portal_out.open_door_lost()
		elif prox_out.event == 0 and portal_out.current_state == portal_out.close_door:
			if hall_top.event == 0 and motor.motor == 0:
				motor.forward()
			elif hall_bottom.event == 0 and motor.motor == 1:
				motor.stop()
				portal_out.door_closed()


		if timer.event == 1:
			if prox_in.event == 1 and (portal_out.current_state == portal_out.search or portal_out.current_state == portal_out.close_door):
				portal_out.found()
				RFID_in.event = 1
				database = open("tags.txt",r)
			elif prox_in.event == 1 and RFID_in.event == 1 and reader.program == False and portal_out.current_state == portal_out.detect and reader.value in database.read():
				portal_out.recognized()
				motor.backward()
				database.close()
			elif prox_in.event == 0 and portal_out.current_state == portal_out.detect:
				portal_out.lost()

			elif (prox_in.event == 1 or prox_out.event == 1) and portal_out.current_state == portal_out.open_door:
				portal_out.recognized()
				if hall_top == 0 and motor.motor == 0:
					motor.stop()
			elif prox_in.event == 0 and prox_out.event == 0 and portal_out.current_state == portal_out.open_door:
				portal_out.open_door_lost()
			elif prox_in.event == 0 and portal_out.current_state == portal_out.close_door:
				if hall_top.event == 0 and motor.motor == 0:
					motor.forward()
				elif hall_bottom.event == 0 and motor.motor == 1:
					motor.stop()
					portal_out.door_closed()
