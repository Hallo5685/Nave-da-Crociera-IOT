import json
import socket
import time
from datetime import datetime
from pathlib import Path
import crypto
import paho.mqtt.publish as publish

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "configurazione" / "parametri.json"
STATUS_ATTESA = "Gateway IoT in attesa di dati"
STATUS_RICEZIONE = "Gateway IoT in ricezione e invio"


def carica_parametri():
    with open('configurazione/parametri.json', 'r') as file:
        parametriServer = json.load(file)


if __name__ == "__main__":
    parametri_server = carica_parametri()

    temperatura_totale = 0.0
    umidita_totale = 0.0
    numero_misurazioni = 0
    numero_invio = 0
    ultimo_invio_database = time.time()
    ultimo_stato = None
    ultimo_payload_ricevuto = None

    parametri_server_bytes = json.dumps(parametri_server).encode("utf-8")

    #creazione della soket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((parametri_server["IP_SERVER"], parametri_server["PORTA_SERVER"]))
    server_socket.listen(5)
    server_socket.settimeout(0.5)

    print(f"Server in ascolto su {parametri_server['IP_SERVER']}:{parametri_server['PORTA_SERVER']}")

    while True:
        try:
            try:
                if ultimo_stato != STATUS_ATTESA:
                    print(STATUS_ATTESA)
                    ultimo_stato = STATUS_ATTESA

                #fase di accettazione    
                connessione_client, indirizzo_client = server_socket.accept()
            except socket.timeout:
                connessione_client = None

            if connessione_client is not None:
                with connessione_client:
                    connessione_client.sendall(parametri_server_bytes)
                    dati_ricevuti_bytes = connessione_client.recv(4096)
                
                #se non ci sono dati ricevuti continua
                if not dati_ricevuti_bytes:
                    continue

                dati_ricevuti_json = json.loads(dati_ricevuti_bytes.decode("utf-8"))
                ultimo_payload_ricevuto = dati_ricevuti_json

                print(f"Connessione da {indirizzo_client}")
                print("Dati ricevuti dal client:", dati_ricevuti_json)

                temperatura = dati_ricevuti_json["osservazione"]["temperatura"]
                umidita = dati_ricevuti_json["osservazione"]["umidita"]

                temperatura_totale += temperatura
                umidita_totale += umidita
                numero_misurazioni += 1

            if (ultimo_payload_ricevuto is not None and numero_misurazioni > 0 and time.time() - ultimo_invio_database >= parametri_server["TEMPO_INVIO"]):
                temperatura_media = round(temperatura_totale / numero_misurazioni, parametri_server["N_DECIMALI"],)
                umidita_media = round(umidita_totale / numero_misurazioni, parametri_server["N_DECIMALI"],)
                numero_invio += 1

                json_database = {
                    "cabina": ultimo_payload_ricevuto["cabina"],
                    "ponte": ultimo_payload_ricevuto["ponte"],
                    "temperaturam": temperatura_media,
                    "umiditam": umidita_media,
                    "dataeora": int(datetime.now().timestamp()),
                    "invionumero": numero_invio,
                    "identita": parametri_server["IDENTITA_GIOT"],
                }

                json_string = json.dumps(json_database, ensure_ascii=False)
                json_criptato = crypto.criptazione(json_string)

                try:
                    if ultimo_stato != STATUS_RICEZIONE:
                        print(STATUS_RICEZIONE)
                        ultimo_stato = STATUS_RICEZIONE

                    publish.single(
                        topic=parametri_server["TOPIC"],
                        payload=json_criptato,
                        hostname=parametri_server["BROKER"],
                        port=parametri_server["PORTA_BROKER"],
                    )
                    print(f"Dati pubblicati su MQTT nel topic {parametri_server['TOPIC']}")
                except Exception as err:
                    print(f"Errore MQTT: {err}")

                temperatura_totale = 0.0
                umidita_totale = 0.0
                numero_misurazioni = 0
                ultimo_invio_database = time.time()

        except KeyboardInterrupt:
            print("Server interrotto manualmente")
            break
        except Exception as err:
            print(f"Errore gateway: {err}")

    server_socket.close()
