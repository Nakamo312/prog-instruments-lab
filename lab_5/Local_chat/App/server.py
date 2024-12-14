import socket
import threading

from App.logger import ChatLogger
from App.regex_processor import RegexProcessor

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
        if message[0] == 194:
            msg = message.replace(b"\x00", b"").decode("utf-8")
            if msg:
                for client in self.clients:
                    client.send(message)
        else:
            recieved_line = message
            nickname = recieved_line[-16::]              
            message = recieved_line[0:-16]
            if message:
                message = message.decode('utf-8')
                message = self.regex_processor.regex_processing(message)
                message = message.encode('utf-8')
                full_msg = message + nickname
                for client in self.clients:
                    client.send(full_msg)

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