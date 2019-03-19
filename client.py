from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from tkinter import messagebox
import os
from functools import partial



def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg = msg.split(":")
            if len(msg) == 1:
            	msg_list.insert(tkinter.END, msg[0] + "\n", "TAG_INFO")
            else:
            	msg_list.insert(tkinter.END, msg[0] + ": ", "TAG_NAME")
            	for i in msg[1:-1]:
            		if i in emojis:
            			msg_list.delete(tkinter.END + "-2c", tkinter.END)
            			msg_list.image_create(tkinter.END, image = emojis[i])
            		else:
            			msg_list.insert(tkinter.END, i, "TAG_MESSAGE")
            			msg_list.insert(tkinter.END, ":", "TAG_MESSAGE")

            	msg_list.insert(tkinter.END, msg[-1] + "\n", "TAG_MESSAGE")
        except OSError:
            break


def send(event=None):
    """Handles sending of messages."""
    if client_socket is None:
    	root.destroy()
    	return
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.

    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        root.quit()
        exit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

def setup_ui():


	root = tkinter.Tk()
	root.title("Chatter")

	messages_frame = tkinter.Frame(root)
	my_msg = tkinter.StringVar()
	my_msg.set("Type your messages here.")

	scrollbar = tkinter.Scrollbar(messages_frame)
	msg_list = tkinter.Text(messages_frame, height=15, width=50, bg="#111", yscrollcommand = scrollbar.set)
	scrollbar.config(command = msg_list.yview)

	scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
	msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)
	messages_frame.pack( fill= tkinter.BOTH, expand = 1)

	def clear_box():
		my_msg.set("")
		return True

	label_entry = tkinter.Label(root, text=">>", bg="black", fg="green")
	label_entry.pack(side=tkinter.LEFT)

	entry_field = tkinter.Entry(root, textvariable=my_msg, validate="focusin", validatecommand = clear_box, 
		background="#111", insertbackground="white", foreground="white")
	entry_field.bind("<Return>", send)
	entry_field.pack(padx=2, pady = 5, ipadx=2, ipady=2, fill = tkinter.X, anchor="n", expand = 1, side=tkinter.LEFT)

	emoji_button = tkinter.Button(root, text="Emojis", command = lambda: emoji_chooser(root))
	emoji_button.pack(padx = 2, side=tkinter.LEFT)

	send_button = tkinter.Button(root, text="Send", command=send)
	send_button.pack(padx=5, side=tkinter.LEFT)

	quit_button = tkinter.Button(root, text="Quit", command = on_closing)
	quit_button.pack(padx=5, side=tkinter.LEFT)


	#styling
	msg_list.tag_configure("TAG_INFO", foreground="orange", font="Courier 9")
	msg_list.tag_configure("TAG_NAME", foreground = "green", font="Verdana 9 bold")
	msg_list.tag_configure("TAG_MESSAGE", foreground = "white", font = "Verdana 9")


	root.protocol("WM_DELETE_WINDOW", on_closing)

	return (root, msg_list, my_msg)

def start_main_gui(event = None):
	global HOST, PORT, client_socket
	
	HOST = entry_host.get()
	PORT = int(entry_port.get())
	dialog.destroy()

	ADDR = (HOST, PORT)
	client_socket = socket(AF_INET, SOCK_STREAM)

	try:
		client_socket.connect(ADDR)
	except:
		messagebox.showerror("Connection Error", "Error Connecting to Host:" + HOST + ", Port: " + str(PORT))
		exit()
		
	root.deiconify()
	receive_thread = Thread(target=receive)
	receive_thread.start()

def splash_screen():

	dialog = tkinter.Toplevel()
	dialog.resizable(width = False, height = False)
	dialog.title("Chatter - Setup")
	dialog.bind("<Return>", start_main_gui)
	tkinter.Label(dialog, text="Enter Host IP:").grid(row=0, column=0, padx=5)
	entry_host = tkinter.Entry(dialog, width=25)
	entry_host.grid(row=0, column=1, padx=5)
	tkinter.Label(dialog, text="Enter Port: ").grid(row=1, column=0,padx=5)
	entry_port = tkinter.Entry(dialog, width=25)
	entry_port.grid(row=1, column=1, padx=5)
	tkinter.Button(dialog, text="Connect...", command = start_main_gui).grid(row=2, columnspan=2,pady=5)

	dialog.protocol("WM_DELETE_WINDOW", on_closing)

	return entry_host, entry_port, dialog

def load_emojis():
	emojis = os.listdir("./emojis")
	emojis_dict = {}
	for e in emojis:
		name = e.split(".")[0]
		emojis_dict[name] = tkinter.PhotoImage(file = "./emojis/" + e).subsample(2)
	return emojis_dict

def emoji_chooser(parent):
	global my_msg

	top = tkinter.Toplevel(parent)
	top.resizable(width = False, height = False)

	def select_emoji(emoji_name):
		my_msg.set(my_msg.get() + ":" + emoji_name + ":")
		top.destroy()

	top_frame = tkinter.Frame(top)
	row ,column = (0, 0)
	for e in emojis:

		select_emoji_with_arg = partial(select_emoji, e)
		tkinter.Button(top_frame, image = emojis[e], command = select_emoji_with_arg, width = 40, height=40).grid(row = row, column = column)
		column += 1
		if column%4 == 0:
			column = 0
			row += 1	

	top_frame.pack()
	top.mainloop()



HOST = None
PORT = None
BUFSIZ = 1024
client_socket = None
USER_NAME = None
root, msg_list, my_msg = setup_ui()
entry_host,entry_port, dialog = splash_screen()

emojis = load_emojis()

root.withdraw()
dialog.mainloop()
root.mainloop()  