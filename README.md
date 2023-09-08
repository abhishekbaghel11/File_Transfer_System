# File Transfer System

The File Transfer System I have created is a Python-based application that enables users to transfer files over a local area network (LAN) or Wi-Fi. It simplifies the process of sharing files between devices connected to the same network.

## Features

- User-friendly interface for transferring files.
- Images used in the Python scripts enhance the user experience.

## Installation

To use the File Transfer System, follow these steps:

1. Download the project files from the GitHub repository.

2. Don't change the relative paths of the files or the files would not work(although you can create a shortcut for the exe file if you want) 

3. Navigate to the project directory:
  ```shell
    cd file-transfer-system
  ```
3. Create a virtual environment (recommended) in the project directory:
```shell
  python -m venv env_name
  ```  
4. Activate the virtual environment:
```shell
  env_name\Scripts\activate
```
5. Install the `subprocess` module if it is not installed:
```shell
  pip install subprocess
```
6. Run the `install_dependencies.exe` file to install the required Python modules (you can check the required modules in the `requirements.txt` file) :
```shell
  install_dependencies.exe
```
7. You have to install the `netifaces` module of python using the anaconda prompt (if `pip install netifaces` doesn't work) . Open the anaconda prompt and type the following command:
```shell
  conda install -c anaconda netifaces
```
8. Ensure you have Python and anaconda installed on your system.

9. Make the firewall system of your device to allow the tcp and udp connections on the port 12345, you can refer to the following link: https://pureinfotech.com/open-port-firewall-windows-10/#:~:text=To%20open%20a%20Windows%20firewall,select%20the%20%E2%80%9CPort%E2%80%9D%20option.

10. Also enable the public and private connections for `python.exe` by going to `Windows Defender Firewall>Allow an app or feature through Windows defender firewall` and then click on change settings and check all the boxes(public,private,domain) for `python.exe` as shown in the image below:

![python.exe](https://filestore.community.support.microsoft.com/api/images/ddca82b8-6dc9-420d-a62e-cdd8e5483dac?upload=true)

11. Open a terminal or command prompt and navigate to the project directory.

12. Run the main executable file to start the File Transfer System.

13. Please ensure that both the devices are connected to the same wifi/lan network.

## Dependencies

The following Python modules are required to run the File Transfer System (can be found in the requirements.txt) :

- tkinter
- threading
- socket
- os
- time
- pickle
- logging
- netifaces

## Screenshots

- For the main gui window:-->
![Main GUI window](https://drive.google.com/uc?export=view&id=1iDIJ-xg2gcWdPs-3LVJaxI6zjVONHDzd)
- For the transfer and receiver interfaces:-->
![Transfer and Receiver](https://drive.google.com/uc?export=view&id=1tSYLhlMlMl6Q6xBhm2Xlbex3Qa0hj7q1) 

## Contact

If you have any questions or feedback, feel free to reach out:

- Email: abhishekbaghel301@gmail.com
- GitHub: https://github.com/abhishekbaghel11


