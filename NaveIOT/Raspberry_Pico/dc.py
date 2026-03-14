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
    with open("configurazionedc.json", 'r') as file:
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
        clientSocket = None # Inizializzo a None per sicurezza
        try:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((parametriServer['IP'], parametriServer['porta']))

            ledStato.value(1)

            # Ricezione parametri
            datiRicevutiSocket = clientSocket.recv(4096)
            parametriRicevutiServer = json.loads(datiRicevutiSocket.decode('utf-8'))

            # --- CORREZIONE 1: Casting forzato a intero ---
            n_decimali = int(parametriRicevutiServer['N_DECIMALI'])
            tempo_attesa = int(parametriRicevutiServer['TEMPO_RILEVAZIONE'])

            # Misurazione
            temperatura, umidita = misurazione.leggi_temp(n_decimali)
            sommaUmidita += umidita
            sommaTemperatura += temperatura

            # ... (resto del codice per il JSON invariato) ...

            print(f"Invio rilevazione {numeroRilevazione}...")
            clientSocket.sendall(json.dumps(jsonDaInviare).encode('utf-8'))

            numeroRilevazione += 1
            
            # Chiudo il socket subito dopo l'invio per liberare memoria
            clientSocket.close() 
            
            time.sleep(tempo_attesa)

        except KeyboardInterrupt:
            # ... gestione interrupt ...
            break
            
        except Exception as e:
            print(f"Errore durante il ciclo: {e}")
            if clientSocket:
                clientSocket.close() # --- CORREZIONE 2: Chiudo SEMPRE il socket ---
            time.sleep(5)

