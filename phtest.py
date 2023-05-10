
import board
import busio
import time
import sys
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Setup 
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

while True:
    buf = list()
    
    for i in range(10): # Take 10 samples
        buf.append(AnalogIn(ads, ADS.P1).voltage)
    buf.sort() # Sort samples and discard highest and lowest
    buf = buf[2:-2]
    avg = (sum(map(float,buf))/6) # Get average value from remaining 6

    print(round(avg,4),'V')
    time.sleep(2)

# import time
# from grovepi import *

# # Connect the PH-4502C pH sensor to analog port A4
# sensor = 4


# # Read the analog voltage output from the sensor
# def read_voltage():
#     voltage = analogRead(sensor)
#     if voltage == -1:
#         return None
#     else:
#         return voltage / 1023.0 * 5.0

# # Continuously read and print the voltage output
# while True:
#     voltage = read_voltage()
#     if voltage is not None:
#         ph = voltage_to_ph(voltage)
#         print("Voltage: %.2f V, pH: %.2f" % (voltage, ph))
#     time.sleep(1)
#     # except KeyboardInterrupt:
#     #     print("Exiting...")
#     #     break
#     # except IOError:
#     #     print("Error: Unable to read analog value")

# import time
# from grove.i2c import Bus
# from grove.adc import ADC

# # Connect the PH-4502C pH sensor to the Grove Base Hat ADC channel A0
# adc = ADC(busnum=1, address=0x48)
# channel = 4

# # Calibration parameters for the pH sensor
# pH_7 = 1.81  # Voltage output of the sensor at pH 7
# slope = -0.247  # Slope of the linear equation relating pH to voltage

# # Read the analog voltage output from the sensor and convert it into a pH value
# def read_ph():
#     voltage = adc.read_voltage(channel)
#     pH = slope * (voltage - pH_7) + 7.0
#     return pH

# # Continuously read and print the pH value
# while True:
#     pH = read_ph()
#     print("pH value: ", pH)
#     time.sleep(1)
    
# import time
# import grovepi

# # Setup ADC
# grovepi.pinMode(4,"INPUT")

# def read_voltage():
#     # Read voltage from ADC
#     sensor = 4
#     time.sleep(0.1) # add delay
#     sensor_value = grovepi.analogRead(sensor)
#     # Convert ADC value to voltage
#     voltage = (float)(sensor_value * 5) / 1024
#     return voltage

# def read_ph():
#     # Read pH value from sensor
#     voltage = read_voltage()
#     ph = 3.5 * voltage - 1.75
#     return ph

# if __name__ == '__main__':
#     print('\n\n\n')
#     print('---- Raspberry Pi Grove Base Hat pH4502C Calibration ----')
#     input('Press Enter once you have connected the sensor to A4...')
#     print('Starting readings. Press CTRL+C to stop...')
#     try:
#         while True:
#             volt = read_voltage()
#             ph = read_ph()
#             print('Voltase: ', volt)
#             print('pH:', round(ph, 2))
#             time.sleep(2)
#     except KeyboardInterrupt:
#         pass