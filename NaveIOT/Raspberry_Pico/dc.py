from machine import Pin
import json
import time
import misurazione
import socket
import wifidc 
import network
import rp2

if __name__ == "__main__":
    # Variabili principali
    numeroRilevazione = 1
    sommaUmidita = 0
    sommaTemperatura = 0
    ledStato = Pin(15, Pin.OUT)

    # 1. Lettura configurazioni
    with open("configurazione.json", 'r') as file:
        configurazioneDispositivo = json.load(file)

    with open("da.json", 'r') as file:
        parametriServer = json.load(file)

    # 2. Inizializzazione Hardware WiFi (Fondamentale farlo PRIMA delle funzioni del modulo)
    rp2.country('IT')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Passiamo l'oggetto wlan al modulo wifidc
    wifidc.wlan = wlan

    # 3. Recupero credenziali e connessione
    # Nota: nel tuo modulo la funzione si chiama Parametri_WiFi, non connetti_wifi
    ssidWifi, passwordWifi = wifidc.Parametri_WiFi()

    # Disattivo powersaving
    wifidc.Powersaving('NO')

    # Stampa info e connette
    wifidc.Info_WiFi()
    
    tempoAttesaConnessione = 10
    tempoPausaConnessione = 1
    
    wifidc.Connessione_WiFi(tempoAttesaConnessione,ssidWifi,passwordWifi,tempoPausaConnessione)

    print("WiFi pronto. Avvio ciclo comunicazione...")

    while True:
        try:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((parametriServer['IP'], parametriServer['porta']))

            ledStato.value(1)

            # Ricezione parametri
            datiRicevutiSocket = clientSocket.recv(4096)
            parametriRicevutiServer = json.loads(datiRicevutiSocket.decode('utf-8'))

            # Misurazione
            temperatura, umidita = misurazione.leggi_temp(parametriRicevutiServer['N_DECIMALI'])
            sommaUmidita += umidita
            sommaTemperatura += temperatura

            # Preparazione JSON
            jsonDaInviare = {
                "cabina": configurazioneDispositivo['cabina'],
                "ponte": configurazioneDispositivo['ponte'],
                "sensore": {
                    "nome": "DHT11", "tmin": 0, "tmax": 40, "umin": 20, "umax": 90, "erroret": 2, "erroreu": 4
                },
                "identita": "DC001-01",
                "osservazione": {
                    "rilevazione": numeroRilevazione,
                    "temperatura": temperatura,
                    "umidita": umidita
                }
            }

            print(f"Invio rilevazione {numeroRilevazione}...")
            clientSocket.sendall(json.dumps(jsonDaInviare).encode('utf-8'))

            numeroRilevazione += 1
            time.sleep(parametriRicevutiServer['TEMPO_RILEVAZIONE'])

        except KeyboardInterrupt:
            ledStato.value(0)
            clientSocket.close()
            print("\nInterruzione dell'utente.")
            
            divisore = numeroRilevazione - 1 if numeroRilevazione > 1 else 1
            print(f"Rilevazioni: {divisore}")
            print(f"Media Umidità: {round(sommaUmidita/divisore, 2)}")
            print(f"Media Temperatura: {round(sommaTemperatura/divisore, 2)}")
            break
        except Exception as e:
            print(f"Errore durante il ciclo: {e}")
            time.sleep(5) # Attesa prima di riprovare in caso di errore rete
