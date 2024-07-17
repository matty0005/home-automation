import paho.mqtt.client as mqtt
import json

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Influx settings
token = os.getenv("INFLUXDB_TOKEN")
org = "matt"
url = "http://grafana.scotchegg.uk:8086"
bucket="mi_temps"

# MQTT settings
BROKER = 'grafana.scotchegg.uk'
PORT = 1883  # Default MQTT port
MI_TOPIC = 'mi/#'

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)




def mqtt_on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(MI_TOPIC)

def mqtt_on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())

        point = (
            Point(data['sensor'])
            .field("humidity", data['humidity'])
            .field("voltage", data['voltage'])
            .field("rssi", data['rssi'])
            .field("temperature", data['temperature'])
            .field("battery", data['battery'])
        )
        write_api.write(bucket=bucket, org=org, record=point)


    except json.JSONDecodeError:
        print("Failed to decode JSON from message payload")




def main():
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message

    mqtt_client.connect(BROKER, PORT, 60)

    mqtt_client.loop_forever()

if __name__ == '__main__':
    main()
