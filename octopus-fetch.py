import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OCTOPUS_API_KEY")
mpanm = os.getenv("OCTOPUS_MPANM")
meter_serial = os.getenv("OCTOPUS_METER_SERIAL")
token = os.getenv("INFLUXDB_TOKEN")
org = "matt"
url = "http://grafana.lan:8086"
bucket="octopus"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def run():

    print(f"Running at {datetime.now()}")

    url = f"https://api.octopus.energy/v1/electricity-meter-points/{mpanm}/meters/{meter_serial}/consumption/"
    params = {
        "page_size": 5,
    }
    response = requests.get(url=url, auth=(api_key, ''), params=params)
    data = response.json()

    for item in data['results']:
        timestamp = datetime.strptime(item['interval_start'], "%Y-%m-%dT%H:%M:%S%z").isoformat()
        consumption = item['consumption']
        
        point = (
            Point("electricity_consumption")
            .field("consumption", consumption)
            .time(timestamp, WritePrecision.S)
        )
        write_api.write(bucket=bucket, org=org, record=point)


def main():
    while True:
        run()
        time.sleep(3600)

if __name__ == '__main__':
    main()
