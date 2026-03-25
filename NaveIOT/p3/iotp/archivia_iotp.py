import os
import json
import crypto
import paho.mqtt.client as mqtt

# caricamento configurazione
with open("iotp.json", "r") as f:
    parametriMQTT = json.load(f)

MQTT_BROKER = parametriMQTT["broker"]["host"]
MQTT_PORT = parametriMQTT["broker"]["porta"]
MQTT_TOPIC = parametriMQTT["topic"]
DBPLATFORM_PATH = parametriMQTT["dbfile"]["file"]

# callback quando arriva un messaggio
def on_message(client, userdata, msg):
    try:
        dati = msg.payload.decode("utf-8")

        print(f"\nMessaggio ricevuto da topic {msg.topic}")

        # decriptazione
        try:
            dati_decriptati = crypto.decriptazione(dati)
            payload = json.loads(dati_decriptati)
        except:
            # se NON criptato
            payload = json.loads(dati)

        # salvataggio su file
        with open(DBPLATFORM_PATH, parametriMQTT["dbfile"]["modo"], encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False))
            f.write("\n")

        print("Dati salvati:", payload)

    except Exception as err:
        print(f"Errore elaborazione messaggio: {err}")


if __name__ == "__main__":

    # crea cartella se non esiste
    os.makedirs("iotp", exist_ok=True)

    print(f"Connessione al broker {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Sottoscritto al topic: {MQTT_TOPIC}")
    print(f"Salvataggio dati in: {DBPLATFORM_PATH}")

    client = mqtt.Client()

    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.subscribe(MQTT_TOPIC)

    # loop infinito
    client.loop_forever()