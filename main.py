#-*- coding: utf-8 -*-

# Modules for python
import threading

# Modules for AD-DAC
import time
import RPi.GPIO as GPIO
from ADC import ADS1256
from DAC import DAC8532

# Modules for GUI
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

from kivy.properties import StringProperty

from kivy.config import Config
from kivy.core.window import Window

# Initializing
Window.fullscreen = True
Window.size = (800, 480)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
DAC = DAC8532.DAC8532()
ADC = ADS1256.ADS1256()
ADC_Value = []
class UFBWidget(BoxLayout):
	# Kivy's internal property
	switch_text = StringProperty()
	flow_text = StringProperty()
	vacuum_text = StringProperty()
	revo_text = StringProperty()

	# Other properties
	active_time = 0.0
	interval_time = 0.0
	start_time = 0.0
	flag = False


	
	def __init__(self, **kwargs):
		super(UFBWidget, self).__init__(**kwargs)
		self.switch_text = 'OFF'
		self.flow_text = '0.0'
		ADCthread = threading.Thread(target=self.readValue)
		ADCthread.start()
	
	def switch_callback(self, instance, value):
		if value:
			# Setting of Active and interval time
			self.active_time = float(self.ids['active_hour'].text) + float(self.ids['active_min'].text)/60.0
			self.interval_time = float(self.ids['interval_hour'].text) + float(self.ids['interval_min'].text)/60.0
			print('active time: ', self.active_time, 'interval time: ', self.interval_time)

			self.ids['active_hour'].disabled = True
			self.ids['active_min'].disabled = True
			self.ids['interval_hour'].disabled = True
			self.ids['interval_min'].disabled = True
			
			self.flag = True
			motor_th = threading.Thread(target=self.measure_time)
			motor_th.start()
		else:
			DAC.DAC8532_Out_Voltage(DAC8532.channel_A, 0)
			self.ids['active_hour'].disabled = False
			self.ids['active_min'].disabled = False
			self.ids['interval_hour'].disabled = False
			self.ids['interval_min'].disabled = False
			self.flag = False

	def readValue(self):
		try:
			while(1):
				ADC_Value = ADC.ADS1256_GetAll()
				self.flow_text = str(round(ADC_Value[0]*5.0/0x7fffff, 2))
				self.vacuum_text = str(round(ADC_Value[1]*5.0/0x7fffff, 2))
				self.revo_text = str(round(ADC_Value[2]*5.0/0x7fffff, 2))

		except :
    			GPIO.cleanup()
    			print ("\r\nADC Erorr     ")
    			exit()

	def measure_time(self):
		active_sec = 3600 * self.active_time
		interval_sec = 3600 * self.interval_time
		print('active_sec: ', active_sec, 'interval_sec', interval_sec)
		dt = 0
		while(self.flag == True):
			# Motor active for active time
			start_time = time.time()
			dt = 0
			DAC.DAC8532_Out_Voltage(DAC8532.channel_A, 5.0)
			while(active_sec > dt):
				current_time = time.time()
				dt = current_time - start_time
				time.sleep(0.1)

			# Rest for interval time
			start_time = time.time()
			dt = 0
			DAC.DAC8532_Out_Voltage(DAC8532.channel_A, 0.0)
			while(interval_sec > dt):
				current_time = time.time()
				dt = current_time - start_time
				time.sleep(0.1)
			
		

class UFBMonitor(App):
	global ADC_Value
	def __init__(self, **kwargs):
		super(UFBMonitor, self).__init__(**kwargs)
		self.title = 'UFB Monitor'
		# DACの初期化　
		DAC.DAC8532_Out_Voltage(DAC8532.channel_A, 0)
		DAC.DAC8532_Out_Voltage(DAC8532.channel_B, 0)
		# ADCの初期化
		ADC.ADS1256_init()

		

	


if __name__ == "__main__":
	
	UFBMonitor().run()


