# Modulo di criptazione
# Script: cripto.py
# Simulazione con sostituzione di alcuni caratteri

def criptazione(payload):
    criptato = payload
    criptato = criptato.replace("a", "*")
    criptato = criptato.replace("e", "#")
    criptato = criptato.replace("i", "@")
    criptato = criptato.replace("o", "%")
    criptato = criptato.replace("u", "&")
    return criptato


def decriptazione(payload):
    decriptato = payload
    decriptato = decriptato.replace("*", "a")
    decriptato = decriptato.replace("#", "e")
    decriptato = decriptato.replace("@", "i")
    decriptato = decriptato.replace("%", "o")
    decriptato = decriptato.replace("&", "u")
    return decriptato