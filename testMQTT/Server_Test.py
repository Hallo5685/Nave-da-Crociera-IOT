import paho.mqtt.client as mqtt
import time

broker = "test.mosquitto.org"
port = 1883
topic = "progetto/test/comandi"

client = mqtt.Client()
client.connect(broker, port)

while True:
    messaggio = "ACCENDI_LED"
    client.publish(topic, messaggio)
    print(f"Inviato: {messaggio}")
    time.sleep(3) # Invia ogni 3 secondi
