from machine import Pin
import json
import time
import misurazione
import socket
import picowifi
import network
import rp2

if __name__ == "__main__":

    # variabili principali
    numeroRilevazione = 1
    sommaUmidita = 0
    sommaTemperatura = 0
    ledStato = Pin(15, Pin.OUT)

    # lettura configurazione cabina e ponte
    with open("configurazionedc.conf", 'r') as file:
        configurazioneDispositivo = json.load(file)

    # lettura parametri di connessione al server
    with open("da.json", 'r') as file:
        parametriServer = json.load(file)

    # tempi di attesa per la connessione WiFi
    tempoAttesaConnessione = 10
    tempoPausaConnessione = 1

    # recupero SSID e password dal modulo picowifi
    ssidWifi, passwordWifi = picowifi.Parametri_WiFi()

    # impostazione paese per regolamentazione WiFi
    rp2.country('IT')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # assegno wlan al modulo picowifi
    picowifi.wlan = wlan

    # disattivo powersaving per maggiore stabilità
    picowifi.Powersaving('NO')

    # stampa informazioni WiFi
    picowifi.Info_WiFi()

    # connessione alla rete WiFi
    picowifi.Connessione_WiFi(
        tempoAttesaConnessione,
        ssidWifi,
        passwordWifi,
        tempoPausaConnessione
    )

    print("WiFi connesso. Avvio comunicazione con server...")

    # ciclo infinito di invio dati al server
    while True:

        try:
            # creazione socket client TCP
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # connessione al server
            clientSocket.connect((parametriServer['IP'], parametriServer['porta']))

            ledStato.value(1)

            # ricezione parametri dal server
            datiRicevutiSocket = clientSocket.recv(4096)

            # conversione bytes → JSON
            parametriRicevutiServer = json.loads(datiRicevutiSocket.decode('utf-8'))

            # lettura temperatura e umidità dal sensore
            temperatura, umidita = misurazione.leggi_temp(
                parametriRicevutiServer['N_DECIMALI']
            )

            # aggiornamento somme per calcolo media finale
            sommaUmidita += umidita
            sommaTemperatura += temperatura

            # creazione JSON da inviare al server
            jsonDaInviare = {

                "cabina": configurazioneDispositivo['cabina'],

                "ponte": configurazioneDispositivo['ponte'],

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
                    "rilevazione": numeroRilevazione,
                    "temperatura": temperatura,
                    "umidita": umidita
                }
            }

            print(json.dumps(jsonDaInviare, indent=4))

            # conversione JSON → bytes
            jsonBytes = json.dumps(jsonDaInviare).encode('utf-8')

            # invio dati al server
            clientSocket.sendall(jsonBytes)

            # incremento contatore rilevazioni
            numeroRilevazione += 1

            # attesa prima della prossima rilevazione
            time.sleep(parametriRicevutiServer['TEMPO_RILEVAZIONE'])

        except KeyboardInterrupt:

            ledStato.value(0)
            clientSocket.close()

            print("Interruzione del salvataggio dei dati")

            print("Rilevazioni effettuate:", numeroRilevazione - 1)

            print(
                "Media umidita:",
                round(sommaUmidita / numeroRilevazione,
                parametriRicevutiServer['N_DECIMALI'])
            )

            print(
                "Media temperatura:",
                round(sommaTemperatura / numeroRilevazione,
                parametriRicevutiServer['N_DECIMALI'])
            )

            break

    print("Salvataggio dei dati sui file completato.")