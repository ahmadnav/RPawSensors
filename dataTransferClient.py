import imp
import os 
#import imumsg_pb2.py
import socket,struct, threading
from bluetooth import *
import bluetooth


dir_path = os.path.dirname(os.path.realpath(__file__))

imuMsgPath = dir_path+ "/release/imumsg_pb2.py"
print(imuMsgPath)
imuMsg = imp.load_source("imumsg_pb2",imuMsgPath)

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

bluetoothHost = 1
bluetoothPort = 2
class sensorMsgGenerator():
	def __init__(self):
		pass

	def getMsg(self):
		_imuMsg = imuMsg.IMUInfo()
		_imuMsg.acc_x=float(2.0)
		_imuMsg.acc_y=float(3.524)
		_imuMsg.sensorID = "Sensor1"
		#print("Value: %f" %_imuMsg.acc_x)
		#print("Value: %f" %_imuMsg.acc_y)
		#len(s.encode('utf-8'))
		binaryMsg = _imuMsg.SerializeToString()
		length  = len( binaryMsg )	
		return binaryMsg
_sensorMsg = sensorMsgGenerator()
sampleMsg = _sensorMsg.getMsg()
class dataTransferClient(threading.Thread):
	
	#Stores messages to send to client.
	_msgBuffer = [sampleMsg, sampleMsg]
	#1 BlueTooth 
	def __init__(self):
		#Initialize thread
		threading.Thread.__init__(self)
		
		self.sensorMsgGenerator = sensorMsgGenerator()
		#self.startClientWifi()
		
	#Ran from thread starter.
	def run(self):
		self.startClientBlueTooth()
		
	
	def addMsgToBuffer(self, msg):
		self._msgBuffer.append(msg)
	
	def sendMsgToClient(self):
		
		if( len(self._msgBuffer) > 0):
			print("Message Buffer Size: %i" %(len(self._msgBuffer)))
			msg = self._msgBuffer[0]
			del self._msgBuffer[0]
			self.sendMsg(msg)
		else:
			pass

	def startClientWifi(self):
		self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#Blocking connect call
		self._client.connect((HOST,PORT))
		
		#print('Received', repr(data))

	def startClientBlueTooth(self):
		#self._client = bluetooth.
		addr = "00:DB:DF:F9:6F:22"
		# search for the SampleServer service
		uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
		service_matches = find_service( uuid = uuid, address = addr )

		if len(service_matches) == 0:
			print("couldn't find the SampleServer service =(")
			sys.exit(0)

		first_match = service_matches[0]
		port = first_match["port"]
		name = first_match["name"]
		host = first_match["host"]

		print("connecting to \"%s\" on %s" % (name, host))
		# Create the client socket
		self._client=BluetoothSocket( RFCOMM )
		self._client.connect((host, port))

		self.controlLoop()
		
		return

	def shutDown(self):
		self._client.close()

	#Ran after connection is made
	def controlLoop(self):
		while(True):
			
			self.sendMsgToClient() 
		

	def blueToothFindServer(self):
		# search for the SampleServer service
		uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
		service_matches = find_service( uuid = uuid, address = addr )

		if len(service_matches) == 0:
		    print("couldn't find the SampleServer service =(")
		    sys.exit(0)

		first_match = service_matches[0]
		port = first_match["port"]
		name = first_match["name"]
		host = first_match["host"]		


	def sendMsg(self, msg):

		msgLen = len(msg)

		#Send the length of message. I denotes max of 4 bytes or unsigned int32
		msgLenArray = struct.pack("I", msgLen)

		for byte in msgLenArray:
			print("Sending")
			print(byte)
			self._client.send(byte)

		totalSent=0
		while totalSent <  msgLen:
			#Sent will always be one (as a byte is sent)
			sent = self._client.send(msg[totalSent])
			totalSent = sent + totalSent
			
		
		




def btLookUp():
	nearby_devices = bluetooth.discover_devices(lookup_names=True)
	print("found %d devices" % len(nearby_devices))
	
	for addr, name in nearby_devices:
		print("  %s - %s" % (addr, name))


if __name__=="__main__":
	client = dataTransferClient()
	client.start()
	print("AFTER THREAD")
	i = 0
	while True:
		name = raw_input("PressEnter ")
	 	client.addMsgToBuffer(sampleMsg)
	 	i = i + 1
	#btLookUp()
	
	#name = raw_input("What is your name? ")
