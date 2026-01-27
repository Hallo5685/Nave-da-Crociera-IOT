import json
import time
import misurazione
import socket

if __name__ == "__main__":
    
    #definizione costanti
    HOST = '127.0.0.1' 
    PORT = 9999

    #definizione variabili
    rilevazione = 1
    umiditaMedia = 0
    temperaturaMedia = 0

    # Apertura di configurazionedc.conf in lettura
    with open("configurazionedc.conf", 'r') as file:
        datiDC = json.load(file)

    # Ciclo di estrazione dei dati e di scrittura in file iotdata.dbt in formato JSON
    while True:

        try:

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((datiDC['IPServer'], datiDC['portaServer']))

            readSocket = client.recv(4096)
            # bytes → stringa → dict
            datiDA = json.loads(readSocket.decode('utf-8'))

            temperatura = misurazione.on_temperatura(datiDA['N_DECIMALI'])
            umidita = misurazione.on_umidita(datiDA['N_DECIMALI'])

            umiditaMedia += umidita
            temperaturaMedia += temperatura

            JSON = {
                "cabina": datiDC['cabina'],
                "ponte": datiDC['ponte'],
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

            # stampa leggibile dei dati estrapolati
            # print(json.dumps(JSON, indent=4))

            dati_bytes = json.dumps(JSON).encode('utf-8')
            client.sendall(dati_bytes)

            rilevazione += 1
            time.sleep(datiDA['TEMPO_RILEVAZIONE'])
        except KeyboardInterrupt as e:
            client.close()
            print("Interruzione del salvataggio dei dati")
            #per motivi tecnici il valore "rilevazione" è sballato in eccesso di 1, quindi quel 1 in eccesso viene sottratto alla stampa 
            print("Rilevazioni effettuate: ", rilevazione-1)
            print("Media umidita: ", round(umiditaMedia/rilevazione, datiDA['N_DECIMALI']))
            print("Media temperatura: ", round(temperaturaMedia/rilevazione, datiDA['N_DECIMALI']))
            break

    print("Salvataggio dei dati sui file completato.")
