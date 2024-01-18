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
            print("5. Envoyer un fihier à un utilisateur")
            print("0. Quitter")
            choice = input("Choix : ")

            if choice == "0":
                break

            if choice == "2":
                recipient = input("Entrez le nom d'utilisateur à qui envoyer le message : ")
                message = input("Entrez le message : ")
                command = [choice, recipient, message]
            elif choice == "3":
                new_name = input("Entrez le nouveau nom d'utilisateur : ")
                command = [choice, "1", new_name]  # Commande pour changer de nom
                client.send(json.dumps(command).encode())

            elif choice == "4":
                # Pour l'instant, affiche un message car la gestion des contacts n'est pas implémentée
                print("Gestion des contacts non supportée pour le moment.")
            elif choice == "5":
                file_path = input("Chemin du fichier à envoyer: ")
                recipient = input("Nom d'utilisateur du destinataire: ")
                send_file(client, file_path, recipient)
                continue
            else:
                command = [choice]

            client.send(json.dumps(command).encode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message : {e}")
            break

    client.close()
    ###############################################
def send_file(client_socket, file_path, recipient):
    file_name = file_path.split('/')[-1]
    client_socket.send(json.dumps(["sendfile", file_name, recipient]).encode())
    with open(file_path, 'rb') as file:
        file_data = file.read()
        client_socket.send(str(len(file_data)).encode())
        client_socket.send(file_data)

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.startswith('file '):
                _, file_name, file_size = message.split()
                file_size = int(file_size)
                file_data = b''
                while len(file_data) < file_size:
                    file_data += client_socket.recv(1024)
                with open(file_name, 'wb') as file:
                    file.write(file_data)
                print(f"Fichier {file_name} reçu.")
            else:
                print(message)
        except Exception as e:
            print(f"Erreur de réception des messages : {e}")
            break

if __name__ == "__main__":
    main()
