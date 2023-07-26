from flask import Flask, request
import paho.mqtt.client as mqtt
import time
import json

app = Flask(__name__)

# MQTT broker configuration
broker_address = "test.mosquitto.org"
broker_port = 1883
payload_data = ""

# Create an MQTT client
mqtt_client = mqtt.Client()

# Connect to the MQTT broker
mqtt_client.connect(broker_address, broker_port)
# Define the 'truffle' endpoint
@app.route('/truffle', methods=['POST'])
def truffle_endpoint():
    global payload_data
    data = json.loads(request.get_data(as_text=True))
    truffletype=data["color"]
    print(truffletype)
    mqtt_client.publish('truffles', truffletype)
    print('Sent message to "truffles":', truffletype)
    while payload_data == "":
      time.sleep(0.5)
    truffleselect = truffle_selection(truffletype)
    payload_data = ""
    return truffleselect

# Define the 'trufflecontrol' endpoint
@app.route('/trufflecontrol', methods=['POST'])
def trufflecontrol_endpoint():
    data = json.loads(request.get_data(as_text=True))
    msg=data["trufflecontrol"]
    mqtt_client.publish('trufflecontrol', msg)
    print('Sent message to "trufflecontrol":', msg)
    return 'Message received from "trufflecontrol"'

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    # Subscribe to the 'trufflelist' topic
    mqtt_client.subscribe('trufflelist')

# MQTT on_message callback
def on_message(client, userdata, msg):
    global payload_data
    if msg.topic == 'trufflelist':
        payload_data = msg.payload.decode()
        print('Received message on "trufflelist" topic:', payload_data)
        return("msg received")


def truffle_selection(truffletype):
    global payload_data
    trufflenotfound = True
    print("Selected truffle is: ", truffletype)
    #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    data = json.loads(payload_data)
    for key in data["detectedobjects"]:
        print(key["label"])
        if key["label"] == truffletype:
          print("xmin, ymin, xmax, ymax", key["xmin"], key["ymin"], key["xmax"], key["ymax"])
          avgx = int(key["xmin"])+(int(key["xmax"])-int(key["xmin"]))/2
          print("Avg X: ", avgx)
          avgy = int(key["ymin"])+(int(key["ymax"])-int(key["ymin"]))/2
          print("Avg Y: ", avgy)
          area = get_area(avgx, avgy)
          print("Area: ", area)
          trufflenotfound = False
          print("Please position your hand under Roboto's claw in order to retrieve your {} truffle".format(truffletype))
          mqtt_client.publish('trufflecontrol', area)
          return("Please position your hand under Roboto's claw in order to retrieve your {} truffle".format(truffletype))
    if trufflenotfound:
        return("No {} truffle left! Please choose another one".format(truffletype))


def get_area(x, y):
  areas = [((0, 0), (170, 200)), ((170, 0), (300, 200)), ((300, 0), (450, 200)), ((450, 0), (600, 200)), ((0, 200), (150, 400)),((150, 200), (300, 400)),((300, 200), (450, 400)),((450, 200), (600, 400))]

  for i, ((x1t, y1t), (x1b, y1b)) in enumerate(areas):
    if x1t <= x <= x1b and y1t <= y <= y1b:
      return f"{i+1}"
  return "No area"


# Set the MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Start the MQTT client loop in a separate thread
print("MQTT Start")
mqtt_client.loop_start()

# Start the Flask web server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 8080)
