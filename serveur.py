import socket
import threading
import sys
import json

# Dictionnaire pour stocker les utilisateurs en ligne
online_users = {}
lock = threading.Lock()

def pywhats(client_socket, username):
    while True:
        try:
            command = json.loads(client_socket.recv(1024).decode())
            if not command:
                break

            # Analyser la commande reçue du client
            if command[0] == '1':
                # Afficher utilisateurs en ligne
                with lock:
                    response = "Utilisateurs en ligne : {}".format(", ".join(online_users.keys()))
                client_socket.send(response.encode())
            elif command[0] == "2":
                # Sélectionner utilisateur et envoyer un message
                selected_user = command[1]
                message = command[2]  # Supposons que le message est le troisième élément de la commande
                with lock:
                    selected_socket = online_users.get(selected_user)
                if selected_socket:
                    try:
                        selected_socket.send(f"{username} says: {message}".encode())
                        client_socket.send("Message envoyé avec succès.".encode())
                    except:
                        client_socket.send("Échec de l'envoi du message.".encode())
                else:
                    client_socket.send("Utilisateur non trouvé.".encode())
            elif command[0] == "3":
                # Gérer le profil (Supposons qu'on veut juste signaler un changement, pas le stocker)
                #client_socket.send("Changement de profil non supporté pour le moment.".encode())
                if command[1] == "1":
                    # Changer le nom
                    new_name = command[2]
                    with lock:
                        # Assurez-vous que le nouveau nom n'est pas déjà pris
                        if new_name not in online_users:
                            del online_users[username]  # Supprimer l'ancien nom
                            online_users[new_name] = client_socket  # Ajouter avec le nouveau nom
                            username = new_name  # Mettre à jour le nom d'utilisateur dans la session courante
                            client_socket.send("Nom changé avec succès.".encode())
                        else:
                            client_socket.send("Le nom est déjà pris.".encode())

            # Ajout d'une fonctionnalité pour la gestion des contacts
            elif command[0] == "4":
                # Gérer les contacts (Supposons qu'on veut juste signaler un changement, pas le stocker)
                client_socket.send("Gestion des contacts non supportée pour le moment.".encode())
            elif command[0] == "sendfile": #################
                file_name = command[1]
                recipient = command[2]
                file_size = int(client_socket.recv(1024).decode().strip())
                file_data = b''
                while len(file_data) < file_size:
                    file_data += client_socket.recv(1024)
                if recipient in online_users:
                    online_users[recipient].send(f"file {file_name} {len(file_data)}".encode() + file_data)

            else:
                client_socket.send("Commande non reconnue.".encode())

        except Exception as e:
            print(f"Erreur de traitement du client {username}: {e}")
            break

    # Fermer la connexion client
    with lock:
        if username in online_users:  # vérifier si l'utilisateur est toujours dans le dictionnaire
            del online_users[username]
    client_socket.close()

def main():
    if len(sys.argv) < 3:
        print("USAGE: python server.py <IP> <Port>")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((sys.argv[1], int(sys.argv[2])))
    server.listen(10)
    print("Démarrage de PyWhats server")

    while True:
        client, _ = server.accept()
        username = client.recv(1024).decode("utf-8")
        print(f"Nouvelle connexion de {username}")

        with lock:
            online_users[username] = client

        # Créer un thread pour gérer le client
        client_thread = threading.Thread(target=pywhats, args=(client, username))
        client_thread.start()

if __name__ == "__main__":
    main()
