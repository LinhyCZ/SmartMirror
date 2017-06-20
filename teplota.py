import RPi.GPIO as GPIO
import dht11
import time
import datetime

#Nastavi piny GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.cleanup()

#Vytvori promennou obsahujici cidlo na pinu 7
cidlo = dht11.DHT11(pin = 7)

#Funkce pro cteni teploty
def read_temp():
	data = cidlo.read()
	intx = data.temperature
	#Pokud data nejsou validni, pokus se znovu nacist hodnotu
	while not data.is_valid():
		data = cidlo.read()
		intx = data.temperature
	return intx

#Funkce pro cteni vlhkosti
def read_hum():
	data = cidlo.read()
	intx = data.humidity
	#Pokud data nejsou validni, pokus se znovu nacist hodnotu
	while not data.is_valid():
		data = cidlo.read()
		intx = data.humidity
	return intx