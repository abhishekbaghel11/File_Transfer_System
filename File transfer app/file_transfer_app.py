import tkinter as tk
from tkinter import PhotoImage
import subprocess
import threading

# Create the main window
root = tk.Tk()
root.title("File Transfer System")
root.geometry("650x450")

# Create a label for the small picture beside the heading
small_image = PhotoImage(file="..\pictures\icons8-exchange-80.png").subsample(1,1)  # Replace "small_icon.png" with your small image file path
small_label = tk.Label(root, image=small_image)
small_label.pack(pady=10)

# Create a label for the heading
heading_label = tk.Label(root, text="FILE TRANSFER SYSTEM", font=("Helvetica", 16))
heading_label.pack(pady=10)

# Load image files for 'SEND' and 'RECEIVE' buttons
send_image = PhotoImage(file="..\pictures\icons8-send-80.png").zoom(2,2)  # Replace "send.png" with your send image file path
receive_image = PhotoImage(file="..\pictures\icons8-received-80.png").zoom(2,2)  # Replace "receive.png" with your receive image file path

# Function to open the server.py script
def send_clicked():
    try:
        # Start the subprocess in a separate thread
        subprocess_thread = threading.Thread(target=lambda: subprocess.run(["python", "server.py"]))
        subprocess_thread.start()

        # Destroy the tkinter window immediately
        root.destroy()
    except FileNotFoundError:
        print("Error: The 'server.py' script was not found.")
        root.destroy()

# Function to open the client.py script
def receive_clicked():
    try:
        # Start the subprocess in a separate thread
        subprocess_thread = threading.Thread(target=lambda: subprocess.run(["python", "client.py"]))
        subprocess_thread.start()

        # Destroy the tkinter window immediately
        root.destroy()
    except FileNotFoundError:
        print("Error: The 'client.py' script was not found.")
        root.destroy()

def button_hover(event):
    event.widget.config(bg="#59d3ff", fg="white", borderwidth = 3)  # Change background and foreground color on hover

def button_leave(event):
    # Get the top-level (parent) widget of the child
    parent_widget = event.widget.winfo_toplevel()
    
    # Get the background color of the parent widget
    parent_bg_color = parent_widget.cget("bg")
    
    # Set the background color of the child widget to match the parent
    event.widget.config(bg=parent_bg_color, borderwidth = 0) # Restore original colors when leaving

# Create a frame for the buttons and labels
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Create 'SEND' button with the image and label
send_button = tk.Button(button_frame, image=send_image, command=send_clicked,  borderwidth=0, relief='raised')
send_label = tk.Label(button_frame, text="SEND")
send_button.grid(row=0, column=0, padx=20, ipadx = 20, ipady=5)
send_label.grid(row=1, column=0)

# Create 'RECEIVE' button with the image and label
receive_button = tk.Button(button_frame, image=receive_image, command=receive_clicked, borderwidth=0, relief='raised')
receive_label = tk.Label(button_frame, text="RECEIVE")
receive_button.grid(row=0, column=1, padx=20,ipadx = 20, ipady=5)
receive_label.grid(row=1, column=1)

# Bind hover and leave events to the buttons
send_button.bind("<Enter>", button_hover)
send_button.bind("<Leave>", button_leave)

receive_button.bind("<Enter>", button_hover)
receive_button.bind("<Leave>", button_leave)


# Start the Tkinter main loop
root.mainloop()




#Print a socket again and again do not give error 