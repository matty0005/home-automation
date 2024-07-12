import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
from datetime import datetime, timedelta

api_key = os.environ.get("OCTOPUS_API_KEY")
mpanm = os.environ.get("OCTOPUS_MPANM")
meter_serial = os.environ.get("OCTOPUS_METER_SERIAL")
token = os.environ.get("INFLUXDB_TOKEN")
org = "matt"
url = "http://10.10.0.85:8086"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)


bucket="octopus"

write_api = client.write_api(write_options=SYNCHRONOUS)
   

url = f"https://api.octopus.energy/v1/electricity-meter-points/{mpanm}/meters/{meter_serial}/consumption/"
params = {
    "page_size": 5,
}
response = requests.get(url=url, auth=(api_key, ''), params=params)
data = response.json()

# Write data to InfluxDB
for item in data['results']:
    timestamp = datetime.strptime(item['interval_start'], "%Y-%m-%dT%H:%M:%S%z").isoformat()
    consumption = item['consumption']
    
    point = (
        Point("electricity_consumption")
        .field("consumption", consumption)
        .time(timestamp, WritePrecision.S)
    )
    print(point)
    write_api.write(bucket=bucket, org=org, record=point)

