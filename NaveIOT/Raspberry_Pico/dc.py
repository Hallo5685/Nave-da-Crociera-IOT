from machine import Pin
import json
import time
import misurazione
import socket

if __name__ == "__main__":
    #definizione variabili
    rilevazione = 1
    umiditaMedia = 0
    temperaturaMedia = 0
    led = Pin(15, Pin.OUT)  # Usa GP15 come output

    # Apertura di configurazionedc.conf in lettura
    with open("configurazionedc.conf", 'r') as file:
        datiConfigurazioneDC = json.load(file)

    with open("da.json", 'r') as file:
        datiConnessioneServer = json.load(file)

    # Ciclo di estrazione dei dati e di scrittura in file iotdata.dbt in formato JSON
    while True:

        try:
            # Creazione del client socket
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((datiConnessioneServer['IP'], datiConnessioneServer['porta']))

            led.value(1)    # Accendi il LED
            readSocket = client.recv(4096)
            # Converte il bytes letti in stringa
            datiDA = json.loads(readSocket.decode('utf-8'))

            # Prende dal file misurazione.py i dati relativi alla temperatura e dell'umidita
            temperatura, umidita = misurazione.leggi_temp(datiDA['N_DECIMALI'])

            umiditaMedia += umidita
            temperaturaMedia += temperatura

            JSON = {
                "cabina": datiConfigurazioneDC['cabina'],
                "ponte": datiConfigurazioneDC['ponte'],
                "sensore":
                {
                    "nome":"DHT11",
                    "tmin":0,
                    "tmax":40,
                    "umin":20,
                    "umax":90,
                    "erroret":2,
                    "erroreu":4
                },
                "identita":"DC001-01",
                "osservazione":
                {
                    "rilevazione": rilevazione,
                    "temperatura": temperatura,
                    "umidita": umidita
                },
            }

            dati_bytes = json.dumps(JSON).encode('utf-8')
            client.sendall(dati_bytes)

            rilevazione += 1
            time.sleep(datiDA['TEMPO_RILEVAZIONE'])
        except KeyboardInterrupt as e:
            led.value(0)    # Spegni il LED
            client.close()
            print("Interruzione del salvataggio dei dati")
            #per motivi tecnici il valore "rilevazione" è sballato in eccesso di 1, quindi quel 1 in eccesso viene sottratto alla stampa 
            print("Rilevazioni effettuate: ", rilevazione-1)
            print("Media umidita: ", round(umiditaMedia/rilevazione, datiDA['N_DECIMALI']))
            print("Media temperatura: ", round(temperaturaMedia/rilevazione, datiDA['N_DECIMALI']))
            break

    print("Salvataggio dei dati sui file completato.")