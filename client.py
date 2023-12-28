import socket
import threading
import sys
import json

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message)
        except Exception as e:
            print(f"Erreur de réception des messages : {e}")
            break

def main():
    if len(sys.argv) < 3:
        print("USAGE: python client.py <IP> <Port>")
        return

    username = input("Entrez votre nom d'utilisateur : ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((sys.argv[1], int(sys.argv[2])))
    client.send(username.encode())

    # Créer un thread pour recevoir les messages
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    while True:
        try:
            print("1. Afficher utilisateurs en ligne")
            print("2. Envoyer un message à un utilisateur")
            print("3. Gérer profil")
            print("4. Gérer contacts")
            print("0. Quitter")
            choice = input("Choix : ")

            if choice == "0":
                break

            if choice == "2":
                recipient = input("Entrez le nom d'utilisateur à qui envoyer le message : ")
                message = input("Entrez le message : ")
                command = [choice, recipient, message]
            else:
                command = [choice]

            client.send(json.dumps(command).encode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message : {e}")
            break

    client.close()

if __name__ == "__main__":
    main()
