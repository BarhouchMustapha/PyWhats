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

def display_submenu(menu_items):
    for key, value in menu_items.items():
        print(f"   {key}. {value}")
        
def menu():
    print("1. Afficher utilisateurs en ligne")
    print("2. Sélectionner utilisateur")
    print("3. Gérer profil")
    print("4. Gérer contacts")
    print("0. Quitter")
        
def main():
	
 
    if len(sys.argv) < 3:
        print("USAGE: python client.py <IP> <Port>") 
        print("EXAMPLE: python client.py localhost 8000")
        return


    username = input("Entrez votre nom d'utilisateur : ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((sys.argv[1], int(sys.argv[2])))
    client.send(username.encode())
    
    command = []
    # Créer un thread pour recevoir les messages
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    while True:
        menu()
        choice = str(input("Choix : "))
        command.append(choice)
        if command[0] == "1":
            client.send(json.dumps(command).encode())
            command.clear()
            response = client.recv(1024).decode()
            print(response)
        elif command[0] == "2":
            selected_user = input("Nom d'utilisateur à sélectionner : ")
            command.append(selected_user)
            client.send(json.dumps(command).encode())
            command.clear()
            # Il reste des manip à faire
            response = client.recv(1024).decode()
            print(response)
        elif command[0] == "3":
            display_submenu({"1": "Changer nom"})
            sub_choice = input("Choix : ")
            if sub_choice == "1":
                command.append("1")
                new_name = input("Nouveau nom : ")
                command.append(new_name)
                client.send(json.dumps(command).encode())
                command.clear()
                response = client.recv(1024).decode()
                print(response)
            else:
                print("Choix non reconnu.")
        elif command[0] == "4":
            display_submenu({"1": "Ajouter contact", "2": "Supprimer contact"})
            sub_choice = input("Choix : ")
            command.append(sub_choice)
            if sub_choice in ["1", "2"]:
                contact_name = input("Nom du contact : ")
                command.append(contact_name)
                client.send(json.dumps(command).encode())
                command.clear()
                response = client.recv(1024).decode()
                print(response)
            else:
                print("Choix non reconnu.")
        elif command[0] == "0":
            break
        else:
            print("Choix non reconnu.")


if __name__ == "__main__":
    main()
