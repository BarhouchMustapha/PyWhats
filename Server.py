import socket
import threading
import sys
import json




# Dictionnaire pour stocker les utilisateurs en ligne
online_users = {}
lock = threading.Lock()

def Pywhats(client_socket, username):
    command = []
    while True:
        try:
            command = json.loads(client_socket.recv(1024).decode())
            if not command:
                break

            # Analyser la commande reçue du client
            
            if command[0] == '1':
                # Afficher utilisateurs en ligne
                response = "Utilisateurs en ligne : {}".format(", ".join(online_users.keys()))
                client_socket.send(response.encode())
            elif command[0] == "2":
                # Sélectionner utilisateur
                selected_user = command[1]
                selected_socket = [sock for user, sock in online_users.items() if user == selected_user]
                if selected_socket:
                    client_socket.send("Utilisateur sélectionné. Vous pouvez maintenant envoyer des messages ou des fichiers.".encode())
                    # Gérer la communication avec l'utilisateur sélectionné
                    # ...
                else:
                    client_socket.send("Utilisateur non trouvé.".encode())
            elif command[0] == "3":
                
                # Gérer le profil
                if command[1] == "1":
                    
                    # Changer le nom
                    new_name = command[2]
                    lock.acquire()
                    online_users[username] = new_name
                    lock.release()
                    client_socket.send("Nom changé avec succès.".encode())
                else:
                    client_socket.send("Commande non reconnue.".encode())
            elif command[0] == "4":
                
                # Gérer les contacts
                if command[1] == "1":
                    # Ajouter un contact
                    
                    contact_name = command[2]
                    lock.acquire()
                    online_users[contact_name] = None  # Ajouter le contact sans socket
                    lock.release()
                    client_socket.send("Contact ajouté avec succès.".encode())
                elif command[1] == "2":
                   
                    # Supprimer un contact
                    contact_name = command[2]
                    lock.acquire()
                    del online_users[contact_name]
                    lock.release()
                    client_socket.send("Contact supprimé avec succès.".encode())
                else:
                    client_socket.send("Commande non reconnue.".encode())
            else:
                client_socket.send("Commande non reconnue.".encode())

        except Exception as e:
            print(f"Erreur de traitement du client {username}: {e}")
            break

    # Fermer la connexion client
    lock.acquire()
    del online_users[username]
    lock.release()
    client_socket.close()



def main(): 
    if len(sys.argv) < 3: 
        print("EXAMPLE d'utilisation: python server.py localhost 8000")
        return

    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Server.bind((sys.argv[1], int(sys.argv[2])))
    Server.listen(10)
    print("Démarrage de PyWhats server")
 
    while True:
        client, _ = Server.accept()
        username = client.recv(1024).decode("utf-8")
        print(f"Nouvelle connexion de {username}")
        
        lock.acquire()
        online_users[username] = client
        lock.release()

        # Créer un thread pour gérer le client
        client_thread = threading.Thread(target=Pywhats, args=(client, username))
        client_thread.start()
             


if __name__ == "__main__":
    main()