#main app.py
import json
import requests
import time
from seeed_dht import DHT
from grove.adc import ADC
from grove.grove_light_sensor_v1_2 import GroveLightSensor
from grove.grove_relay import GroveRelay
from grove.grove_servo import GroveServo
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
from grove.grove_servo import GroveServo



#koneksi pada azure
connection_string = "HostName=greenhouse-ubaya.azure-devices.net;DeviceId=smart-gardening-sensor;SharedAccessKey=t25ek8UiJJBPE2N8SenkEQkSsi7IMPgaPWU94JynF6c="
device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
print('Connecting')
wait_time = []
servo_degree = []


# try:
device_client.connect()
print('Connected')
#deklarasi id raspberry
raspberrypi_id = "pi-3b-1"
    
def insert_log(id, value, message):
    api_url = "http://192.168.137.1//tugas_akhir/log/insert_log.php"
    todo = {"id": id, "value": value, "status": message}
    response = requests.post(api_url, todo)
    response.json()
    
def insert_error_log(id, error_code):
    api_url = "http://192.168.137.1/tugas_akhir/log/insert_error_log.php"
    todo = {"id": id, "error_code" : error_code}
    response = requests.post(api_url, todo)
    response.json()


def handle_method_request(request):
    global wait_time    
    global servo_degree
    for i in data: 
        if request.name == i['id']+"_method_on": 
            if i['nama_sensor'] == 'Sensor Cahaya':
                print("sensor id: " + i['id'] + ", sensor name: " + i['nama_sensor'] + "\nPort aktuator: " + i['port_aktuator'][1:] + ", value: " + str(request.payload)) 
                servo = GroveServo(int(i['port_aktuator'][1:]))
                for d in servo_degree:
                    if d[0] == i['id']:   
                        if d[1] == 0: 
                            for s in range(0, 180, +1):
                                servo.setAngle(s)
                                time.sleep(0.003)
                            d[1] = 1  
                        else:
                            servo.setAngle(180)
                insert_log(i['id'],str(request.payload), "Papan terbuka")  
            elif i['nama_sensor'] == 'Sensor Suhu':
                GroveRelay(int(i['port_aktuator'][1:])).on()
                print("sensor id: " + i['id'] + ", sensor name: " + i['nama_sensor'] + "\nPort aktuator: " + i['port_aktuator'][1:] + ", value: " + str(request.payload)) 
                insert_log(i['id'],str(request.payload), "Kipas angin menyala")  
            else:
                GroveRelay(int(i['port_aktuator'][1:])).on()
                if i['nama_sensor'] == 'Sensor Kelembaban Tanah':
                    x = [i['id'],25]
                elif i['nama_sensor'] == 'Sensor pH':
                    x = [i['id'],65]    
                wait_time.append(x) 
                print("sensor id: " + i['id'] + ", sensor name: " + i['nama_sensor'] + "\nPort aktuator: " + i['port_aktuator'][1:] + ", value: " + str(request.payload)) 
                insert_log(i['id'],str(request.payload), "Pompa menyala" )        
        elif request.name == i['id']+"_method_off":
            if i['nama_sensor'] == 'Sensor Cahaya':
                print("sensor id: " + i['id'] + ", sensor name: " + i['nama_sensor'] + "\nPort aktuator: " + i['port_aktuator'][1:] + ", value: " + str(request.payload)) 
                servo = GroveServo(int(i['port_aktuator'][1:]))
                for d in servo_degree:
                    if d[0] == i['id']:
                        if d[1] == 1:  
                            for s in range(180, 0, -1):
                                servo.setAngle(s)
                                time.sleep(0.003)
                            d[1] = 0
                        else:
                            servo.setAngle(0)
                insert_log(i['id'],str(request.payload), "Papan tertutup")  
            elif i['nama_sensor'] == 'Sensor Suhu':
                GroveRelay(int(i['port_aktuator'][1:])).off()
                print("sensor id: " + i['id'] + ", sensor name: " + i['nama_sensor'] + "\nPort aktuator: " + i['port_aktuator'][1:] + ", value: " + str(request.payload)) 
                insert_log(i['id'],str(request.payload),  "Kipas angin mati")  
            else:                
                GroveRelay(int(i['port_aktuator'][1:])).off()
                print("sensor id: " + i['id'] + ", sensor name: " + i['nama_sensor'] + "\nPort aktuator: " + i['port_aktuator'][1:] + ", value: " + str(request.payload)) 
                insert_log(i['id'],str(request.payload), "Pompa mati")  
        elif request.name == i['id']+"_waiting":            
            GroveRelay(int(i['port_aktuator'][1:])).off()
            print("sensor id: " + i['id'] + ", sensor name: " + i['nama_sensor'] + "\nPort aktuator: " + i['port_aktuator'][1:] + ", value: " + str(request.payload)) 
            insert_log(i['id'],str(request.payload), "Menunggu tanah menyerap cairan")
    method_response = MethodResponse.create_from_method_request(request, 200)
    device_client.send_method_response(method_response) 
        
