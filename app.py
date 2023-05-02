from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay
from counterfit_shims_grove.grove_light_sensor_v1_2 import GroveLightSensor
from counterfit_shims_seeed_python_dht import DHT
import json
import requests
import time
# from seeed_dht import DHT
# from grove.adc import ADC
# from grove.grove_light_sensor_v1_2 import GroveLightSensor
# from grove.grove_relay import GroveRelay
# from grove.grove_servo import GroveServo
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse



#koneksi pada azure
connection_string = "HostName=greenhouse-ubaya.azure-devices.net;DeviceId=smart-gardening-sensor;SharedAccessKey=t25ek8UiJJBPE2N8SenkEQkSsi7IMPgaPWU94JynF6c="
device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
print('Connecting')
wait_time = []

# try:
device_client.connect()
print('Connected')
#deklarasi id raspberry
raspberrypi_id = "pi-3b-1"

def insert_log(id, value, status):
    api_url = "http://192.168.137.1//tugas_akhir/log/insert_log.php"
    todo = {"id": id, "value": value, "status": status}
    response = requests.post(api_url, todo)
    response.json()
    
def insert_error_log(id, error_code):
    api_url = "http://192.168.137.1/tugas_akhir/log/insert_error_log.php"
    todo = {"id": id, "error_code" : error_code}
    response = requests.post(api_url, todo)
    response.json()

def handle_method_request(request):
    global wait_time
    print("Direct method received - " + request.name)
    for i in data: 
        print(i) 
        if request.name == i['id']+"_method_on": 
            if i['nama_sensor'] == 'Sensor Cahaya':
                GroveServo(i['port_aktuator'][1:]).setAngle(90)
                message = "Papan terbuka"
            elif i['nama_sensor'] == 'Sensor Temperatur':
                GroveRelay(i['port_aktuator'][1:]).on()
                message = "Kipas angin menyala"
            else:
                GroveRelay(i['port_aktuator'][1:]).on()
                x = [i['id'],25]
                wait_time.append(x)   
                message = "Pompa menyala"  
            print("id: " + i['id'] + " sensor: " + i['nama_sensor'] + " port: " + i['port_sensor'] + " value: " + str(value))
            print("Aktuator " + i['port_aktuator'][1:] +" = on")          
        elif request.name == i['id']+"_method_off":
            if i['nama_sensor'] == 'Sensor Cahaya':
                GroveServo(i['port_aktuator'][1:]).setAngle(0)
                message = "Papan tertutup"
            elif i['nama_sensor'] == 'Sensor Temperatur':
                GroveRelay(i['port_aktuator'][1:]).off()
                message = "Kipas angin mati"
            else:
                GroveRelay(i['port_aktuator'][1:]).off()
                message = "Pompa mati"
            print("id: " + i['id'] + " sensor: " + i['nama_sensor'] + " port: " + i['port_sensor'] + " value: " + str(value))
            print("Aktuator " + i['port_aktuator'][1:] +" = off")
        elif request.name == i['id']+"_waiting":
            GroveRelay(i['port_aktuator'][1:]).off()
            message = "Menunggu tanah menyerap cairan"
            print("relay " + i['port_aktuator'] +" = waiting") 
        insert_log(i['id'], request.payload, message)                   
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
    wait_time = [ele for ele in wait_time if ele != []]     
    todo = []  

        
    for i in data:
        wait = 0
        todo.append(i['id'], i['nama_sensor'], value, wait)
        if i['nama_sensor'] == 'Sensor Kelembaban Tanah':
            value = ADC().read(i['port_sensor'][1:])
            send_message(i['id'], i['nama_sensor'], value, wait)
        elif i['nama_sensor'] == 'water-sensor':
            value = ADC().read(i['port_sensor'][1:])
            if value < 100:
                insert_error_log(i['id'], "S1")
        elif i['nama_sensor'] == 'light-sensor':
            value = GroveLightSensor(i['port_sensor'][1:]).light
            send_message(i['id'], i['nama_sensor'], value, wait)
        elif i['nama_sensor'] == 'temperature-sensor':
            _,value = DHT("11", i['port_sensor'][1:])   
            send_message(i['id'], i['nama_sensor'], value, wait)              
        for w in wait_time:
            if w[0] == i['id']:
                if w[1] > 0:
                    w[1] -= 5
                    wait = w[1]
                else:
                    del w[0:]
                    wait = 0 
        
        # except:
        #     print("error")
            #insert_error_log(i['id'],"S2")
    time.sleep(5)       
# except:
#     print("Connection failure")          