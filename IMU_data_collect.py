#!/usr/bin/python

import smbus
import math
import time
import csv
from MPU6050 import MPU6050
import datetime


DATA_NAME = "MANUAL_TEST_HR_2.csv"
#import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('QT4Agg')
#from matplotlib import pyplot as plt


#print("Back end: ",  matplotlib.get_backend())


# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
def read_byte(reg):
    return bus.read_byte_data(address, reg)
 
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value
 
def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
 
bus = smbus.SMBus(1) 
address = 0x68       # via i2cdetect
 
bus.write_byte_data(address, power_mgmt_1, 0)

sensor = MPU6050(0x68)
sensor.set_gyro_range(MPU6050.GYRO_RANGE_2000DEG)
run_time = 1  # seconds


x_acc = []
y_acc = []
z_acc = []
x_rot = []
y_rot = []
z_rot = []
timeX = []
startTime = time.time()
t_end = startTime + 35
  
#pltFig = plt.figure()
#plt.ion()

#ax = pltFig.add_subplot(1,1,1)
#def plotData():
    #ax.clear()
    #ax.plot(timeX ,x_acc)
    
    #plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')
    #plt.axis([0, 6, 0, 20])
    #plt.clear()
 #   plt.plot(timeX ,x_acc)
  #  plt.show()
   # plt.pause(0.00001)

       
def plotLive():
    #plt.set_xdata(timeX)
    #plt.set_ydata(x_acc)
    #plt.scatter(timeX, x_acc)
        
    plt.subplot(2,3,1)
    plt.plot(timeX, x_acc)
    plt.title('X Acc')

    plt.subplot(2,3,2)
    plt.plot(timeX, y_acc)
    plt.title('Y Acc')

    plt.subplot(2,3,3)
    plt.plot(timeX, z_acc)
    plt.title('Z Acc')

    plt.subplot(2,3,4)
    plt.plot(timeX, x_rot)
    plt.title('X Acc')

    plt.subplot(2,3,5)
    plt.plot(timeX, y_rot)
    plt.title('Y Acc')

    plt.subplot(2,3,6)
    plt.plot(timeX, z_rot)
    plt.title('Z Acc')
    plt.pause(0.0001)
    plt.show()

def plotFinal():

    for i in xrange(len(x_acc)):
        x_acc[i] = x_acc[i] / 16384.0
        y_acc[i] = y_acc[i] / 16384.0
        z_acc[i] = z_acc[i] / 16384.0
        x_rot[i] = -x_rot[i] / 16.4
        y_rot[i] = -y_rot[i] / 16.4
        z_rot[i] = -z_rot[i] / 16.4
        
    plt.subplot(2,3,1)
    plt.plot(timeX, x_acc)
    plt.title('X Acc')

    plt.subplot(2,3,2)
    plt.plot(timeX, y_acc)
    plt.title('Y Acc')

    plt.subplot(2,3,3)
    plt.plot(timeX, z_acc)
    plt.title('Z Acc')

    plt.subplot(2,3,4)
    plt.plot(timeX, x_rot)
    plt.title('X Acc')

    plt.subplot(2,3,5)
    plt.plot(timeX, y_rot)
    plt.title('Y Acc')

    plt.subplot(2,3,6)
    plt.plot(timeX, z_rot)
    plt.title('Z Acc')
    plt.pause(0.0001)
    plt.show()


while(time.time() < t_end):
    loopStartTime = time.time()
    #print "Gyro"
    #print "--------"
         
    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)
    
    #print "gyro_xout: ", ("%5d" % gyro_xout), " scaled: ", (gyro_xout / 131)
    #print "gyro_yout: ", ("%5d" % gyro_yout), " scaled: ", (gyro_yout / 131)
        #print "gyro_zout: ", ("%5d" % gyro_zout), " scaled: ", (gyro_zout / 131)
         
        #print
        #print "Accelerometer"
        #print "---------------------"
         
    acc_xout = read_word_2c(0x3b)
    acc_yout = read_word_2c(0x3d)
    acc_zout = read_word_2c(0x3f)
         
    acc_xout_scaled = acc_xout / 16384.0
    acc_yout_scaled = acc_yout / 16384.0
    acc_zout_scaled = acc_zout / 16384.0
         
        #print "acc_xout: ", ("%6d" % acc_xout), " scaled: ", acc_xout_scaled
        #print "acc_yout: ", ("%6d" % acc_yout), " scaled: ", acc_yout_scaled
        #print "acc_zout: ", ("%6d" % acc_zout), " scaled: ", acc_zout_scaled

    x_acc.append(acc_xout_scaled)
    y_acc.append(acc_yout_scaled)
    z_acc.append(acc_zout_scaled)

    x_rot.append(gyro_xout/131.0)
    y_rot.append(gyro_yout/131.0)
    z_rot.append(gyro_zout/131.0)
    
    

    loopTime = time.time() - loopStartTime
        #t_end += loopTime
        
    currTime = time.time() - startTime
    timeX.append(currTime)
        #plotLive()
    
    #print([timeX[0], x_acc[0], y_acc[0], z_acc[0], x_rot[0], y_rot[0], z_rot[0]])
    #break

with open("./mpu_data/"+DATA_NAME, 'w') as dataf:
    csvWriter = csv.writer(dataf)
    csvWriter.writerow(datetime.datetime.now().strftime("%H:%M:%S"))
    for i in range(0,len(x_acc)):
        csvWriter.writerow([timeX[i], x_acc[i], y_acc[i], z_acc[i], x_rot[i], y_rot[i], z_rot[i]])
    dataf.close()

print(len(x_acc))

'''
plotFinal()

#plotData()
'''
