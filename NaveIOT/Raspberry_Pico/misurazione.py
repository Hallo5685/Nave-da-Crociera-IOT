# Gestione sensore temperatura e umidità
# DHT11 (celeste) o DHT22 (bianco)
# Raspberry Pico WH
# Utilizzo libreria dht
#
# Script: pico3.py
#
import time
from machine import Pin
import dht 
#
# Funzioni
#
def leggi_temp(decimale): 
    
    # definizione pin collegato al segnale del sensore
    PIN_SEGNALE = 0
    
    # inizializzazione sensore DHT11 collegato al pin scelto
    sensor = dht.DHT11(Pin(PIN_SEGNALE))
    
    # se si utilizza il DHT22 decommentare la riga sotto
    #sensor = dht.DHT22(Pin(N_PIN))
    
    try:
        # avvia la misurazione del sensore
        sensor.measure()

        # lettura temperatura e umidità
        temperatura = sensor.temperature()
        umidita = sensor.humidity()

        # formattazione dei valori con numero di decimali scelto
        temp = f"{temperatura:.{decimale}f}"
        hum  = f"{umidita:.{decimale}f}"
    
    except OSError as e:
        # errore di comunicazione con il sensore
        print('Problemi con il sensore...')
    
    # assegno i valori formattati a variabili di ritorno
    TEMP = temp
    UMI  = hum

    # ritorna temperatura e umidità come stringhe formattate
    return TEMP,UMI
