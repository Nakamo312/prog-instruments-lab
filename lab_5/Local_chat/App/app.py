import hashlib
import os
import random
import socket
import string
import time
import art 

import multiprocessing 
from App.logger import ChatLogger
from App.client import Client
from App.server import Server


class Start():
    """
    The handles the initialization and execution of the chat application.
    It checks for available ports, prompts the user to choose between server and client modes,
    and manages the creation of server or client instances.
    """
    logger = ChatLogger().getLogger()
    characters = string.ascii_letters + string.digits
    @staticmethod
    def main_start():
        """
        Main method that starts the application.
        It searches for available ports, prompts the user for input, and creates either
        a server or client instance based on the user's choice.
        """
        # Search for open ports.
        '''20, 21, 22, 23, 25, 53, 67, 68, 80,
            110, 143, 443, 993, 995, 8080, 3306,
            5432, 6379, 27017, 5000, 8000,'''
        common_ports = [
             9000
        ]
        list_of_ports = []
        for i in common_ports:
            s = socket.socket()
            s.settimeout(1)
            try:
                s.connect(('127.0.0.1', i))
            except socket.error as error:
                print(f"Connection failed on port {i}: {error}")
            finally:
                s.close
                list_of_ports.append(i)
        os.system("cls")
        art.tprint("Anon    chat")

        command = str(input("Are you [S]erver or [C]lient?\n"))

        if command == "S":
            key_is_correct = False
            ip_adr = "localhost"
            nickname = None
            while not key_is_correct:
                os.system("cls")
                art.tprint("Anon    chat")
                key_prefix = "?"
                key_length = 6
                lett = [random.choice(Start.characters) for _ in range(key_length)]
                private_key = key_prefix + ''.join(lett)
                print(f"checking key {private_key} for unic.")
                time.sleep(0.75)
                os.system("cls")
                art.tprint("Anon    chat")
                print(f"checking key {private_key} for unic..")
                time.sleep(0.75)
                os.system("cls")
                art.tprint("Anon    chat")
                print(f"checking key {private_key} for unic...")
                time.sleep(0.75)
                
                hash_object = hashlib.sha256(
                    bytes(private_key.encode('utf-8')))
                hash_dig = hash_object.hexdigest()
                numbers = ''.join(i for i in hash_dig if not i.isalpha())
                port_for_key = int(sum(list(map(int, numbers))) ** 1.64)
                time.sleep(0.3)

                if port_for_key not in list_of_ports or port_for_key > 2000:
                    try:                        
                        os.system("cls")
                        art.tprint("Anon    chat")
                        print(f'''trying to create server
                               by private key {private_key}''')
                        server = Server(ip_adr, port_for_key,
                                        private_key, nickname)
                        server.run()                                                
                        key_is_correct = True
                    except ValueError as ve:
                        Start.logger.error(f"ValueError occurred: {ve}")
                        key_is_correct = False
                    except ConnectionError as ce:
                        Start.logger.error(f"ConnectionError occurred: {ce}")
                        key_is_correct = False
                    except Exception as e: 
                        Start.logger.error(f"An unexpected error occurred: {e}")
                        key_is_correct = False           

        elif command == "C":
            queue = multiprocessing.Queue()
            queue_send = multiprocessing.Queue()
            
            ip_adr = "localhost"

            private_key_for_client = input("Enter the key: ")
            
            hash_object = hashlib.sha256(
                bytes(private_key_for_client.encode('utf-8')))
            hash_dig = hash_object.hexdigest()
            numbers = ''.join(i for i in hash_dig if not i.isalpha())
            port_for_key = int(sum(list(map(int, numbers))) ** 1.64)
            time.sleep(0.3)

            if port_for_key not in list_of_ports or port_for_key < 2000:
                key_is_correct = True
                os.system("cls")
                art.tprint("Anon    chat")
                print(f"done! {private_key_for_client} is correct")
            nickname = input("Enter your nickname for chat (max len 16): ")

            client = Client(
                ip_adr, port_for_key, 
                private_key_for_client,
                nickname, queue, queue_send)

            is_connected = client.connect_to_server()

            if is_connected:                
                client.run()                                                
            else:
                print("Error while connecting to server")
                exit()
        else:
            print("wrong input, restarting software")
            Start.main_start()