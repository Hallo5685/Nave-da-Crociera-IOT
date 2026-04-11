import json
import paho.mqtt.client as mqtt
import crypto  # noqa: E402


# lettura dei parametri MQTT dal file locale
with open("iotp.json", "r") as f:
    parametriMQTT = json.load(f)

MQTT_BROKER = parametriMQTT["broker"]["host"]
MQTT_PORT = parametriMQTT["broker"]["porta"]
MQTT_TOPIC = parametriMQTT["topic"]
DBPLATFORM_PATH = parametriMQTT["dbfile"]["file"]
DBPLATFORM_MODE = parametriMQTT["dbfile"]["modo"]


# callback di connessione al broker

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connesso al broker {MQTT_BROKER}:{MQTT_PORT}")
    client.subscribe(MQTT_TOPIC)
    print(f"Sottoscritto al topic: {MQTT_TOPIC}")


# callback quando arriva un messaggio

def on_message(client, userdata, msg):
    try:
        # payload ricevuto dal topic MQTT
        dati = msg.payload.decode("utf-8")
        print(f"\nMessaggio ricevuto da topic {msg.topic}")

        try:
            # tentativo di decriptazione del messaggio
            dati_decriptati = crypto.decriptazione(dati)
            payload = json.loads(dati_decriptati)
        except Exception:
            # se non serve decriptare usa direttamente il payload
            payload = json.loads(dati)

        # salvataggio del JSON nell'archivio testuale
        with open(DBPLATFORM_PATH, DBPLATFORM_MODE, encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False))
            f.write("\n")

        print("Dati non criptati ricevuti dal gateway:", payload)
    except Exception as err:
        print(f"Errore elaborazione messaggio: {err}")


if __name__ == "__main__":
    print(f"Archivio dati: {DBPLATFORM_PATH}")

    # creazione del client MQTT e registrazione callback
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # connessione al broker e avvio ciclo di ascolto
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
