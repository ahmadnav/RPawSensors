import socket
import os, imp, struct, threading, csv, time
from bluetooth import *
import bluetooth, signal, sys
from enum import Enum
from cobs import cobs

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

dir_path = os.path.dirname(os.path.realpath(__file__))

imuMsgPath = dir_path+ "/release/imumsg_pb2.py"

imuMsg = imp.load_source("imumsg_pb2",imuMsgPath)

#Class defines mode of data transfer
class dataTransferMode(Enum):

	TCP = 1
	BLUETOOTH = 2

class commonBTAdress(Enum):
	
	RASPBERRYBTADDR = "B8:27:EB:6B:15:7F"

class msgServer(threading.Thread):
	connected = False
	#If true choose blueTooth connection
	blueTooth = False
	_maxClients = 1
	_numClients = 0
	_serverRunning = True
	def __init__(self, dataTransferMode):
		threading.Thread.__init__(self)

		print("Binding to port")
		self.transferMode = dataTransferMode

	def run(self):
		#self.startServer()
		if(self.transferMode == dataTransferMode.TCP):
			self.startTCPServer()
		elif(self.transferMode == dataTransferMode.BLUETOOTH):
			self.startServerBlueTooth()
			# self.startServiceBTServer()

	def startServiceBTServer(self):
		server_sock=BluetoothSocket( RFCOMM )
		server_sock.bind(("",PORT_ANY))
		server_sock.listen(1)

		port = server_sock.getsockname()[1]

		uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

		advertise_service( server_sock, "mainDataTransferServer",
							service_id = uuid,
							service_classes = [ uuid, SERIAL_PORT_CLASS ],
							profiles = [ SERIAL_PORT_PROFILE ], 
							#                   protocols = [ OBEX_UUID ] 
							)

		print("Waiting for connection on RFCOMM channel %d" % port)

		client_sock, client_info = server_sock.accept()
		print("Accepted connection from ", client_info)

		try:
			while True:
				data = client_sock.recv(1024)
				if len(data) == 0: break
				print("received [%s]" % data)
		except IOError:
			pass

		print("disconnected")
	
	def startTCPServer(self):
			print("Binding to port")
			#create an INET, STREAMing socket
			self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#bind the socket to a public host,
			# and a well-known port
			print("Binding to port")
			self.serversocket.bind((HOST, PORT))
			print("Succesfully connected to a client")


			self.controlLoop()


 	
			
	#Ran after connection is made
	def controlLoop(self):
		_thread = IMUMsgThread(self.clientsocket,self)
		_thread.start()		

	@property
	def numClients(self):
		return self._numClients

	def removeClient(self):
		##For now just lower number clients connected
		self._numClients = self._numClients - 1
	
	def startServerBlueTooth(self):
		self.serverSocket=BluetoothSocket( RFCOMM )

		self.serverSocket.bind((commonBTAdress.RASPBERRYBTADDR, 3 ))
		print("listening for clients on bt")
		self.serverSocket.listen(1)

		clientSocket, address = self.serverSocket.accept()
		print("Connected to server")
		_mThread = IMUMsgThread(clientSocket, self)
		_mThread.start()
		# self.serverSocket.close()

	def shutDown(self):
		self._serverRunning = False
		sys.exit(0)




	def receive(self, MSGLEN):
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			chunk = self.clientsocket.recv(1)
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		return ''.join(chunks)	






			
class IMUMsgThread(threading.Thread):
	#Thread is running
	_running = True
	#Whether to store incoming data in a CSV file.
	_recordData=False

	def __init__(self, clientSocket, parentServer):
		threading.Thread.__init__(self)
		self.clientsocket = clientSocket
		self._parentServer = parentServer
		

	def run(self):
		# self.csvFile = open(dir_path+"/data.csv", 'wb')
		# self.CSVData = csv.writer(self.csvFile)		
		while self._running: 
			
			time.sleep(1)
			# try:
			# 	self._currentIMUData = self.getIMUMsg()
			# except:
			# 	print("ERROR getting message")
			# 	pass				
			

	def getLatestStoredIMUData(self):

		return self._currentIMUData

	def getIMUMsg(self):
	 #
		dataSizeArray = self.receive(4)
		

		dataSize = struct.unpack("<L", dataSizeArray)[0]
		print(dataSize)

		data = self.receive(dataSize)	
		

		#Get incoming data.
		_imuMsg = imuMsg.IMUInfo()				
		_imuMsg.ParseFromString(data)
		print("Value: %f" %_imuMsg.acc_x)
		print("Data from sensor "+ _imuMsg.sensorID)
		if self._recordData:
			self.CSVData.writerow([_imuMsg.acc_x])
		return _imuMsg
		

	###
	def receive(self, MSGLEN):
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			print("Waiting for msg")
			chunk = self.clientsocket.recv(1)
			print(chunk)
			if chunk == '':

				#raise RuntimeError("socket connection broken")
				print("socket connection broken shutting down this thread")
				self.shutDown()
				return 0


			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		return ''.join(chunks)	

	def shutDown(self):
		self.clientsocket.close()
		self.csvFile.close()
		self._running = False
		self._parentServer.removeClient()

	def sendMsg(self, msg):
		
		msgLen = len(msg)
		#Send the length of message. I denotes max of 4 bytes or unsigned int32
		msgLenArray = struct.pack("I", msgLen)

		for byte in msgLenArray:
			self._client.send(byte)

		totalSent=0
		while totalSent <  msgLen:
			#Sent will always be one (as a byte is sent)
			sent = self._client.send(msg[totalSent])
			totalSent = sent + totalSent


	def sendCOBSMessage(self, msg):
		msgLen = len(msg)
		#Send the length of message. I denotes max of 4 bytes or unsigned int32
		msgLenArray = struct.pack("I", msgLen)

		totalMsg = msgLen + msg

		encodedMsg = cobs.encode(totalMsg)
		totalSent=0
		while totalSent <  len(encodedMsg):
			#Sent will always be one (as a byte is sent)
			sent = self._client.send(encodedMsg[totalSent])
			totalSent = sent + totalSent
		

if __name__=="__main__":
	
	# print("Binding to port")
	#~ connect()
	_msgServerThread = msgServer(dataTransferMode.BLUETOOTH)
	_msgServerThread.start()
