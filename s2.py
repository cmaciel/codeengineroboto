from flask import Flask, request
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)

# MQTT broker configuration
broker_address = "192.168.29.84"
broker_port = 1883
broker_username = "your_mqtt_username"
broker_password = "your_mqtt_password"
payload_data = ""

# Create an MQTT client
mqtt_client = mqtt.Client()

# Connect to the MQTT broker
#mqtt_client.username_pw_set(broker_username, broker_password)
mqtt_client.connect(broker_address, broker_port)

# Define the 'truffle' endpoint
@app.route('/truffle', methods=['POST'])
def truffle_endpoint():
    global payload_data
    data = request.get_data(as_text=True)
    mqtt_client.publish('truffle', data)
    while payload_data == "":
      time.sleep(0.5)
    msg = payload_data
    payload_data = ""
    return msg

# Define the 'trufflecontrol' endpoint
@app.route('/trufflecontrol', methods=['POST'])
def truffle_control_endpoint():
    data = request.get_data(as_text=True)
    print('Received message from "trufflecontrol":', data)
    return 'Message received from "trufflecontrol"'

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    # Subscribe to the 'trufflecontrol' topic
    mqtt_client.subscribe('trufflecontrol')

# MQTT on_message callback
def on_message(client, userdata, msg):
    global payload_data
    if msg.topic == 'trufflecontrol':
        payload_data = msg.payload.decode()
        print('Received message on "trufflecontrol" topic:', payload_data)
        return("msg received")

# Set the MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Start the MQTT client loop in a separate thread
print("MQTT Start")
mqtt_client.loop_start()

# Start the Flask web server
if __name__ == '__main__':
    app.run(host="0.0.0.0")