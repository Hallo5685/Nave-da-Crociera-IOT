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
    
    PIN_SEGNALE = 0
    
    sensor = dht.DHT11(Pin(PIN_SEGNALE))      # Sensore celeste
    #sensor = dht.DHT22(Pin(N_PIN))     # Sensore bianco
    #
    try:
        sensor.measure()

        temperatura = sensor.temperature()
        umidita = sensor.humidity()
        temp = f"{temperatura:.{decimale}f}"
        hum  = f"{umidita:.{decimale}f}"
    
    except OSError as e:
        print('Problemi con il sensore...')
    
    TEMP = temp
    UMI  = hum
    return TEMP,UMI