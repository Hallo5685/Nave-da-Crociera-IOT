import json
import paho.mqtt.client as mqtt
import crypto  # noqa: E402

with open("iotp.json", "r") as f:
    parametriMQTT = json.load(f)

MQTT_BROKER = parametriMQTT["broker"]["host"]
MQTT_PORT = parametriMQTT["broker"]["porta"]
MQTT_TOPIC = parametriMQTT["topic"]
DBPLATFORM_PATH = parametriMQTT["dbfile"]["file"]
DBPLATFORM_MODE = parametriMQTT["dbfile"]["modo"]


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connesso al broker {MQTT_BROKER}:{MQTT_PORT}")
    client.subscribe(MQTT_TOPIC)
    print(f"Sottoscritto al topic: {MQTT_TOPIC}")


# callback quando arriva un messaggio

def on_message(client, userdata, msg):
    try:
        dati = msg.payload.decode("utf-8")
        print(f"\nMessaggio ricevuto da topic {msg.topic}")

        try:
            dati_decriptati = crypto.decriptazione(dati)
            payload = json.loads(dati_decriptati)
        except Exception:
            payload = json.loads(dati)

        with DBPLATFORM_PATH.open(DBPLATFORM_MODE, encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False))
            f.write("\n")

        print("Dati non criptati ricevuti dal gateway:", payload)
    except Exception as err:
        print(f"Errore elaborazione messaggio: {err}")


if __name__ == "__main__":
    print(f"Archivio dati: {DBPLATFORM_PATH}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
