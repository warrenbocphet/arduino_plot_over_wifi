import sys
import time
import socket
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

pg.setConfigOptions(antialias=True)
# probe1 = time.time()

def bytes2coor(byte_fnc):
	receivedData_fnc = [0, 0]

	receivedData_fnc[0] = ((-1)**(byte_fnc[0]>>7)) * ((byte_fnc[1]) | (((byte_fnc[0]&0x7f)<<8)))
	receivedData_fnc[1] = ((-1)**(byte_fnc[2]>>7)) * ((byte_fnc[3]) | (((byte_fnc[2]&0x7f)<<8)))

	return receivedData_fnc

class plotting_window:

	def __init__(self, socket_input, start_time):
		self.socket = socket_input
		self.start_timestamp = start_time

		self.app = QtGui.QApplication([])

		# Windows
		self.win = pg.GraphicsWindow(title="Plot some data")
		self.win.resize(1000,600)
		self.win.setWindowTitle('Plot some data')

		# Plot
		self.plot1 = self.win.addPlot(title='Data 1')
		self.plot1.setYRange(0,1023,padding=0.1)
		self.win.nextRow()
		self.plot2 = self.win.addPlot(title='Data 2')
		self.plot2.setYRange(0,1023,padding=0.1)

		self.curve1 = self.plot1.plot(pen='b')
		self.curve2 = self.plot2.plot(pen='r')

		self.data1 = np.zeros((200,))
		self.data2 = np.zeros((200,))

		self.timestamp = np.zeros((200,))

	def get_new_data(self):
		while (True):
			try:
				self.socket.send(bytes([1]))
				bytesReceived = []
				full_msg = []

				while (len(full_msg) < 4):
					bytesReceived = self.socket.recv(8)
					for x in range(len(bytesReceived)):
						full_msg.append(bytesReceived[x])
				
				receivedData = bytes2coor(full_msg)
				elapsedTime = time.time() - self.start_timestamp
				self.timestamp[:-1] = self.timestamp[1:]
				self.timestamp[-1] = elapsedTime

				self.data1[:-1] = self.data1[1:]
				self.data1[-1] = receivedData[0]

				self.data2[:-1] = self.data2[1:]
				self.data2[-1] = receivedData[1]
			
				break

			except socket.timeout:
				pass

	def update(self):
		# global probe1
		
		# refresh_time = time.time() - probe1
		# probe1 = time.time()
		# print("Refresh time: ",refresh_time)

		self.get_new_data()

		self.curve1.setData(self.timestamp, self.data1)
		self.curve2.setData(self.timestamp, self.data2)

	def start(self):
		if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
			print("Start!")
			QtGui.QApplication.instance().exec_()

	def animation(self):
		timer = QtCore.QTimer()
		timer.timeout.connect(self.update)
		timer.start(50)
		self.start()

def main():
	print("Establishing the socket")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((socket.gethostname(), 1234)) # bind(ip, port)
	print("Done binding, now listening for connection.")
	print()
	s.listen(5)

	clientSocket, address = s.accept()
	print(f"Connection from {address} has been established!")
	clientSocket.settimeout(1)

	start = time.time()
	pw = plotting_window(clientSocket, start)
	pw.animation()

if __name__ == '__main__':
	main()
