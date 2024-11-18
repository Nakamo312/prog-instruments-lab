import hashlib
import json
import os
import random
import re
import socket
import string
import time
import threading
import art 

import logging, logging.config
import multiprocessing 
import tkinter as tk


characters = string.ascii_letters + string.digits

class RegexProcessor:
    def __init__(self):
        self.masked = True
        self.patterns = [
          (r"https?:\/\/\S+", "URL"),
          (r"\+?\d{1,3}?[-.\s]?(?\d{3})?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}", "Phone")
        ]
        self.logger = ChatLogger().getLogger(self.__class__.__name__)
    
    def regex_processing(self, message:str) -> str:
        for pattern, name in self.patterns:
            matches = re.findall(pattern, message)
            for m in matches:
                self.logger.info("CATCH: %s"\
                                 " | %s" %(name, m))           
            message = re.sub(pattern, "*", message)
        return message


class ChatLogger:
    """
    A class for managing chat logging based on a JSON configuration file.

    Initializes a logger from a configuration file and provides methods for obtaining loggers 
    with different names in the logger hierarchy.
    """

    def __init__(self):
        with open(os.path.join(os.getcwd(),"server_logging.json"),
                  mode='r', encoding='utf-8') as config:
            data = json.load(config)
            logging.config.dictConfig(data)
            self.logger = logging.getLogger('App')

    def getLogger(self, name:str = None) -> logging.Logger:
        """
        Returns a logger with the specified name in the logger hierarchy.    
        Args:
          name (str, optional): The name of the logger. If None, the root logger 'App' is returned. Defaults to None.

        Returns:
          logging.Logger: An instance of the logger.
        """
        return logging.getLogger('App.' + name if name else '')


class Server():
    """
    This class represents the chat server. 
    Handles client connections, broadcasts messages, and manages nicknames.
    """

    def __init__(self, ip_adr, port, key, nickname): 
        """
        Args:
          ip_adr (str): The IP address of the server.
          port (int): The port number of the server.
          key (str): The private key used to identify the server.
          nickname (str): The nickname of the server.
        """       
        self.ip_adr = ip_adr
        self.port = port
        self.key = key
        self.nickname = nickname
        self.socket = None
        self.socket_conn = None
        self.conn_addr = None
        self.clients = []
        self.nicknames = []

        self.regex_processor = RegexProcessor()
        self.logger = ChatLogger().getLogger(self.__class__.__name__)

    def handle_client(self, client: socket):
        """
        Handles a single client connection.
        Continuously receives messages from the client
        and broadcasts them to all other connected clients.

        Args:
            client (socket): The socket object representing the client connection.
        """
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except (ConnectionResetError, OSError) as error:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                msg = f'{nickname} has left the chat room!'.encode('utf-8')
                self.logger.info("USER_REMOVED: %s"\
                                 "has left the chat room!" %nickname)
                self.broadcast(msg)
                self.nicknames.remove(nickname)
                break 
            except Exception as ex:
                self.logger.error("An unexpected error occurred: %s" %ex)


    def broadcast(self, message:bytes):
        """
        Broadcasts a message to all connected clients.
            Args:
                message (bytes): The message to broadcast.
        """
        msg = message.replace(b"\x00", b"").decode('utf-8')
        if msg:
            msg = self.regex_processor.regex_processing(msg)
            for client in self.clients:
                client.send(msg)

    def run(self):
        """
        Starts the server and listens for incoming client connections.
        Creates a socket, binds it to the specified IP address and port,
        and listens for incoming connections.
        For each incoming connection, it creates
        a new thread to handle the client.
        """
        self.socket = socket.socket()
        self.socket.bind((self.ip_adr, self.port))
        self.socket.listen()
        port = self.port
        self.logger.info("AСTION: Server is running and "\
                         "listening on port %s" %port)
        while True:  
            self.socket_conn, self.conn_addr = self.socket.accept()
            ip, port = self.conn_addr
            self.logger.info("ACTION: connection is established "\
                             "with %s:%d" %(ip, port))

            recieved_msg = self.socket_conn.recv(128)
            recieved_line = recieved_msg.decode('utf-8')

            nickname = recieved_line[-16::]
            nickname = nickname.replace("\x00", "")

            if nickname not in self.nicknames:
                self.nicknames.append(nickname)
            
            if self.socket_conn not in self.clients:
                self.clients.append(self.socket_conn)

            nickname_for_send = nickname.replace("\x00", "")
            nick = nickname_for_send.encode('utf-8')
            self.broadcast(("\xaa %s has connected to chat" % nickname_for_send).encode('utf-8'))
            self.logger.info("USER_ADDED: %s "\
                             "has connected to chat"
                              %nick.decode('utf-8'))
            thread = threading.Thread(target=self.handle_client,
                                      args=(self.socket_conn,))
            thread.start()        

    def close_conn(self):
        """Closes the server's socket and connection address."""
        self.socket_conn.close()
        self.socket.close()
        self.logger.info("AСTION: closing the server connection")
        self.conn_addr = None


