# Questo file riceve i dati criptati inviati da iotgwda.py, li decripta e li salva in iotp/dbplatform.json (decriptato).
#LE TRE COSTANTI PATH, PORT e HOST SONO DEFINITE IN QUESTO FILE, NON IN IOTGWDA.PY quindi in futuro andranno lette da un altro file
import os
import socket
import json
import crypto as crypto

DBPLATFORM_PATH = "iotp/dbplatform.json"
ARCHIVIA_HOST = "0.0.0.0"
ARCHIVIA_PORT = 9091

if __name__ == "__main__":
    # Viene creata la cartella iotp se non esiste
    os.makedirs("iotp", exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((ARCHIVIA_HOST, ARCHIVIA_PORT))
        server_socket.listen(5)

        print(f"Archivia in ascolto su {ARCHIVIA_HOST}:{ARCHIVIA_PORT}")
        print(f"I dati decriptati saranno salvati in {DBPLATFORM_PATH}")

        # Loop principale per accettare connessioni e processare dati
        while True:
            try:
                conn, addr = server_socket.accept()
                with conn:
                    print(f"Connessione da {addr}")
                    dati_criptati = conn.recv(65536).decode('utf-8').strip()

                    if not dati_criptati:
                        conn.sendall(b"Nessun dato ricevuto")
                        continue

                    try:
                        dati_decriptati = crypto.decriptazione(dati_criptati)
                        payload = json.loads(dati_decriptati)
                    except Exception as err:
                        error_msg = f"Errore decriptazione/parse JSON: {err}"
                        print(error_msg)
                        conn.sendall(error_msg.encode('utf-8'))
                        continue

                    with open(DBPLATFORM_PATH, "a", encoding="utf-8") as f:
                        f.write(json.dumps(payload, ensure_ascii=False))
                        f.write("\n")

                    print("Dati decriptati salvati in dbplatform.json:", payload)
                    conn.sendall(b"OK")

            except KeyboardInterrupt:
                print("Archivia interrotta manualmente")
                break
            except Exception as err:
                print(f"Errore in archivia: {err}")
                continue

