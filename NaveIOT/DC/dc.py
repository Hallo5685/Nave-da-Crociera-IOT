import json
import time
import datetime
from DC import misurazione

if __name__ == "__main__":

    # Apertura di parametri.conf in lettura
    with open('DA/parametri.conf', 'r') as file:
        dati = json.load(file)

    # variabili
    rilevazione = 1
    umiditaMedia = 0
    temperaturaMedia = 0

    # Ciclo di estrazione dei dati e di scrittura in file iotdata.dbt in formato JSON
    for estrazioni in range(dati['N_CABINE']):

        try:
        # Apertura di parametri.conf in scrittura
            json_file_dbt = open('IOTp/iotdata.dbt', 'a', encoding='utf-8')

            temperatura = misurazione.on_temperatura(dati['N_DECIMALI'])
            umidita = misurazione.on_umidita(dati['N_DECIMALI'])

            umiditaMedia += umidita
            temperaturaMedia += temperatura

            JSON = {
                "cabina": estrazioni + 1,
                "ponte": dati['N_PONTI'],
                "rilevazione": rilevazione,
                "dataeora": datetime.datetime.now().timestamp(),
                "temperatura": temperatura,
                "umidita": umidita
            }

            # stampa leggibile dei dati estrapolati
            print(json.dumps(JSON, indent=4))

            # salvataggio nel file iotdata.dbt
            json.dump(JSON, json_file_dbt)
            json_file_dbt.write(", \n")

            rilevazione += 1
            time.sleep(dati['TEMPO_RILEVAZIONE'])
            json_file_dbt.close()
        except KeyboardInterrupt as e:
            print("Interruzione del salvataggio dei dati")
            print("Rilevazioni effettuate: ", rilevazione)
            print("Media umidita: ", round(umiditaMedia/rilevazione, dati['N_DECIMALI']))
            print("Media temperatura: ", round(temperaturaMedia/rilevazione, dati['N_DECIMALI']))
            break

    print("Salvataggio dei dati sui file completato.")
