import serial

import time 
import string  
 
import pynmea2

def get_pos():  
	while True:  
		try:
			port="/dev/ttyAMA0"
			ser=serial.Serial(port, baudrate=9600, timeout=0.25) 
			dataout =pynmea2.NMEAStreamReader() 
			newdata=ser.readline()  
			newdata = newdata.decode()

			if newdata[0:6] == "$GPRMC":  
				print('Succes')
				newmsg=pynmea2.parse(newdata)  
				lat=newmsg.latitude 
				lng=newmsg.longitude 
				gps = "Latitude=" + str(lat) + "and Longitude=" +str(lng) 
				print(gps)
				if lat != 0.0 and lng != 0.0:
					return [lat, lng]
		except:
			print("error in gps")