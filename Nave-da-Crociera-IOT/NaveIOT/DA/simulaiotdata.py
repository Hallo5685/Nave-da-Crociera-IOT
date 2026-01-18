import json
import misurazione
import time
import os

#funzione che apre un file json e ci salva umidità e temperatura dentro
def salva_json(umidita, temperatura):
    print("Funzione del salvataggio json non ancora attiva")


#controllo per verificare che questo script funzioni se eseguito come principale e NON come modulo importato
if __name__ == "__main__":

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'parametri.conf')
    with open(config_path, 'r') as file:
        dati = json.load(file)

    rilevazione = 0
    estrazioni = 0

    #ciclo del programma che estrae e scrive i valori di temperature e umidità in base alle cabine della nave
    for estrazioni in range(dati['N_CABINE']):
        dbt_dir = os.path.join(script_dir, '..', 'IOTp')
        dbt_path = os.path.join(dbt_dir, 'iotdata.dbt')
        json_file_dbt = open(dbt_path, 'a', encoding='utf-8')
        
        temperatura = misurazione.on_temperatura(dati['N_DECIMALI'])
        umidita = misurazione.on_umidita(dati['N_DECIMALI'])
        print(temperatura)
        print(umidita,"\n")
        
        #Aggiungere algoritmo per PONTE
        JSON = {"CABINA": estrazioni + 1,"PONTE": dati['N_PONTI'],"RILEVAZIONE": rilevazione,"TEMPERATURA": temperatura,"UMIDITA": umidita}
        
        json.dump(JSON, json_file_dbt)

        json_file_dbt.close()

        rilevazione = rilevazione+1
        estrazioni = estrazioni+1
        time.sleep(dati['TEMPO_RILEVAZIONE'])

        #controllo per l'uscita dal ciclo di estrazione dei valori di temperatura e umidità
        if estrazioni == dati['N_CABINE']:
            
            inizio = False
    print("Salvataggio dei dati sui file")