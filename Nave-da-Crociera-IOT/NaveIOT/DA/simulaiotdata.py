import json
import misurazione
import time

#definizione di variabili usate come costanti
cif_decimali = 2
num_cabine = 350
num_navi = 3
tempo_rilevazione = 1
inizio = True
estrazioni = 0

#funzione che apre un file json e ci salva umidità e temperatura dentro
def salva_json(umidita, temperatura):
    print("Funzione del salvataggio json non ancora attiva")


#controllo per verificare che questo script funzioni se eseguito come principale e NON come modulo importato
if __name__ == "__main__":
    #print("Questa è solo una prova (questo messaggio verrà rimosso non appena inizierà la scrittura del codice)") 
    
    #ciclo del programma che estrae e scrive i valori di temperature e umidità in base alle cabine della nave
    for estrazioni in range(num_cabine):

        temperatura = misurazione.on_temperatura(cif_decimali)
        umidita = misurazione.on_umidita(cif_decimali)
        #print(temperatura)
        #print(umidita,"\n")
        estrazioni = estrazioni+1
        time.sleep(tempo_rilevazione)

        #controllo per l'uscita dal ciclo di estrazione dei valori di temperatura e umidità
        if estrazioni == num_cabine:
            
            inizio = False
    print("Salvataggio dei dati sui file")