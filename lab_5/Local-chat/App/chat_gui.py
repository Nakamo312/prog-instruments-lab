import tkinter as tk

class ChatGUI:
    """
    This class handles the graphical user interface (GUI) for the chat application.
    It interacts with the message queue and sends messages from the input field.
    """

    def __init__(self, nickname, queue, queue_send):
        """
        Args:
            nickname (str): The nickname of the user.
            queue (multiprocessing.Queue): Queue for incoming messages.
            queue_send (multiprocessing.Queue): Queue for outgoing messages.
        """
        self.nickname = nickname
        self.queue = queue
        self.queue_send = queue_send
        self.root = None
        self.label1 = None
        self.button1 = None
        self.entry1 = None
        self.scrollbar = None
        self.text_output = None

    def add_lines(self):
        """Adds received messages from the queue to the text output."""
        try:         
            if not self.queue.empty():
                recieved_msg_from_queue = self.queue.get()
                formatted_msg = "".join(map(str, list(recieved_msg_from_queue))).replace('\x00', '')
                self.text_output.insert("end", formatted_msg + "\n")
                self.text_output.see("end")
            self.root.after(100, self.add_lines)
        except Exception as ex:
            print(f"Error in adding lines: {ex}")

    def send_msg_button(self):
        """Handles sending a message when the send button is pressed."""
        msg_for_send = self.entry1.get()
        self.queue.put(f'{self.nickname} : {msg_for_send}')
        self.queue_send.put(msg_for_send)
        self.entry1.delete(0, 'end')

    def run_gui(self):
        """Initialize and run the GUI in mainloop."""
        self.root = tk.Tk()
        self.label1 = tk.Label(self.root, text='Anon chat')
        self.label1.config(font=('helvetica', 14))
        self.label1.place(x=220, y=15)

        self.entry1 = tk.Entry(self.root)
        self.entry1.place(x=15, y=400, width=450, height=50)

        self.button1 = tk.Button(self.root, text='Send', command=self.send_msg_button)
        self.button1.place(x=400, y=450)

        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side="right", fill="none", expand=True)

        self.text_output = tk.Text(self.root, yscrollcommand=self.scrollbar.set)
        self.text_output.place(x=15, y=50, width=450, height=300)
        self.scrollbar.config(command=self.text_output.yview)

        self.root.minsize(500, 500)
        self.root.maxsize(500, 500)

        self.root.after(0, self.add_lines)
        self.root.mainloop()

