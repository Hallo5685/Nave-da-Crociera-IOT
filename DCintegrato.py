import json
import time
import socket

# -------------------------------
#  SEZIONE: LETTURA SENSORE DHT
# -------------------------------
from machine import Pin
import dht

PIN_SEGNALE = 0  # Pin del sensore DHT11/DHT22

# Scegli il sensore corretto
sensor = dht.DHT11(Pin(PIN_SEGNALE))
# sensor = dht.DHT22(Pin(PIN_SEGNALE))

def leggi_temp():
    """
    Legge temperatura e umidità dal sensore DHT.
    Restituisce (temperatura, umidità)
    """
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        return temp, hum
    except OSError:
        print("Problemi con il sensore...")
        return None, None


# -------------------------------
#  PROGRAMMA PRINCIPALE
# -------------------------------
if __name__ == "__main__":

    rilevazione = 1
    umiditaMedia = 0
    temperaturaMedia = 0

    # Lettura configurazione
    with open("configurazionedc.conf", 'r') as file:
        datiDC = json.load(file)

    while True:
        try:
            # Connessione al server
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((datiDC['IPServer'], datiDC['portaServer']))

            readSocket = client.recv(4096)
            datiDA = json.loads(readSocket.decode('utf-8'))

            # -------------------------------
            #  LETTURA REALE DAL SENSORE
            # -------------------------------
            temperatura, umidita = leggi_temp()

            if temperatura is None or umidita is None:
                temperatura = 0
                umidita = 0

            temperatura = round(temperatura, datiDA['N_DECIMALI'])
            umidita = round(umidita, datiDA['N_DECIMALI'])

            umiditaMedia += umidita
            temperaturaMedia += temperatura

            JSON = {
                "cabina": datiDC['cabina'],
                "ponte": datiDC['ponte'],
                "sensore": {
                    "nome": "DHT11",
                    "tmin": 0,
                    "tmax": 40,
                    "umin": 20,
                    "umax": 90,
                    "erroret": 2,
                    "erroreu": 4
                },
                "identita": "DC001-01",
                "osservazione": {
                    "rilevazione": rilevazione,
                    "temperatura": temperatura,
                    "umidita": umidita
                }
            }

            dati_bytes = json.dumps(JSON).encode('utf-8')
            client.sendall(dati_bytes)

            rilevazione += 1
            time.sleep(datiDA['TEMPO_RILEVAZIONE'])

        except KeyboardInterrupt:
            client.close()
            print("Interruzione del salvataggio dei dati")
            print("Rilevazioni effettuate:", rilevazione - 1)
            print("Media umidità:", round(umiditaMedia / rilevazione, datiDA['N_DECIMALI']))
            print("Media temperatura:", round(temperaturaMedia / rilevazione, datiDA['N_DECIMALI']))
            break

    print("Salvataggio dei dati completato.")
