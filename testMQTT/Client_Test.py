import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Ricevuto messaggio sul topic {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message

client.connect("test.mosquitto.org", 1883)
client.subscribe("progetto/test/comandi")

print("In attesa di messaggi...")
client.loop_forever()