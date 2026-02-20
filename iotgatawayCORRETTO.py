import socket
import json
import time
import datetime
import crypto as crypto

if __name__ == "__main__":
    
    # Variabili per le medie
    temperat_media = 0
    umidita_media = 0

    # Lettura parametri.conf
    with open('parametri.conf', 'r') as file:
        datiDA = json.load(file)

    # Converte parametri.conf in bytes
    dati_bytes = json.dumps(datiDA).encode('utf-8')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((datiDA['IP_SERVER'], datiDA['PORTA_SERVER']))
    server.listen(5)

    print("Server in ascolto su", datiDA['IP_SERVER'], ":", datiDA['PORTA_SERVER'])

    while True:
        try:
            conn, addr = server.accept()
            print(f"Connessione da {addr}")

            # Invia parametri.conf al client
            conn.sendall(dati_bytes)

            # Ricezione dati dal client
            data_bites = conn.recv(4096)
            data_json = json.loads(data_bites.decode('utf-8'))

            print("Dati ricevuti dal client:", data_json)

            # Estrazione valori
            temperatura = data_json['osservazione']['temperatura']
            umidita = data_json['osservazione']['umidita']
            rilevazione = data_json['osservazione']['rilevazione']

            # Calcolo medie progressive
            temperat_media += temperatura
            umidita_media += umidita

            temperatura_media = round(temperat_media / rilevazione, datiDA['N_DECIMALI'])
            umidita_media_val = round(umidita_media / rilevazione, datiDA['N_DECIMALI'])

            # Costruzione JSON come nella foto
            json_iotPlatform = {
                "invionumero": rilevazione,
                "cabina": data_json['cabina'],
                "ponte": data_json['ponte'],
                "temperaturam": temperatura_media,
                "umiditam": umidita_media_val,
                "dataeora": datetime.datetime.now().timestamp(),
                "identita": datiDA['IDENTITA_GIOT'],
                "dc": datiDA['DC']  # Assicurati che esista in parametri.conf
            }

            # Conversione in stringa
            json_string = json.dumps(json_iotPlatform, ensure_ascii=False)

            # Criptazione
            json_string_cryptato = crypto.criptazione(json_string)

            # Ritardo invio successivo
            time.sleep(datiDA['TEMPO_INVIO'])

            # Salvataggio su file .dbt
            with open("../IOTp/iotdata.dbt", 'a', encoding='utf-8') as file:
                file.write(json_string_cryptato + ",\n")

            conn.close()

        except KeyboardInterrupt:
            print("Numero di rilevazioni inviate:", rilevazione)
            break
