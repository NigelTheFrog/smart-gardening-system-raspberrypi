import logging
import json
import os
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
import azure.functions as func

      

def main(event: func.EventHubEvent):
    body = json.loads(event.get_body().decode('utf-8'))
    device_id = event.iothub_metadata['connection-device-id']    
    
    logging.info(f'Received message: {body} from {device_id}')
    
    if body['sensor_name'] == 'soil-moisture-sensor':
        if body['value'] < 450:
            direct_method = CloudToDeviceMethod(method_name=body['sensor_id']+'_relay_on', payload=body["value"])   
        else:
            direct_method = CloudToDeviceMethod(method_name=body['sensor_id']+'_relay_off', payload=body["value"]) 
    elif body['sensor_name'] == 'light-sensor':
        if body['value'] < 200:
            direct_method = CloudToDeviceMethod(method_name=body['sensor_id']+'_relay_on', payload=body["value"])   
        else:
            direct_method = CloudToDeviceMethod(method_name=body['sensor_id']+'_relay_off', payload=body["value"])   

    logging.info(f'Sending direct method request for {direct_method.method_name} for device {device_id}')

    registry_manager_connection_string = os.environ['REGISTRY_MANAGER_CONNECTION_STRING']
    registry_manager = IoTHubRegistryManager(registry_manager_connection_string)
    
    registry_manager.invoke_device_method(device_id, direct_method)

    logging.info('Direct method request sent!')                                  