from flask import Flask, jsonify
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv

# Initialize the Flask app
app = Flask(__name__)

load_dotenv()

# Influx settings
INFLUXDB_URL = "http://grafana.scotchegg.uk:8086"  # Update with your InfluxDB URL
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = "matt"
INFLUXDB_BUCKET = "mi_temps" 

# Initialize InfluxDB Client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

@app.route('/api/temperatures', methods=['GET'])
def get_latest_temperature():
    try:
        # Query to get the most recent temperature value
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1h)  // Query for the last hour, adjust as needed
          |> filter(fn: (r) => r._field == "temperature")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 1)
        '''
        
        # Execute the query
        query_api = client.query_api()
        result = query_api.query(org=INFLUXDB_ORG, query=query)

        # Parse the result
        temperatures = []
        for table in result:
            for record in table.records:
                temperatures.append({
                    'measurement': record.get_measurement(),
                    'time': record.get_time(),
                    'value': record.get_value()
                })

        # Return the most recent temperature value as JSON
        if temperatures:
            temperatures = {item["measurement"].lower(): item["value"] for item in temperatures}
            return jsonify(temperatures), 200
        else:
            return jsonify({"error": "No data found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
