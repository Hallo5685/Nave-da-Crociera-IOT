import random

# Simulazione sensore temperatura, da 10 a 40 gradi
def on_temperatura(N):
    TEMP = round(random.uniform(10,40), N)
    return TEMP
# Simulazione sensore umidità, da 20 a 90 gradi
def on_umidita(N):
    UMID = round(random.uniform(20,90), N)
    return UMID