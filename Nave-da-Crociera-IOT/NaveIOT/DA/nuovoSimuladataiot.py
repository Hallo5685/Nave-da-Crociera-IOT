import json
import misurazione
import time

# funzione che apre un file json e ci salva umidità e temperatura dentro
def salva_json(umidita, temperatura):
    print("Funzione del salvataggio json non ancora attiva")


if __name__ == "__main__":

    # parametri.conf si trova nella stessa cartella dello script
    with open('parametri.conf', 'r') as file:
        dati = json.load(file)

    rilevazione = 0

    for estrazioni in range(dati['N_CABINE']):

        # Percorso relativo: esci da DA → entra in IOTp → apri iotdata.dbt
        dbt_path = '../IOTp/iotdata.dbt'

        # apertura del file in append
        json_file_dbt = open(dbt_path, 'a', encoding='utf-8')

        temperatura = misurazione.on_temperatura(dati['N_DECIMALI'])
        umidita = misurazione.on_umidita(dati['N_DECIMALI'])

        print("Temperatura:", temperatura)
        print("Umidità:", umidita, "\n")

        JSON = {
            "cabina": estrazioni + 1,
            "ponte": dati['N_PONTI'],
            "rilevazione": rilevazione,
            "dataeora": time.time(),
            "temperatura": temperatura,
            "umidita": umidita
        }

        # stampa leggibile
        print(json.dumps(JSON, indent=4))

        # salvataggio nel file
        json.dump(JSON, json_file_dbt)
        json_file_dbt.write("\n\n")

        rilevazione += 1
        time.sleep(dati['TEMPO_RILEVAZIONE'])
        json_file_dbt.closed()

    print("Salvataggio dei dati sui file completato.")
