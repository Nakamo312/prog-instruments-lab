import socket
import threading
import time

from App.logger import ChatLogger


class Client:
    """
    This class represents the chat client. 
    Handles connection to the server, sending
    and receiving messages.
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
        self.queue = queue

        self.queue_send = queue_send
        self.logger = ChatLogger().getLogger(self.__class__.__name__)

    def connect_to_server(self):
        """Attempts to connect to the specified server."""
        self.socket = socket.socket()
        count_of_connection = 0
        while True:
            try:
                self.socket.connect((self.ip_adr, self.port))
                break
            except socket.error as error:
                self.logger.warning("Error while connecting to server %s" % error)
                count_of_connection += 1
                if count_of_connection > 4:
                    self.logger.warning("You tried 5+ times. Closing connection.")
                    self.socket.close()
                    return False
                time.sleep(1)
        
        nickname_enc = self.nickname.encode('utf-8')
        need_bytes_of_zero = 16 - len(nickname_enc)
        msg_to_send = b'\x00' * need_bytes_of_zero + nickname_enc
        
        try:
            self.socket.send(msg_to_send)
        except socket.error as error:
            self.logger.error("Sorry, we can't send your message.")
        return True

    def send_msg(self, exit_after_one=False):
        """Sends messages from the queue to the server."""
        while True:
            if not self.queue_send.empty():
                kboard_input = self.queue_send.get()
                message_enc = kboard_input.encode("utf-8")
                nickname_enc = self.nickname.encode('utf-8')
                need_bytes_of_zero = 16 - len(nickname_enc)
                msg_to_send = message_enc + b'\x00' * need_bytes_of_zero + nickname_enc
                
                self.logger.info("ALL_SEND: %s: %s" % (self.nickname, kboard_input))
                try:
                    self.socket.send(msg_to_send)
                except socket.error as error:
                    self.logger.warning("Sorry, we can't send your message: %s" % error)
            if exit_after_one:
                break

    def receive_msg(self):
        """Receives messages from the server and puts them into the queue."""
        while True:
            recieved_msg = self.socket.recv(128)
            if recieved_msg:
                recieved_line = recieved_msg.decode("utf-8")
                nickname = recieved_line[-16:].replace("\x00", "")
                if nickname != self.nickname.replace("\x00", ""):
                    message = recieved_line[:-16]
                    full_message = f"{nickname}: {message}"
                    self.queue.put(full_message)
            else:
                break

    def run(self):
        """Runs the client, starting threads for sending and receiving messages."""
        send_thread = threading.Thread(target=self.send_msg)
        receive_thread = threading.Thread(target=self.receive_msg)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

    def close_conn(self):
        """Closes the client's socket connection."""
        self.socket.close()
