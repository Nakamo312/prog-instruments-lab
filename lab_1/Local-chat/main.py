import hashlib
import os
import random
import socket
import string
import time
import _thread 
import tkinter as tk

import multiprocessing
import art


characters = string.ascii_letters + string.digits


class Server():
    """
    This class represents the chat server. 
    Handles client connections, broadcasts messages, and manages nicknames.
    """

    def __init__(self, ip_adr:str, port:int, key:str, nickname:str): 
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

    def handle_client(self, client: socket) -> None:
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
                self.broadcast(msg)
                self.nicknames.remove(nickname)
                break 
            except Exception as ex:
                print(f"An unexpected error occurred: {ex}")

    def broadcast(self, message: bytes) -> None:
        """
        Broadcasts a message to all connected clients.
            Args:
                message (bytes): The message to broadcast.
        """
        for client in self.clients:
            print(message)
            client.send(message)

    def run(self) -> None:
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
        print(f'''Server is running and listening on port
               {self.port} by private key {self.key}...''')
        while True:
            print(self.clients, self.nickname)
            self.socket_conn, 
            self.conn_addr = self.socket.accept()
            print(f'''connection is established with
                   {str(self.conn_addr)}''')

            recieved_msg = self.socket_conn.recv(128)
            recieved_line = recieved_msg.decode('utf-8')

            nickname = recieved_line[-16::]
            nickname.replace("\x00", "")

            if nickname not in self.nicknames:
                self.nicknames.append(nickname)
            
            if self.socket_conn not in self.clients:
                self.clients.append(self.socket_conn)

            nickname_for_send = nickname.replace("\x00", "")

            self.broadcast(f'''\xaa{nickname_for_send}
                            has connected to chat'''.encode('utf-8'))
            
            thread = _thread.threading.Thread(target=self.handle_client,
                                      args=(self.socket_conn,))
            thread.start()        

    def close_conn(self) -> None:
        """Closes the server's socket and connection address."""
        self.socket_conn.close()
        self.socket.close()
        self.conn_addr = None


class Client():
    """
    This class represents the chat client. 
    Handles connection to the server, sending
    and receiving messages, and GUI updates.
    """

    def __init__(self, ip_adr:str, port:int, key:str,
                 nickname:str, queue:multiprocessing.Queue,
                 queue_send:multiprocessing.Queue):
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

    def connect_to_server(self) -> None:
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
                print("Error while connecting to server")
                print(error)
                count_of_connection += 1
                if count_of_connection > 4:
                    print('''You try it for 5+ times, we gonna close
                           your connection''')
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
            print("Sorry, we can't send your message")
            print(error)
        return True
    
    def send_msg(self) -> None:
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

                try:
                    self.socket.send(msg_to_send)
                except socket.error as error:
                    print("Sorry, we can't send your message")
                    print(error)

    def receive_msg(self) -> None:
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

    def add_lines(self) -> None:
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
            print(f"An unexpected error occurred: {ex}")
    
    def send_msg_button(self) -> None:
        """
        Handles sending a message when
        the send button is pressed.
        """
        msg_for_send = self.entry1.get()
        self.queue.put(f'{self.nickname} : {msg_for_send}')
        self.queue_send.put(msg_for_send)
        self.entry1.delete(0, 'end')

    def run_gui(self) -> None:
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

    def run(self) -> None:
        """
        Runs the client, starting threads for GUI,
        sending, and receiving messages.
        """                              
        GUITread = multiprocessing.Process(target=self.run_gui)
        send_thread = _thread.threading.Thread(target=self.send_msg)
        receive_thread = _thread.threading.Thread(target=self.receive_msg)

        GUITread.start()
        send_thread.start()
        receive_thread.start()       

        send_thread.join()
        receive_thread.join()                        

    def close_conn(self) -> None:
        """Closes the client's socket connection."""
        self.socket.close()


class Start():
    """
    The handles the initialization and execution of the chat application.
    It checks for available ports, prompts the user to choose between server and client modes,
    and manages the creation of server or client instances.
    """

    @staticmethod
    def main_start() -> None:
        """
        Main method that starts the application.
        It searches for available ports, prompts the user for input, and creates either
        a server or client instance based on the user's choice.
        """
        # Search for open ports.
        list_of_ports = []
        for i in range(65536):
            s = socket.socket()
            s.settimeout(1)
            try:
                s.connect(('127.0.0.1', i))
            except socket.error as error:
                print(f"Connection failed on port {i}: {error}")
            finally:
                s.close
                list_of_ports.append(i)
        os.system("clear")
        art.tprint("Anon    chat")

        command = str(input("Are you [S]erver or [C]lient?\n"))

        if command == "S":
            key_is_correct = False
            ip_adr = "localhost"
            nickname = None
            while not key_is_correct:
                os.system("clear")
                art.tprint("Anon    chat")
                key_prefix = "?"
                key_length = 6
                lett = [random.choice(characters) for _ in range(key_length)]
                private_key = key_prefix + ''.join(lett)
                print(f"checking key {private_key} for unic.")
                time.sleep(0.75)
                os.system("clear")
                art.tprint("Anon    chat")
                print(f"checking key {private_key} for unic..")
                time.sleep(0.75)
                os.system("clear")
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
                        os.system("clear")
                        art.tprint("Anon    chat")
                        print(f'''trying to create server
                               by private key {private_key}''')
                        server = Server(ip_adr, port_for_key,
                                        private_key, nickname)
                        server.run()                                                
                        key_is_correct = True
                    except ValueError as ve:
                        print(f"ValueError occurred: {ve}")
                        key_is_correct = False
                    except ConnectionError as ce:
                        print(f"ConnectionError occurred: {ce}")
                        key_is_correct = False
                    except Exception as e: 
                        print(f"An unexpected error occurred: {e}")
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
                os.system("clear")
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
