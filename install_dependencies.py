import subprocess

def install_dependencies():
    # List of required modules in your project
    required_modules = [
        'tkinter',
        'threading',
        'socket',
        'os',
        'time',
        'pickle',
        'logging',
    ]

    for module in required_modules:
        try:
            # Install each module one by one and redirect errors to a log file
            with open('pip_install_log.txt', 'a') as log_file:
                subprocess.run(['pip', 'install', module], stdout=log_file, stderr=log_file, check=True)
                print(f"'{module}' module was installed")
        except subprocess.CalledProcessError as e:
            print(f"The module '{module}' is either already installed or their is some version error")
        except Exception as e:
            print(f"An unexpected error occurred during installation of {module}: {e}")
        
        finally:
            subprocess.run(['del', 'pip_install_log.txt'], shell=True)
    
    print("\nPlease install 'netifaces' module using conda prompt as explained in the readme file\n(ignore this if it is installed already)")

    print("Press any key to Exit.")
    input()

if __name__ == '__main__':
    install_dependencies()