def send_message(sensor_id, sensor_name, sensor_value, wait):  
    device_client.on_method_request_received = handle_method_request               
    message = Message(json.dumps({'sensor_id': sensor_id , 'sensor_name': sensor_name ,'value': sensor_value, 'wait_time':wait}))    
    device_client.send_message(message)  
    
while True:
    api_url = "http://192.168.137.1/tugas_akhir/sensor/sensorlist.php"
    todo = {"raspberry_id": raspberrypi_id}
    response = requests.post(api_url, todo) 
    data = response.json()['data']  
    
    for i in data:
        wait_time = [ele for ele in wait_time if ele != []]      
        wait = 0
        servo_degree = [ele for ele in servo_degree if ele != []]   
        if i['nama_sensor'] == 'Sensor Kelembaban Tanah':
            value = ADC().read(int(i['port_sensor'][1:]))
            
        elif i['nama_sensor'] == 'water-sensor':
            value = ADC().read(int(i['port_sensor'][1:]))
            if value < 100:
                insert_error_log(i['id'], "S1")
        elif i['nama_sensor'] == 'Sensor Cahaya':
            value = GroveLightSensor(int(i['port_sensor'][1:])).light  
            if servo_degree == []:
                y = [i['id'], 0]
                servo_degree.append(y)
            else :
                for d in servo_degree:
                    if d[0] != i['id'] :   
                        y = [i['id'], 0]
                        servo_degree.append(y) 
        elif i['nama_sensor'] == 'Sensor Suhu':
            _,value = DHT("11", int(i['port_sensor'][1:])).read()
        for w in wait_time:
            if w[0] == i['id']:
                if w[1] > 0:
                    w[1] -= 5
                    wait = w[1]
                else:
                    del w[0:]
                    wait = 0 
        
        send_message(i['id'], i['nama_sensor'], value, wait)
        # except:
        #     print("error")
        #     insert_error_log(i['id'],"S2")
    time.sleep(5)       
# except:
#     print("Connection failure")          

#phtest.py


# import board
# import busio
# import time
# import sys
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn

# # Setup 
# i2c = busio.I2C(board.SCL, board.SDA)
# ads = ADS.ADS1115(i2c)

# while True:
#     buf = list()
    
#     for i in range(10): # Take 10 samples
#         buf.append(AnalogIn(ads, ADS.P1).voltage)
#     buf.sort() # Sort samples and discard highest and lowest
#     buf = buf[2:-2]
#     avg = (sum(map(float,buf))/6) # Get average value from remaining 6

#     print(round(avg,2),'V')
#     time.sleep(2)

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

import time
from grove.i2c import Bus
from grove.adc import ADC

# Connect the PH-4502C pH sensor to the Grove Base Hat ADC channel A0
adc = ADC(busnum=1, address=0x48)
channel = 4

# Calibration parameters for the pH sensor
pH_7 = 1.81  # Voltage output of the sensor at pH 7
slope = -0.247  # Slope of the linear equation relating pH to voltage

# Read the analog voltage output from the sensor and convert it into a pH value
def read_ph():
    voltage = adc.read_voltage(channel)
    pH = slope * (voltage - pH_7) + 7.0
    return pH

# Continuously read and print the pH value
while True:
    pH = read_ph()
    print("pH value: ", pH)
    time.sleep(1)
    
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