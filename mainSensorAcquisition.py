from USonicJSNapi import USSensor
from dataTransferServer import *
import threading



#This class initiates all sensor acquisition software threads, and polls them for data at 
#a specified rate.
class mainSensorAcquistion(threading.Thread):

	def __init__(self):
		self.initIMUSensors()
		#self.initUltraSonicSensors()

		print("Threads have been started")
		pass



	def initUltraSonicSensors(self):
		self.USonicThread = USSensor()

		self.USonicThread.start()  


	def initIMUSensors(self):
		print("Binding to port")
		#~ connect()
		self._msgServerThread = msgServer(dataTransferMode.BLUETOOTH)
		self._msgServerThread.start()


	def polData(self):
		self.USonicThread.getDistance()
		self._msgServerThread.getLeftIMUData()
		delay(250)

if __name__ == '__main__':
	_mainServer = mainSensorAcquistion()
	_mainServer.start()



