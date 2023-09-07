import socket
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter import messagebox
import tkinter.ttk as ttk
import os
import threading
import subprocess
import time
import pickle
import netifaces as ni

def main():
    server = None
    client = None
    total_file_size = 0
    data_sent = 0

    def make_connection():
        nonlocal server, client

        try:
            #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
            file_transfer_status_label.config(text="Status messages for file transfer.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
            file_transfer_status_label.grid(padx=10, pady=5, row=0, column=0)
            #clearing the icon too
            icon = tk.Label(file_transfer_status_frame, text="                         \n\n\n\n")
            icon.grid(row=1, column=0, padx=10) 

            #disable the make_connection btn--> enable through the close_connection btn 
            make_connection_button.config(state='disabled')

            #enable the close_connection btn 
            close_connection_button.config(state='active')
            
            #get the device ip address
            server_ip_address = socket.gethostbyname(socket.gethostname())

            #broadcasting the ip address using the udp socket + receiving a msg of confirmation 
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.settimeout(5)
            broadcast_addr = get_broadcast_address()

            msg = "I am the broadcasting server"
            time.sleep(5)

            #broadcast the msg
            udp_socket.sendto(msg.encode(), (broadcast_addr, 12345)) #use any available port

            #get confirmation msg from the client
            conf_msg, client_ip_address = udp_socket.recvfrom(1024)

            #close the socket 
            udp_socket.close()

            if conf_msg.decode() != "Received":
                return 

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((server_ip_address, 12345))
            server.listen(1)
            make_connection_status_label.config(text="Server listening...", fg="green")

            #display a listening icon
            listen_icon = PhotoImage(file="..\pictures\icons8-iphone-spinner-100.png").subsample(1,1)
            listen_label = tk.Label(make_connection_status_frame, image=listen_icon)
            listen_label.image = listen_icon  # Keep a reference to the image
            listen_label.grid(row=1, column=0, padx=10) 
            
            clients_served = 0
            while clients_served < 1:
                client, address = server.accept()
                make_connection_status_label.config(text=f"Connection from {address}", fg="blue")
                file_transfer_button.config(state='active')

                # Display a connection icon
                connect_icon = PhotoImage(file="..\pictures\icons8-connected-people-100.png").subsample(1,1)
                connect_label = tk.Label(make_connection_status_frame, image=connect_icon)
                connect_label.image = connect_icon  # Keep a reference to the image
                connect_label.grid(row=1, column=0, padx=10) 

                clients_served += 1

        #handle the timeout error of the udp socket 
        except socket.timeout:
            #close the udp socket 
            udp_socket.close()

            make_connection_status_label.config(text='The server timed out', fg='red')

            #add icons 
            connect_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
            connect_label = tk.Label(make_connection_status_frame, image=connect_icon)
            connect_label.image = connect_icon  # Keep a reference to the image
            connect_label.grid(row=1, column=0, padx=10) 

            #enable the make connection and disable the close connection 
            make_connection_button.config(state='active') 
            close_connection_button.config(state='disabled')

        except OSError as e:
            if e.errno == 10038:
                pass
            elif e.errno == 10048:
                make_connection_status_label.config(
                    text="A server using the port already exists,\nwait for it to finish its process",
                    fg="red"
                )

                #Display a error icon
                error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                error_label = tk.Label(make_connection_status_frame, image=error_icon)
                error_label.image = error_icon  # Keep a reference to the image
                error_label.grid(row=1, column=0, padx=10) 
            else:
                print(f"Socket error: {e}")
        

        except Exception as e:
            print(f"Error in make connection: {e}")

    def close_connection():
        nonlocal server, client

        #disable close_connection button 
        close_connection_button.config(state='disabled')

        #close the client and server socket
        if client is not None:
            try:
                client.close()
                # to resolve a error in file transfer function --> closing the connection in between the file , the finally function activates the file transfer button(we dont want that)
                client = None
            except Exception as e:
                print(f"Error closing client socket: {e}")

        if server is not None:
            try:
                server.close()
                server = None
            except Exception as e:
                print(f"Error closing server socket: {e}")

        #Also make the status messages go back to its default state------>

        #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
        make_connection_status_label.config(text="Status messages for connections.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
        make_connection_status_label.grid(padx=10, pady=5, row=0, column=0)
        #clearing the icon too
        icon = tk.Label(make_connection_status_frame, text="                         \n\n\n\n")
        icon.grid(row=1, column=0, padx=10) 

        #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
        file_transfer_status_label.config(text="Status messages for file transfer.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
        file_transfer_status_label.grid(padx=10, pady=5, row=0, column=0)
        #clearing the icon too
        icon = tk.Label(file_transfer_status_frame, text="                         \n\n\n\n")
        icon.grid(row=1, column=0, padx=10) 

        #disable the file_transfer btn
        file_transfer_button.config(state='disabled')
        #disable the make_connection btn--> enable through the close_connection btn 
        make_connection_button.config(state='active')

    def select_file_and_transfer():
        nonlocal server, client, total_file_size, data_sent

        try:
            file_transfer_button.config(state="disabled")

            file_path = filedialog.askopenfilename()
            if file_path:
                file_name = os.path.basename(file_path)

                total_file_size = os.path.getsize(file_path)

                #send the file_name and size at the same time using pickle serialization 
                data_tuple = (file_name, total_file_size)
                serialized_data = pickle.dumps(data_tuple)
                client.send(serialized_data)

                #Acknowledgement msg whether the client wants to receive the file or not
                acknowledge_msg = client.recv(1024).decode()

                if acknowledge_msg == "Accepted":
                    file_transfer_status_label.config(text=f'File was {acknowledge_msg}', fg="green")

                    # Display a connection icon
                    connect_icon = PhotoImage(file="..\pictures\icons8-connected-people-100.png").subsample(1,1)
                    connect_label = tk.Label(file_transfer_status_frame, image=connect_icon)
                    connect_label.image = connect_icon  # Keep a reference to the image
                    connect_label.grid(row=1, column=0, padx=10) 
                    # connect_label.pack(padx=10)

                    time.sleep(1)
                    file_transfer_status_label.config(text=f"Selected file: {file_name}", fg="blue")

                    # Display a success icon
                    success_icon = PhotoImage(file="..\pictures\icons8-done-100.png").subsample(1,1)
                    success_label = tk.Label(file_transfer_status_frame, image=success_icon)
                    success_label.image = success_icon  # Keep a reference to the image
                    success_label.grid(row=1, column=0, padx=10) 
                    # success_label.pack(padx=10)

                    try:
                        #create the progress bar

                        #destroy prev widget before making a progress bar
                        icon = tk.Label(file_transfer_status_frame, text="                          \n\n\n\n")
                        icon.grid(row=1, column = 0, padx=10)

                        progress_bar = ttk.Progressbar(file_transfer_status_frame, mode='determinate')
                        progress_bar.grid(row=1, column=0, padx=10, ipadx=50)

                        with open(file_path, 'rb') as file:
                            data_sent = 0 #make the data 0, since that might get used if its value is not made zero at start of each file transfer
                            i = 0
                            data = file.read(1024)
                            while data:
                                i += 1
                                #update the value of the progress bar
                                data_sent += len(data)
                                if (i%1000) == 0:
                                    update_progress(progress_bar, data_sent)

                                #We have to send and receive data on both sides such that --> when a chunk is received , it is known and then only the server sends the next chunk because the server.send doesnt wait for recv , but recv waits for the receival of message by the client or the server 

                                #main process of loop--> data transfer
                                client.send(data)
                                update = client.recv(1024).decode()
                                if update == 'chunk received':
                                    data = file.read(1024)
                            #to close the recv of the client --> had an extra recv for data = None
                            client.send(b'a') #don't know why but this wasn't working for b''

                    except ConnectionResetError:

                        # #Display a error icon
                        # error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                        # error_label = tk.Label(file_transfer_status_frame, image=error_icon)
                        # error_label.image = error_icon  # Keep a reference to the image
                        # error_label.grid(row=1, column=0, padx=10) 

                        #call the close connection function
                        start_close_connection_thread()

                        time.sleep(0.5)

                        #update the status in the connection status frame 
                        make_connection_status_label.config(text="The connection was aborted" ,fg="red")

                        #Display a error icon
                        error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                        error_label = tk.Label(make_connection_status_frame, image=error_icon)
                        error_label.image = error_icon  # Keep a reference to the image
                        error_label.grid(row=1, column=0, padx=10) 

                        #come out of the function no need anymore
                        file.close()
                        return

                    except OSError as e:
                        if e.errno == 10038: #sending data(a operation) through something which is not a socket(or a closed socket)
                            #call the close connection function
                            start_close_connection_thread()

                            time.sleep(0.5)

                            #update the status in the connection status frame 
                            file_transfer_status_label.config(text="The file transfer failed!" ,fg="red")
                            # make_connection_status_label.config(text="Server listening...", fg="green")

                            #Display a error icon
                            error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                            error_label = tk.Label(file_transfer_status_frame, image=error_icon)
                            error_label.image = error_icon  # Keep a reference to the image
                            error_label.grid(row=1, column=0, padx=10) 

                            #come out of the function no need anymore
                            file.close()
                            return

                            
                    except Exception as e:
                        #remove the progress bar
                        progress_bar.grid_remove()

                        file_transfer_status_label.config(text=f"Error sending data: {e}", fg="red")

                        #Display a error icon
                        error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                        error_label = tk.Label(file_transfer_status_frame, image=error_icon)
                        error_label.image = error_icon  # Keep a reference to the image
                        error_label.grid(row=1, column=0, padx=10) 
                    finally:
                        file.close()

                        #remove the progress bar
                        progress_bar.grid_remove()

                        # We don't want to close the connection , we want even further transfer of files with the connection --> so don't close it 

                    time.sleep(0.5)

                    if not data:
                        file_transfer_status_label.config(text="File was sent successfully!", fg="green")

                        # Display a success icon
                        success_icon = PhotoImage(file="..\pictures\icons8-happy-100.png").subsample(1,1)
                        success_label = tk.Label(file_transfer_status_frame, image=success_icon)
                        success_label.image = success_icon  # Keep a reference to the image
                        success_label.grid(row=1, column=0, padx=10)         

                    else:
                        file_transfer_status_label.config(text="Error occurred:\nFile was not sent successfully!", fg="red")

                        #Display a error icon
                        error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                        error_label = tk.Label(file_transfer_status_frame, image=error_icon)
                        error_label.image = error_icon  # Keep a reference to the image
                        error_label.grid(row=1, column=0, padx=10)

                else:
                    file_transfer_status_label.config(text=f'File was {acknowledge_msg}', fg="red")

                    # Display a connection icon
                    connect_icon = PhotoImage(file="..\pictures\icons8-sad-100.png").subsample(1,1)
                    connect_label = tk.Label(file_transfer_status_frame, image=connect_icon)
                    connect_label.image = connect_icon  # Keep a reference to the image
                    connect_label.grid(row=1, column=0, padx=10) 

            else:
                client.send(b'')
                file_transfer_status_label.config(text="No file selected", fg="red")

                #Display a error icon
                error_icon = PhotoImage(file="..\pictures\icons8-cancel-100.png").subsample(1,1)
                error_label = tk.Label(file_transfer_status_frame, image=error_icon)
                error_label.image = error_icon  # Keep a reference to the image
                error_label.grid(row=1, column=0, padx=10) 

        except OSError as e:
            if e.errno == 10054: #the client closed the connection
                #call the close connection function
                start_close_connection_thread()
                
                time.sleep(0.5)

                #update the status in the connection status frame 
                make_connection_status_label.config(text="The connection was aborted" ,fg="red")

                #Display a error icon
                error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                error_label = tk.Label(make_connection_status_frame, image=error_icon)
                error_label.image = error_icon  # Keep a reference to the image
                error_label.grid(row=1, column=0, padx=10) 

            else:
                print(f"Error in file transfer: {e}")



        except Exception as e:
            print(f"Error in file transfer: {e}")
        finally:
            #in order that the close connection does not make the file transfer active due to the finally statement --> therefore the condition is added to avoid this
            if server is not None:
                file_transfer_button.config(state="active")

    def start_make_connection_thread():
        # Create a thread for the make connection function
        transfer_thread = threading.Thread(target=make_connection)
        transfer_thread.daemon = True  # Allow the program to exit even if the thread is still running(closes the thread if the main program closes)
        transfer_thread.start()

    def start_close_connection_thread():
        # Create a thread for the make connection function
        transfer_thread = threading.Thread(target=close_connection)
        transfer_thread.daemon = True  # Allow the program to exit even if the thread is still running(closes the thread if the main program closes)
        transfer_thread.start()

    def start_file_transfer_thread():
        # Create a thread for the file selection and transfer unction
        transfer_thread = threading.Thread(target=select_file_and_transfer)
        transfer_thread.daemon = True  # Allow the program to exit even if the thread is still running(closes the thread if the main program closes)
        transfer_thread.start()

    def on_closing():
        nonlocal server, client
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if client is not None:
                try:
                    client.close()
                except Exception as e:
                    print(f"Error closing client socket: {e}")

            if server is not None:
                try:
                    server.close()
                except Exception as e:
                    print(f"Error closing server socket: {e}")

            root.destroy()

    def go_back():
        nonlocal server, client
        
        if messagebox.askokcancel("Return Back", "Do you want to return back?"):
            if client is not None:
                try:
                    client.close()
                except Exception as e:
                    print(f"Error closing client socket: {e}")

            if server is not None:
                try:
                    server.close()
                except Exception as e:
                    print(f"Error closing server socket: {e}")

            root.destroy()

            subprocess.run(["python", "file_transfer_app.py"])

    def btn_hover(event):
        event.widget.config(borderwidth=3, relief='ridge')

    def btn_leave(event):
        event.widget.config(relief="raised", borderwidth=2)

    #updates the value of the progress bar 
    def update_progress(progress_bar, data_sent):
        nonlocal total_file_size  # Access the variable

        if total_file_size == 0:
            return  # Avoid division by zero

        percentage_complete = (data_sent / total_file_size) * 100
        progress_bar['value'] = percentage_complete
        root.update_idletasks()

    #get the broadcast address of the device 
    def get_broadcast_address():
        try:
            # Get your computer's IP address
            hostname = ni.gateways()['default'][ni.AF_INET][1]
            addrs = ni.ifaddresses(hostname)

            if ni.AF_INET in addrs:
                broadcast_address = addrs[ni.AF_INET][0]['broadcast']
                return broadcast_address
        except Exception as e:
            print(f"Error: {e}")
        return None

    root = tk.Tk()
    root.title("File Transfer GUI")
    root.geometry("400x200")
    root.minsize(500, 600)
    root.configure(bg="#f0f0f0")

    title_label = tk.Label(root, text="File Transfer System", font=("Book Antiqua", 16), bg="#f0f0f0")
    title_label.pack(pady=10)

    connection_frame = tk.Frame(root)
    connection_frame.pack(pady=10)

    make_connection_button = tk.Button(connection_frame, text="Make Connection", command=start_make_connection_thread, bg="#007acc", fg="white", font=("Comic Sans MS", 12), borderwidth=2)
    make_connection_button.pack(pady=10, ipadx=10, padx = 10, side='left')

    close_connection_button = tk.Button(connection_frame, text="Close Connection",command=start_close_connection_thread, bg="#007acc", fg="white", font=("Comic Sans MS", 12), borderwidth=2, state='disabled')
    close_connection_button.pack(pady=10, ipadx=10, padx = 10, side='left')

    make_connection_status_frame = tk.Frame(root, relief="solid", borderwidth=1)
    make_connection_status_frame.pack(pady=10, padx=10)

    make_connection_status_label = tk.Label(make_connection_status_frame, text="Status messages for making connection.\n\n\n\n", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
    make_connection_status_label.grid(padx=10, pady=5, row=0, column=0)

    file_transfer_button = tk.Button(root, text="Select File to Transfer", command=start_file_transfer_thread, bg="#007acc", fg="white", font=("Comic Sans MS", 12), borderwidth=2, state ="disabled")
    file_transfer_button.pack(pady=10, ipadx=10)

    file_transfer_status_frame = tk.Frame(root, relief="solid", borderwidth=1)
    file_transfer_status_frame.pack(pady=10, padx=10)

    file_transfer_status_label = tk.Label(file_transfer_status_frame, text="Status messages for file transfer.\n\n\n\n", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
    file_transfer_status_label.grid(padx=10, pady=5, row=0, column=0)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    go_back_button = tk.Button(btn_frame, text="GO BACK", command=go_back, bg="#2c9e4b", fg="white", relief="raised", font=("Comic Sans MS", 10), borderwidth=2)
    go_back_button.pack(side='left', pady=10, padx=10, ipadx=10)

    exit_button = tk.Button(btn_frame, text="EXIT", command=on_closing, bg="#e74c3c", fg="white", relief="raised", font=("Comic Sans MS", 10), borderwidth=2)
    exit_button.pack(side='left', pady=10, padx=10, ipadx=10)

    exit_button.bind("<Enter>", btn_hover)
    exit_button.bind("<Leave>", btn_leave)

    go_back_button.bind("<Enter>", btn_hover)
    go_back_button.bind("<Leave>", btn_leave)

    make_connection_button.bind("<Enter>", btn_hover)
    make_connection_button.bind("<Leave>", btn_leave)

    close_connection_button.bind("<Enter>", btn_hover)
    close_connection_button.bind("<Leave>", btn_leave)

    file_transfer_button.bind("<Enter>", btn_hover)
    file_transfer_button.bind("<Leave>", btn_leave)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()