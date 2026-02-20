import socket
import json
import time
import datetime
import crypto as crypto

if __name__ == "__main__":
    
    #definizione variabili
    temperat_media = 0
    umidita_media = 0

    # Apertura di parametri.conf in lettura
    with open('parametri.conf', 'r') as file:
        datiDA = json.load(file)

    # Converte la stringa in bytes
    dati_bytes = json.dumps(datiDA).encode('utf-8')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((datiDA['IP_SERVER'], datiDA['PORTA_SERVER']))
    #gestisce massimo 5 host in coda
    server.listen(5)
    print("Server in ascolto su 127.0.0.1:9999")

    while True:
        try:
            conn, addr = server.accept()
            print(f"Connessione da {addr}")

            #invio dei dati di parametri.conf al client
            conn.sendall(dati_bytes)

            #ricezione dei dati dal client
            data_bites = conn.recv(4096)
            # Converte il bytes letti in stringa
            data_json = json.loads(data_bites.decode('utf-8'))
            print("Dati ricevuti dal client:")

            #estrazione dei valori di temperatura e umidità dal JSON ricevuto
            temperatura = data_json['osservazione']['temperatura']
            umidita = data_json['osservazione']['umidita']

            #somme che servono per svolgere il calcolo delle medie
            temperat_media += temperatura
            umidita_media += umidita

            #construzione del JSON da salvare nel file iotdata.dbt
            json_iotPlatform = { 
                            "invionumero" : data_json['osservazione']['rilevazione'],
                            "cabina": data_json['cabina'],
                            "ponte": data_json['ponte'],
                            "temperatura_media": round(temperat_media/data_json['osservazione']['rilevazione'] , datiDA['N_DECIMALI']),
                            "umidita_media": round(umidita_media/data_json['osservazione']['rilevazione'] , datiDA['N_DECIMALI']),
                            "data_ora": datetime.datetime.now().timestamp(),
                            "identita_giot": datiDA['IDENTITA_GIOT'],
                           }

            #conversione in stringa
            json_string = json.dumps(json_iotPlatform , ensure_ascii=False)
            #criptazione della json string
            json_string_cryptato = crypto.criptazione(json_string)

            #ritardo dell'invio successivo
            time.sleep(datiDA['TEMPO_INVIO'])

            #apertura del file iotdata.dbt in append
            with open ("../IOTp/iotdata.dbt", 'a', encoding='utf-8') as file:
                #scrittura dei dati ricevuti nel file iotdata.dbt
                file.write(json_string_cryptato + ', \n')

            #chiusura connessione
            conn.close()
        except KeyboardInterrupt as e:
            print("Numero di rilevazioni inviate: ", data_json['osservazione']['rilevazione'])
            break
    
