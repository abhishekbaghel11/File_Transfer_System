import socket
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import PhotoImage
from tkinter import messagebox
import subprocess
import threading
import time 
import pickle

download_directory = "../download"

def main():
    client = None
    receive_file_var = False #varaible to take care of the receive files thread (make True when socket is connected otherwise false)
    total_file_size = 0
    data_recv = 0

    def make_connection():
        nonlocal client
        nonlocal receive_file_var
        try:
            make_connection_button.config(state='disabled')

            #create a udp socket to receive the server ip address through the broadcasting 
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.settimeout(10)
            udp_socket.bind((socket.gethostbyname(socket.gethostname()), 12345)) 

            
            msg, ip_address = udp_socket.recvfrom(1024)

            conf_msg = "Received"
            udp_socket.sendto(conf_msg.encode(), ip_address)

            udp_socket.close()

            #get the server ip address 
            server_ip_address = ip_address[0]

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((server_ip_address, 12345))

            #make the receive_file_var true 
            receive_file_var = True

            #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
            file_transfer_status_label.config(text="Status messages for file transfer.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
            file_transfer_status_label.grid(padx=10, pady=5, row=0, column=0)
            #clearing the icon too
            icon = tk.Label(file_transfer_status_frame, text="                         \n\n\n\n")
            icon.grid(row=1, column=0, padx=10) 

            #update the status frame 
            connection_status_label.config(text=f"Connected with the server:{server_ip_address}", fg="blue")

            # Display a connection icon
            connect_icon = PhotoImage(file="..\pictures\icons8-connected-people-100.png").subsample(1,1)
            connect_label = tk.Label(connection_status_frame, image=connect_icon)
            connect_label.image = connect_icon  # Keep a reference to the image
            connect_label.grid(row=1, column=0, padx=10) 

            close_connection_button.config(state='active')

        except socket.timeout:
            #close the udp socket 
            udp_socket.close()

            connection_status_label.config(text='The server timed out', fg='red')

            #add icons 
            connect_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
            connect_label = tk.Label(connection_status_frame, image=connect_icon)
            connect_label.image = connect_icon  # Keep a reference to the image
            connect_label.grid(row=1, column=0, padx=10) 

            make_connection_button.config(state='active')


        except OSError as e:
            if e.errno == 10061:
                #update the status frame 
                connection_status_label.config(text=f"There is no sender", fg="red")

                # Display a connection icon
                connect_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                connect_label = tk.Label(connection_status_frame, image=connect_icon)
                connect_label.image = connect_icon  # Keep a reference to the image
                connect_label.grid(row=1, column=0, padx=10) 

        except Exception as e:
            connection_status_label.config(text=f"Connection error: {e}", fg="red")

    def close_connection():
        nonlocal client
        nonlocal receive_file_var
        try:
            client.close()

            #make the receive_file_var false
            receive_file_var = False

            make_connection_button.config(state='active')
            close_connection_button.config(state='disabled')
        except Exception as e:
            connection_status_label.config(text=f"Error closing connection: {e}", fg="red")

        #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
        connection_status_label.config(text="Status messages for connections.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
        connection_status_label.grid(padx=10, pady=5, row=0, column=0)
        #clearing the icon too
        icon = tk.Label(connection_status_frame, text="                         \n\n\n\n")
        icon.grid(row=1, column=0, padx=10) 

        #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
        connection_status_label.config(text="Status messages for file transfer.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
        connection_status_label.grid(padx=10, pady=5, row=0, column=0)
        #clearing the icon too
        icon = tk.Label(connection_status_frame, text="                         \n\n\n\n")
        icon.grid(row=1, column=0, padx=10) 

    def receive_files():
        nonlocal client
        nonlocal receive_file_var
        nonlocal total_file_size
        nonlocal data_recv

        #so that the thread is always running 
        while True:
            while receive_file_var:
                try:
                    #receive the tuple data from the server
                    serialized_data = client.recv(1024)
                    data_tuple = pickle.loads(serialized_data)
                    (file_name, total_file_size) = data_tuple 

                    #if a file is selected for transfer--> give acknowledgement to receive or not
                    if file_name:
                        #ask if you want to accept the file 
                        if messagebox.askokcancel("Decision", f"Do you want to accept the file: {file_name}?"):
                            #send the acknowledgement msg that the file is accepted
                            client.send(b'Accepted')
                            #######################################################

                            file_path = os.path.join(download_directory, file_name)

                            os.makedirs(download_directory, exist_ok=True)

                            #Update the status label of file transfer
                            time.sleep(1)
                            file_transfer_status_label.config(text=f"Selected file: {file_name}", fg="blue")
                            
                            #clear area for progress bar 
                            icon = tk.Label(file_transfer_status_frame, text="                          \n\n\n\n")
                            icon.grid(row=1, column = 0, padx=10)

                            #progress bar 
                            progress_bar = ttk.Progressbar(file_transfer_status_frame, mode='determinate')
                            progress_bar.grid(row=1, column=0, padx=10, ipadx=50)

                            #create a token whether there was any error in sending file or not
                            data_transfer_success_token = "Success" #--> by default success
                            try:
                                with open(file_path, 'wb') as file:
                                    data_recv = 0 #make the data 0, since that might get used if its value is not made zero at start of each file transfer

                                    i = 0 
                                    while True:
                                        i += 1
                                        #We have to send and receive data on both sides such that --> when a chunk is received , it is known and then only the server sends the next chunk because the server.send doesnt wait for recv , but recv waits for the receival of message by the client or the server 

                                        data = client.recv(1024)
                                        if not data or data == b'a':
                                            break
                                        data_recv += len(data)
                                        if(i%1000 == 0):
                                            update_progress(progress_bar, data_recv)
                                        client.send(b'chunk received')
                                        file.write(data)
                            
                            except ConnectionResetError:
                                data_transfer_success_token = "Failure"

                                #remove the progress bar 
                                progress_bar.grid_remove()

                                file_transfer_status_label.config(text="File transfer failed!", fg="red")

                                #Display a error icon
                                error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                                error_label = tk.Label(file_transfer_status_frame, image=error_icon)
                                error_label.image = error_icon  # Keep a reference to the image
                                error_label.grid(row=1, column=0, padx=10) 

                            except Exception as e:
                                data_transfer_success_token = "Failure"

                                #remove the progress bar
                                progress_bar.grid_remove()

                                file_transfer_status_label.config(text="File transfer failed!", fg="red")

                                #Display a error icon
                                error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                                error_label = tk.Label(file_transfer_status_frame, image=error_icon)
                                error_label.image = error_icon  # Keep a reference to the image
                                error_label.grid(row=1, column=0, padx=10) 

                            finally:
                                # Close the file if it's open, even if an exception occurred
                                if 'file' in locals():
                                    file.close()

                                #remove the progress bar 
                                progress_bar.grid_remove()

                                #delete the received file if there was data transfer failure
                                if data_transfer_success_token == "Failure":
                                    if os.path.exists(file_path):
                                        os.remove(file_path)

                            time.sleep(0.5)

                            if not data or data == b'a': #succesful transfer of file 
                                file_transfer_status_label.config(text="File received successfully!", fg="green")

                                # Display a success icon
                                success_icon = PhotoImage(file="..\pictures\icons8-happy-100.png").subsample(1,1)
                                success_label = tk.Label(file_transfer_status_frame, image=success_icon)
                                success_label.image = success_icon  # Keep a reference to the image
                                success_label.grid(row=1, column=0, padx=10) 

                        else:
                            #send the acknowledgement msg that the file is accepted
                            client.send(b'Rejected')
                            #######################################################

                    if not file_name:
                        continue


                except OSError as e:
                    if e.errno == 10054 or e.errno == 10053: #sending data to a lost connection
                        #no data being sent to read but still reading (or) the connection was aborted by the software system 
                        start_close_connection_thread()

                        time.sleep(0.5)

                        #update the status in the connection status frame 
                        connection_status_label.config(text="The connection was aborted" ,fg="red")

                        #Display a error icon
                        error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                        error_label = tk.Label(connection_status_frame, image=error_icon)
                        error_label.image = error_icon  # Keep a reference to the image
                        error_label.grid(row=1, column=0, padx=10) 

                        #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
                        file_transfer_status_label.config(text="Status messages for file transfer.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
                        file_transfer_status_label.grid(padx=10, pady=5, row=0, column=0)
                        #clearing the icon too
                        icon = tk.Label(file_transfer_status_frame, text="                         \n\n\n\n")
                        icon.grid(row=1, column=0, padx=10)
                    else:
                        print(f'Os Error: {e}')

                except EOFError as e:
                    #no data being sent to read but still reading
                    start_close_connection_thread()
                
                    time.sleep(0.5)

                    #update the status in the connection status frame 
                    connection_status_label.config(text="The connection was aborted" ,fg="red")

                    #Display a error icon
                    error_icon = PhotoImage(file="..\pictures\icons8-error-100.png").subsample(1,1)
                    error_label = tk.Label(connection_status_frame, image=error_icon)
                    error_label.image = error_icon  # Keep a reference to the image
                    error_label.grid(row=1, column=0, padx=10) 

                    #Always clear the file_transfer_status_frame when making a new connection --> make same as it was initially
                    file_transfer_status_label.config(text="Status messages for file transfer.", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
                    file_transfer_status_label.grid(padx=10, pady=5, row=0, column=0)
                    #clearing the icon too
                    icon = tk.Label(file_transfer_status_frame, text="                         \n\n\n\n")
                    icon.grid(row=1, column=0, padx=10)

                except Exception as e:
                    print(f"Receiving Error: {e}")


    def start_make_connection_thread():
        # Create a thread for the make connection function
        transfer_thread = threading.Thread(target=make_connection)
        transfer_thread.daemon = True  # Allow the program to exit even if the thread is still running(closes the thread if the main program closes)
        transfer_thread.start()

    def start_close_connection_thread():
        # Create a thread for the close connection function
        transfer_thread = threading.Thread(target=close_connection)
        transfer_thread.daemon = True  # Allow the program to exit even if the thread is still running(closes the thread if the main program closes)
        transfer_thread.start()

    def on_closing():
        nonlocal client
        nonlocal receive_file_var
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if client is not None:
                try:
                    client.close()
                    receive_file_var = False
                except Exception as e:
                    print(f"Error closing client socket: {e}")
            root.destroy()

    def go_back():
        nonlocal client
        nonlocal receive_file_var

        if messagebox.askokcancel("Return Back", "Do you want to return back?"):
            if client is not None:
                try:
                    client.close()
                    receive_file_var = False
                except Exception as e:
                    print(f"Error closing client socket: {e}")
            root.destroy()

            subprocess.run(["python", "file_transfer_app.py"])


    def btn_hover(event):
        event.widget.config(borderwidth=3, relief='ridge')

    def btn_leave(event):
        event.widget.config(relief="raised", borderwidth=2)

    def update_progress(progress_bar, data_sent):
        nonlocal total_file_size  # Access the variable

        if total_file_size == 0:
            return  # Avoid division by zero

        percentage_complete = (data_sent / total_file_size) * 100
        progress_bar['value'] = percentage_complete
        root.update_idletasks()

    root = tk.Tk()
    root.title("File Receiver GUI")
    root.geometry("400x300")
    root.minsize(500, 600)
    root.configure(bg="#f0f0f0")

    title_label = tk.Label(root, text="File Receiver System", font=("Book Antiqua", 16), bg="#f0f0f0")
    title_label.pack(pady=10)

    connection_frame = tk.Frame(root)
    connection_frame.pack(pady=10)

    make_connection_button = tk.Button(connection_frame, text="Make Connection", command=start_make_connection_thread, bg="#007acc", fg="white", font=("Comic Sans MS", 12), borderwidth=2)
    make_connection_button.pack(pady=10, ipadx=10, padx=10, side='left')

    close_connection_button = tk.Button(connection_frame, text="Close Connection", command=start_close_connection_thread, bg="#007acc", fg="white", font=("Comic Sans MS", 12), borderwidth=2, state='disabled')
    close_connection_button.pack(pady=10, ipadx=10, padx=10, side='left')

    connection_status_frame = tk.Frame(root, relief="solid", borderwidth=1)
    connection_status_frame.pack(pady=10, padx=10)

    connection_status_label = tk.Label(connection_status_frame, text="Status messages for connection.\n\n\n\n", font=("Helvetica", 12), anchor='center', justify='center', fg='grey')
    connection_status_label.grid(padx=10, pady=5, row=0, column=0)

    file_transfer_label = tk.Label(root, text="Status messages for file transfer", font=("Helvetica", 14))
    file_transfer_label.pack(pady = (10,5))

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

    root.protocol("WM_DELETE_WINDOW", on_closing)

    #Threading for the receive file option --> so that it is always running for a connected socket
    receive_thread = threading.Thread(target=receive_files)
    receive_thread.daemon = True
    receive_thread.start()
    #############################################################################################

    root.mainloop()

if __name__ == "__main__":
    main()
