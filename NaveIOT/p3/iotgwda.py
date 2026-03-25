import socket
import json
import time
import datetime
import crypto as crypto
import paho.mqtt.publish as publish


if __name__ == "__main__":

    # variabili per il calcolo delle medie
    temperaturaTotale = 0
    umiditaTotale = 0
    numeroMisurazioni = 0

    # timer per l'invio dei dati
    ultimoInvioDatabase = time.time()

    # lettura parametri di configurazione
    with open('configurazione/parametri.conf', 'r') as file:
        parametriServer = json.load(file)

    # conversione dei parametri in bytes per inviarli al client
    parametriServerBytes = json.dumps(parametriServer).encode('utf-8')

    # creazione del server TCP (rimane per ricevere dai sensori)
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((parametriServer['IP_SERVER'], parametriServer['PORTA_SERVER']))
    serverSocket.listen(5)

    print(f"Server in ascolto su {parametriServer['IP_SERVER']}:{parametriServer['PORTA_SERVER']}")

    while True:
        try:
            connessioneClient, indirizzoClient = serverSocket.accept()
            print(f"Connessione da {indirizzoClient}")

            # invio parametri al client
            connessioneClient.sendall(parametriServerBytes)

            # ricezione dati dal client
            datiRicevutiBytes = connessioneClient.recv(4096)
            datiRicevutiJson = json.loads(datiRicevutiBytes.decode('utf-8'))

            print("Dati ricevuti dal client:", datiRicevutiJson)

            # estrazione valori
            temperatura = datiRicevutiJson['osservazione']['temperatura']
            umidita = datiRicevutiJson['osservazione']['umidita']

            # aggiornamento somme
            temperaturaTotale += temperatura
            umiditaTotale += umidita
            numeroMisurazioni += 1

            connessioneClient.close()

            # controllo invio
            if time.time() - ultimoInvioDatabase >= parametriServer['TEMPO_INVIO'] and numeroMisurazioni > 0:

                temperaturaMedia = round(
                    temperaturaTotale / numeroMisurazioni,
                    parametriServer['N_DECIMALI']
                )

                umiditaMedia = round(
                    umiditaTotale / numeroMisurazioni,
                    parametriServer['N_DECIMALI']
                )

                # JSON finale
                jsonDatabase = {
                    "cabina": datiRicevutiJson['cabina'],
                    "ponte": datiRicevutiJson['ponte'],
                    "temperaturam": temperaturaMedia,
                    "umiditam": umiditaMedia,
                    "dataeora": datetime.datetime.now().timestamp(),
                    "invionumero": numeroMisurazioni,
                    "identita": parametriServer['IDENTITA_GIOT']
                }

                # conversione JSON
                jsonString = json.dumps(jsonDatabase, ensure_ascii=False, indent=4)

                # criptazione (simulata)
                jsonCriptato = crypto.criptazione(jsonString)

                # ---------------- MQTT PUBLISH ----------------
                try:
                    publish.single(
                        topic=parametriServer["TOPIC"],
                        payload=jsonCriptato,
                        hostname=parametriServer["BROKER"],
                        port=parametriServer["PORTA_BROKER"]
                    )
                    print("Dati pubblicati su MQTT")
                except Exception as err:
                    print(f"Errore MQTT: {err}")
                # ------------------------------------------------

                print("Dati inviati tramite MQTT")

                # reset variabili
                temperaturaTotale = 0
                umiditaTotale = 0
                numeroMisurazioni = 0

                ultimoInvioDatabase = time.time()

        except KeyboardInterrupt:
            print("Server interrotto manualmente")
            break