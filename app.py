import json
from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)
import time
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
from counterfit_shims_grove.grove_light_sensor_v1_2 import GroveLightSensor
import json
import requests


connection_string = "HostName=greenhouse-ubaya.azure-devices.net;DeviceId=smart-gardening-sensor;SharedAccessKey=t25ek8UiJJBPE2N8SenkEQkSsi7IMPgaPWU94JynF6c="

device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)

print('Connecting')

try:
    device_client.connect()
    print('Connected')
    raspberrypi_id = "pi3b-1"
    
    def insert_log(sensor_id, value, status):
        api_url = "https://ubaya.fun/hybrid/160419017/tugas_akhir/insert_log.php"
        todo = {"sensor_id": sensor_id, "value": value, "status": status, "raspberry_id": raspberrypi_id}
        response = requests.post(api_url, todo)
        response.json()
   
    while True:
        api_url = "https://ubaya.fun/hybrid/160419017/tugas_akhir/sensorlist.php"
        todo = {"raspberry_id": raspberrypi_id}
        response = requests.post(api_url, todo) 
        data = response.json()['data']
        
        def handle_method_request(request):
            print("Direct method received - " + request.name)
            for i in data:  
                relay = GroveRelay(i['actuator_port']) 
                value = request.payload                   
                if request.name == i['sensor_id']+"_relay_on": 
                    insert_log(i['sensor_id'], value, "relay_on")                   
                    print("id: " + i['sensor_id'] + " sensor: " + i['sensor_name'] + " port: " + i['sensor_port'] + " value: " + str(value))
                    relay.on()
                    print("relay " + i['actuator_port'][1:] +" = on")
                elif request.name == i['sensor_id']+"_relay_off":
                    insert_log(i['sensor_id'], value, "relay_off")   
                    print("id: " + i['sensor_id'] + " sensor: " + i['sensor_name'] + " port: " + i['sensor_port'] + " value: " + str(value))
                    relay.off()
                    print("relay " + i['actuator_port'][1:] +" = off")
                method_response = MethodResponse.create_from_method_request(request, 200)
                device_client.send_method_response(method_response) 
        

        def send_message(sensor_id, sensor_name, sensor_value): 
            device_client.on_method_request_received = handle_method_request               
            message = Message(json.dumps({'sensor_id': sensor_id , 'sensor_name': sensor_name ,'value': sensor_value}))    
            device_client.send_message(message)
            
        for i in data:
            try:
                if i['sensor_name'] == 'soil-moisture-sensor':
                    value = ADC().read(i['sensor_port'][1:])
                elif i['sensor_name'] == 'light-sensor':
                    value = GroveLightSensor(i['sensor_port'][1:]).light                     
                send_message(i['sensor_id'], i['sensor_name'], value)
            except:
                print(i['sensor_name'] + ' from port A' + i['sensor_port'] + ' was disconnected from raspberry')      

        time.sleep(5)
except:
    print("connection failure")