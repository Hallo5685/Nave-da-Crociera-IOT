import socket
import json
import time
import datetime
import crypto as crypto

if __name__ == "__main__":

    # variabili per il calcolo delle medie
    temperaturaTotale = 0
    umiditaTotale = 0
    numeroMisurazioni = 0

    # timer per l'invio dei dati al database
    ultimoInvioDatabase = time.time()

    # lettura parametri di configurazione del server
    with open('configurazione/parametri.conf', 'r') as file:
        parametriServer = json.load(file)

    # conversione dei parametri in bytes per inviarli al client
    parametriServerBytes = json.dumps(parametriServer).encode('utf-8')

    # creazione del server TCP
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

            # estrazione valori di temperatura e umidità
            temperatura = datiRicevutiJson['osservazione']['temperatura']
            umidita = datiRicevutiJson['osservazione']['umidita']

            # aggiornamento somme per il calcolo della media
            temperaturaTotale += temperatura
            umiditaTotale += umidita
            numeroMisurazioni += 1

            connessioneClient.close()

            # controllo se è arrivato il momento di salvare i dati
            if time.time() - ultimoInvioDatabase >= parametriServer['TEMPO_INVIO'] and numeroMisurazioni > 0:

                temperaturaMedia = round(
                    temperaturaTotale / numeroMisurazioni,
                    parametriServer['N_DECIMALI']
                )

                umiditaMedia = round(
                    umiditaTotale / numeroMisurazioni,
                    parametriServer['N_DECIMALI']
                )

                # JSON da salvare nel database
                jsonDatabase = {
                    "invioNumero": numeroMisurazioni,
                    "cabina": datiRicevutiJson['cabina'],
                    "ponte": datiRicevutiJson['ponte'],
                    "temperaturaMedia": temperaturaMedia,
                    "umiditaMedia": umiditaMedia,
                    "dataOra": datetime.datetime.now().timestamp(),
                    "identitaGiot": parametriServer['IDENTITA_GIOT']
                }

                # conversione JSON formattato
                jsonString = json.dumps(
                    jsonDatabase,
                    ensure_ascii=False,
                    indent=4
                )

                # criptazione
                jsonCriptato = crypto.criptazione(jsonString)

                # salvataggio nel file
                with open("iotp/db.json", "a", encoding="utf-8") as file:
                    file.write(jsonCriptato + "\n")

                print("Dati salvati nel DB")

                # reset delle variabili per il prossimo intervallo
                temperaturaTotale = 0
                umiditaTotale = 0
                numeroMisurazioni = 0

                # reset timer invio
                ultimoInvioDatabase = time.time()

        except KeyboardInterrupt:
            print("Server interrotto manualmente")
            break