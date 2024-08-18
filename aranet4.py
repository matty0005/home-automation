import pexpect
import time
import paho.mqtt.client as mqtt #import the client1
import time
import sys
 
MAC_ADDR = "60:c0:bf:48:8d:78"
broker_address = "mqtt_server"
broker_username = "username"
broker_psw = "password"

# Run gatttool interactively.
#print("Run gatttool...")
try:
   child = pexpect.spawn("gatttool -t random -b " + MAC_ADDR + " -l high --char-read -a 0x38")
except pexpect.TIMEOUT:
   print "timeout, giving up."
   sys.exit("could not connect to Aranet over BLE") # if something goes wrong

child.expect("Characteristic value/descriptor: ", timeout=10)
child.expect("\r\n", timeout=10)

print(int(child.before[3:5]+child.before[0:2],16)),
print("ppm")

client = mqtt.Client("RPi")
client.username_pw_set(broker_username, broker_psw)
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
json_body = {
      "co2": int(child.before[3:5]+child.before[0:2],16),
      "temp": float(int(child.before[9:11]+child.before[6:8],16)/20.0)
}

client.publish("aranet4", json.dumps(json_body))

time.sleep(4) # wait ... because example had it ;)
client.loop_stop() #stop the loop