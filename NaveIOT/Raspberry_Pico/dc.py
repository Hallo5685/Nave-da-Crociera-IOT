from machine import Pin
import json
import time
import misurazione
import socket
import picowifi
import network
import rp2

if __name__ == "__main__":
    # definizione variabili principali
    rilevazione = 1
    umiditaMedia = 0
    temperaturaMedia = 0
    led = Pin(15, Pin.OUT)  # Usa GP15 come output per il LED di stato

    # Apertura di configurazionedc.conf in lettura (parametri cabina e ponte)
    with open("configurazionedc.conf", 'r') as file:
        datiConfigurazioneDC = json.load(file)

    # Apertura file da.json in lettura (parametri connessione server)
    with open("da.json", 'r') as file:
        datiConnessioneServer = json.load(file)

    # tempi di attesa per la connessione WiFi
    ATTESA = 10
    TEMPO_PAUSA = 1

    # recupero SSID e password dal modulo picowifi
    SSID, PASW = picowifi.Parametri_WiFi()

    # imposto il paese per la regolamentazione WiFi
    rp2.country('IT')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)  # attiva la modalità station

    # assegno wlan al modulo picowifi per poterlo usare nelle funzioni
    picowifi.wlan = wlan

    # disattivo powersaving per maggiore stabilità
    picowifi.Powersaving('NO')

    # stampa informazioni WiFi
    picowifi.Info_WiFi()

    # connessione alla rete WiFi
    picowifi.Connessione_WiFi(ATTESA, SSID, PASW, TEMPO_PAUSA)

    print("WiFi connesso. Avvio comunicazione con server...")
    
    # Ciclo infinito di estrazione dei dati e invio al server
    while True:

        try:
            # Creazione del client socket TCP
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connessione al server tramite IP e porta letti dal file
            client.connect((datiConnessioneServer['IP'], datiConnessioneServer['porta']))

            led.value(1)    # Accendi il LED quando la comunicazione è attiva

            # Ricezione dati dal server (massimo 4096 byte)
            readSocket = client.recv(4096)

            # Converte i bytes letti in stringa e poi in dizionario JSON
            datiDA = json.loads(readSocket.decode('utf-8'))

            # Prende dal file misurazione.py i dati relativi alla temperatura e dell'umidita
            # il numero di decimali viene deciso dal server
            temperatura, umidita = misurazione.leggi_temp(datiDA['N_DECIMALI'])

            # somma progressiva per il calcolo della media finale
            umiditaMedia += umidita
            temperaturaMedia += temperatura

            # Creazione struttura JSON da inviare al server
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

            # Conversione del dizionario in bytes JSON
            dati_bytes = json.dumps(JSON).encode('utf-8')

            # Invio dei dati al server
            client.sendall(dati_bytes)

            # incremento contatore rilevazioni
            rilevazione += 1

            # attesa prima della prossima rilevazione (tempo deciso dal server)
            time.sleep(datiDA['TEMPO_RILEVAZIONE'])

        except KeyboardInterrupt as e:
            led.value(0)    # Spegni il LED in caso di interruzione manuale
            client.close()  # chiusura della connessione socket
            print("Interruzione del salvataggio dei dati")

            # per motivi tecnici il valore "rilevazione" è sballato in eccesso di 1,
            # quindi quel 1 in eccesso viene sottratto alla stampa 
            print("Rilevazioni effettuate: ", rilevazione-1)

            # calcolo e stampa delle medie finali
            print("Media umidita: ", round(umiditaMedia/rilevazione, datiDA['N_DECIMALI']))
            print("Media temperatura: ", round(temperaturaMedia/rilevazione, datiDA['N_DECIMALI']))
            break

    print("Salvataggio dei dati sui file completato.")
