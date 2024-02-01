import socket
import threading
import sys
import json
import os


username = ""
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.startswith('file,'):
                _, file_name, file_size = message.split(",")
                file_size = int(file_size)
                
                file_data = b''
                while len(file_data) < file_size:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    file_data += chunk

                # Créer un répertoire 'fichiers' s'il n'existe pas
                if not os.path.exists('fichiers_de_'+f"{username}"):
                    os.makedirs('fichiers_de_'+f"{username}")

                # Créer un chemin unique en ajoutant un suffixe numérique si le fichier existe déjà
                base, extension = os.path.splitext(file_name)
                index = 1
                file_path = os.path.join('./fichiers_de_'+f"{username}", f"{base}_{index}{extension}")
                while os.path.exists(file_path):
                    index += 1
                    file_path = os.path.join('./fichiers_de_'+f"{username}", f"{base}_{index}{extension}")

                with open(file_path, 'wb') as file:
                    file.write(file_data)

                print(f"Fichier {file_name} reçu et enregistré dans le répertoire fichiers_de_+{username} avec le nom '{os.path.basename(file_path)}'.")
            else:
                print(message)
        except Exception as e:
            print(f"Erreur de réception des messages : {e}")
            break
 





def send_file(client_socket, file_path, recipient):
    file_name = file_path.split('/')[-1]
    
    # Envoi du nom du fichier et du destinataire
    data_to_send = json.dumps(["sendfile", file_name, recipient]).encode()
    client_socket.send(data_to_send)
    
    # Envoi de la taille du fichier
    file_size = os.path.getsize(file_path)
    client_socket.send(file_size.to_bytes(8, byteorder='big'))  # Utilisation de 8 octets pour la taille 

    # Envoi du contenu du fichier
    with open(file_path, 'rb') as file:
        while True:
            file_data = file.read(1024)  # Lecture par petits morceaux (1024 octets à la fois)
            if not file_data:
                break
            client_socket.sendall(file_data)


def send_message(client_socket, recipient):
    global username
    message = input(f"{username}: ")     
    command = ["2", recipient, message]
    client_socket.send(json.dumps(command).encode())

def change_username(client_socket):
    global username
    username = input("Entrez le nouveau nom d'utilisateur : ")
    command = ["3", "1", username]  # Commande pour changer de nom
    client_socket.send(json.dumps(command).encode())

def main_menu():
    print("1. Afficher utilisateurs en ligne")
    print("2. Envoyer un message à un utilisateur")
    print("3. Gérer profil")
    print("4. Gérer contacts")
    print("5. Envoyer un fichier à un utilisateur")
    print("0. Quitter")

def main():
    global username
    if len(sys.argv) < 3:
        print("USAGE: python client.py <IP> <Port>")
        return

    username = input("Entrez votre nom d'utilisateur : \n ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((sys.argv[1], int(sys.argv[2])))
    client.send(username.encode())

    # Créer un thread pour recevoir les messages
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    recipient = ""
    while True:
        try:
            main_menu()
            choice = input("Choix : ")

            if choice == "0":
                break
            elif choice == "2":
                while True:
                    if not recipient:
                        recipient = input("Entrez le nom d'utilisateur à qui envoyer le message : ")
                    send_message(client, recipient)
                    continue_option = input("Voulez-vous continuer à envoyer des messages? (o/n) : ").lower()
                    if continue_option != "o":
                        recipient = ""
                        break
            elif choice == "3":
                change_username(client)
    
            elif choice == "4":
                # Gestion des contacts non supportée pour le moment.
                print("Gestion des contacts non supportée pour le moment.")
            elif choice == "5":
                file_path = input("Chemin du fichier à envoyer: ")
                recipient = input("Nom d'utilisateur du destinataire: ")
                send_file(client, file_path, recipient)
            else:
                command = [choice]
                client.send(json.dumps(command).encode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message : {e}")
            break

    client.close()

if __name__ == "__main__":
    main()
