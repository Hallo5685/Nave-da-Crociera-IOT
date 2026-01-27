import socket
import json

if __name__ == "__main__":
    
    #definizione costanti
    HOST = '127.0.0.1' 
    PORT = 9999

    # Apertura di parametri.conf in lettura
    with open('parametri.conf', 'r') as file:
        datiDA = json.load(file)

    # Trasformo stringa → bytes
    dati_bytes = json.dumps(datiDA).encode('utf-8')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print("Server in ascolto su 127.0.0.1:9999")

    while True:
        try:
            conn, addr = server.accept()
            print(f"Connessione da {addr}")

            conn.sendall(dati_bytes)
            readSocket = conn.recv(4096)
            # print(readSocket)
            conn.close()
        except KeyboardInterrupt as e:
            break

    