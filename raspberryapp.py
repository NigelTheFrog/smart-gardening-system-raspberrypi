import json
import requests
import time
import RPi.GPIO as gp  
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
                            print("Servo berputar menuju 180")                                                
                            for s in range(0, 180, +1):
                                servo.setAngle(s)
                                time.sleep(0.003)
                            d[1] = 1  
                        else:
                            servo.setAngle(180)
                            print("Servo stay di 180")              
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
                            print("Servo berputar menuju 0")                               
                            for s in range(180, 0, -1):
                                servo.setAngle(s)
                                time.sleep(0.003)
                            d[1] = 0
                        else:
                            servo.setAngle(0)
                            print("Servo stay di 0")
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