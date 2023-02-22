import requests
import json

api_url = "https://ubaya.fun/hybrid/160419017/tugas_akhir/insert_log.php"
todo = {"sensor_id": "A2-ligth-sensor-D24", "value": "800", "status": "relay_off"}
response = requests.post(api_url, todo)
response.json()

print(response.status_code)