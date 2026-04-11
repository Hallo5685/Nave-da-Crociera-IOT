from machine import Pin
import json
import time
import socket
import network
import rp2
import misurazione
import wifidc

#cosante da tenere
TEMPO_ATTESA_WIFI = 10
TEMPO_PAUSA_WIFI = 1
TEMPO_RITENTA_ERRORE = 5
BUFFER_SIZE = 4096


def carica_json(nome_file):
    with open(nome_file, "r") as file:
        return json.load(file)


def crea_led_interno():
    try:
        return Pin("LED", Pin.OUT)
    except Exception:
        return Pin(15, Pin.OUT)


def misura_dati(n_decimali):
    temperatura, umidita = misurazione.leggi_temp(n_decimali)
    temperatura = round(float(temperatura), n_decimali)
    umidita = round(float(umidita), n_decimali)
    return temperatura, umidita


def costruisci_iotdata(configurazione, numero_rilevazione, temperatura, umidita):
    chiave_posizione = "camera" if "camera" in configurazione else "cabina"

    dato = {
        chiave_posizione: configurazione.get(chiave_posizione, 1),
        "ponte": configurazione.get("ponte", 1),
        "sensore": configurazione.get("sensore", {}),
        "identita": configurazione.get("identita", "DC001-00001"),
        "osservazione": {
            "rilevazione": numero_rilevazione,
            "temperatura": temperatura,
            "umidita": umidita,
            "dataeora": int(time.time()),
        },
    }
    return dato


def inizializza_wifi():
    rp2.country("IT")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wifidc.wlan = wlan

    ssid_wifi, password_wifi = wifidc.Parametri_WiFi()
    wifidc.Powersaving("NO")
    wifidc.Connessione_WiFi(
        TEMPO_ATTESA_WIFI,
        ssid_wifi,
        password_wifi,
        TEMPO_PAUSA_WIFI,
    )
    return wlan


if __name__ == "__main__":
    led_stato = crea_led_interno()
    led_stato.off()

    configurazione_dispositivo = carica_json("configurazionedc.json")
    #apertura del file da.json
    parametri_server = carica_json("da.json")
    #apertura del file parametri.json
    config_parametri = carica_json("../p3/configurazione/parametri.json")

    inizializza_wifi()
    print("WiFi pronto. DC avviato.")

    numero_rilevazione = 1
    tempo_rilevazione = config_parametri.get("TEMPO_RILEVAZIONE")
    n_decimali = config_parametri.get("N_DECIMALI")

    while True:
        client_socket = None
        try:
            #creazione soket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((parametri_server["IP"], parametri_server["porta"]))

            dati_ricevuti_socket = client_socket.recv(BUFFER_SIZE)
            if dati_ricevuti_socket:
                parametri_ricevuti_server = json.loads(dati_ricevuti_socket.decode("utf-8"))
                n_decimali = int(parametri_ricevuti_server.get("N_DECIMALI", n_decimali))
                tempo_rilevazione = int(parametri_ricevuti_server.get("TEMPO_RILEVAZIONE", tempo_rilevazione))

            temperatura, umidita = misura_dati(n_decimali)
            json_da_inviare = costruisci_iotdata(configurazione_dispositivo, numero_rilevazione,temperatura,umidita,)

            print("DatoIoT inviato a iotgwda.py:")
            print(json.dumps(json_da_inviare))

            led_stato.on()
            client_socket.sendall(json.dumps(json_da_inviare).encode("utf-8"))
            led_stato.off()

            numero_rilevazione += 1

            client_socket.close()
            client_socket = None

            time.sleep(tempo_rilevazione)

        except KeyboardInterrupt:
            led_stato.off()
            if client_socket is not None:
                try:
                    client_socket.close()
                except Exception:
                    pass
            print("\nDC terminato manualmente.")
            break

        except Exception as errore:
            led_stato.off()
            print("Errore nel DC:", errore)
            if client_socket is not None:
                try:
                    client_socket.close()
                except Exception:
                    pass
            time.sleep(TEMPO_RITENTA_ERRORE)
