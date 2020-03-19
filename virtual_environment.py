import BlynkLib
import time

auth = "Authentication Token"
blynk = BlynkLib.Blynk(auth)

class Door:
	position = 0 #the door is initially closed
	size = 11 #the size of the door

	def up(self):
		while self.position < self.size:
			self.position += 1
	def down(self):
		while position > 0:
			self.position -= 1
class Sensor:
	sensor = False
	def detect(self, input):
                if input == True:
                        self.sensor = True
                else:
                        self.sensor = False

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


button = Event()
timer = Event()
motor = Motor()
hall_top = Sensor()
hall_bottom = Sensor()
RFID_in = Sensor()
RFID_out = Sensor()
prox_in = Sensor()
prox_out = Sensor()


@blynk.VIRTUAL_WRITE(1)
def manual_override(value):
	button.toggle(int(value[0]))

@blynk.VIRTUAL_WRITE(2)
def programmable_timer(value):
	timer.toggle(int(value[0]))

@blynk.VIRTUAL_WRITE(3)
def record_RFID_tag(value):
	if int(value[0]) == 1:
		tag = open("tags.txt",w)
		tag.seek(-1)
		tag.write("\n")
		tag.write(str(reader.value())+"\n")
		tag.close()

while(True):
	blynk.run()
	print(button.event)
	