class Client():
    """
    This class represents the chat client. 
    Handles connection to the server, sending
    and receiving messages, and GUI updates.
    """

    def __init__(self, ip_adr, port, key, nickname, queue, queue_send):
        """
            Args:
                ip_adr (str): The IP address of the server to connect to.
                port (int): The port number of the server.
                key (str): The private key used for authentication.
                nickname (str): The nickname of the client (user).
                queue (multiprocessing.Queue): Queue for incoming
                messages from the server.
                queue_send (multiprocessing.Queue): Queue for outgoing messages
                to be sent to the server.
        """
        self.ip_adr = ip_adr
        self.port = port 
        self.key = key
        self.nickname = nickname
        self.socket = None
        self.root = None
        self.label1 = None
        self.button1 = None
        self.scrollbar = None
        self.text_output = None
        self.full_recieved_msg = ''
        self.queue = queue
        self.queue_send = queue_send
        self.logger = ChatLogger().getLogger(self.__class__.__name__)

    def connect_to_server(self):
        """
        Attempts to connect to the specified server.
        This method creates a socket connection to the
        server using the provided IP address and port.
        It retries the connection up to five times in case of failure.
        Returns:
            bool: Returns True if the connection was successful,
            False if the connection failed after five attempts.
        """
        self.socket = socket.socket()
        count_of_connection = 0
        while True:
            try:
                self.socket.connect((self.ip_adr, self.port))
                break
            except socket.error as error:
                self.logger.warning("Error while connecting to server %s" %error)
                count_of_connection += 1
                if count_of_connection > 4:
                    self.logger.warning("You try it for 5+ times"\
                                        "we gonna close your connection")
                    self.socket.close()
                    return False
                time.sleep(1)
        list_for_join = []
        nickname_enc = self.nickname.encode('utf-8')
        need_bytes_of_zero = 16 - len(nickname_enc)

        list_for_join.append(b'\x00'*need_bytes_of_zero)
        list_for_join.append(nickname_enc)

        msg_to_send = b''.join(list_for_join)

        try:
            self.socket.send(msg_to_send)
        except socket.error as error:
            self.logger.error("Sorry, we can't send your message")
        return True
    
    def send_msg(self):
        """Sends messages from the queue to the server."""
        while True:
            if not self.queue_send.empty():
                kboard_input = self.queue_send.get()
                list_for_join = []

                message_enc = kboard_input.encode("utf-8")

                nickname_enc = self.nickname.encode('utf-8')
                need_bytes_of_zero = 16 - len(nickname_enc)

                list_for_join.append(message_enc)
                list_for_join.append(b'\x00' * need_bytes_of_zero)
                list_for_join.append(nickname_enc)

                msg_to_send = b''.join(list_for_join)
                self.logger.info("ALL_SEND: %s: %s" %(kboard_input, self.nickname))
                try:
                    self.socket.send(msg_to_send)
                except socket.error as error:
                    self.logger.warning("Sorry, we can't send your message \t %s" %error)

    def receive_msg(self):
        """
        Receives messages from the server
        and puts them into the queue.
        """
        while True:
            recieved_msg = self.socket.recv(128)
            
            if recieved_msg[0] == 194:
                recieved_line = recieved_msg.decode("utf-8")
            else:
                recieved_line = recieved_msg.decode("utf-8")
                nickname = recieved_line[-16::].replace("\x00", "")                

                if nickname != self.nickname.replace("\x00", ""):
                    message = recieved_line[0:-16]
                    self.full_recieved_msg = f"{nickname}: {message}"
                    self.queue.put(self.full_recieved_msg)    

    def add_lines(self):
        """
        Adds received messages
        from the queue to the text output.
        """
        try:         
            if not self.queue.empty():
                recieved_msg_from_queue = self.queue.get()
                kastil = "".join(map(
                    str, list(recieved_msg_from_queue))).replace('\x00', '')

                self.text_output.insert("end", kastil + "\n") 
                self.text_output.see("end")  
            self.root.after(100, self.add_lines)  
        except Exception as ex:
            self.logger.error("An unexpected error occurred: %s" %ex)
    
    def send_msg_button(self):
        """
        Handles sending a message when
        the send button is pressed.
        """
        msg_for_send = self.entry1.get()
        self.queue.put(f'{self.nickname} : {msg_for_send}')
        self.queue_send.put(msg_for_send)
        self.entry1.delete(0, 'end')

    def run_gui(self):
        """Initialize and runs the GUI in mainloop."""
        self.root= tk.Tk()

        self.label1 = tk.Label(self.root, text='Anon chat')
        self.label1.config(font=('helvetica', 14))
        self.label1.place(x=220, y=15)

        self.entry1 = tk.Entry(self.root) 
        self.entry1.place(x=15, y=400, width=450, height=50)

        self.button1 = tk.Button(self.root, text='send',
                                 command=self.send_msg_button)
        self.button1.place(x=400, y=450)

        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side="right", fill="none", expand=True)
        self.text_output = tk.Text(self.root, 
                                   yscrollcommand=self.scrollbar.set)
        self.text_output.place(x=15, y=50, width=450, height=300)
        self.scrollbar.config(command=self.text_output.yview)

        self.root.minsize(500, 500)
        self.root.maxsize(500, 500)

        self.root.after(0, self.add_lines)
        self.root.mainloop()

    def run(self):
        """
        Runs the client, starting threads for GUI,
        sending, and receiving messages.
        """                              
        GUITread = multiprocessing.Process(target=self.run_gui)
        send_thread = threading.Thread(target=self.send_msg)
        receive_thread = threading.Thread(target=self.receive_msg)

        GUITread.start()
        send_thread.start()
        receive_thread.start()       

        send_thread.join()
        receive_thread.join()                        

    def close_conn(self):
        """Closes the client's socket connection."""
        self.socket.close()


class Start():
    """
    The handles the initialization and execution of the chat application.
    It checks for available ports, prompts the user to choose between server and client modes,
    and manages the creation of server or client instances.
    """
    logger = ChatLogger().getLogger()
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
                lett = [random.choice(characters) for _ in range(key_length)]
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


if __name__ == "__main__":  
    #TODO:
    #  1. check users by ip
    #  2. create ports for chat by some hash func  
    Start.main_start()    
