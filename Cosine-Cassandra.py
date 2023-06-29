# system imports
import os
import subprocess
import sys
import threading

# cassandra helper
from cassandra.cluster import Cluster

# various imports for main functionality
import helpers.Printer as Printer
import main.Ansible as Ansible
import main.HiveMind as HiveMind
import main.Philotic as Philotic

# tools import
import tools.webscraper as webscraper

class Cosine_Cassandra:
    def __init__(self):
        self.cluster = None
        self.session = None
        self.tables = None
        self.keyspace = None
        self.flask_process = None
        self.web = False

    def connect_to_cassandra(self):
        stop_event = threading.Event()  # Create a threading.Event object
        waiting_thread = threading.Thread(target=Printer.waiting, args=("Connecting to Cassandra", stop_event))
        waiting_thread.start()
        try:
            self.cluster = Cluster(['127.0.0.1']) # default location of server
            self.session = self.cluster.connect()
            stop_event.set()
            Printer.type("\033[32mConnected to Cassandra Successfully!\033[0m\n------------------------------------")
        except Exception as e:
            Printer.error_response(f"Error connecting to Cassandra: {e}")
            exit(0)
    
        # Wait for the waiting thread to finish
        waiting_thread.join()
    
    def get_info(self):
        self.keyspace = input("Enter the KeySpace to use: ")
        
        try:
            self.tables = self.session.cluster.metadata.keyspaces[f'{self.keyspace}'].tables
        except Exception as e:
            Printer.error_response(f"Error accessing keyspace: {e}")
            exit(0)

    def shutdown(self):
        if self.session is not None:
            self.session.shutdown()
        if self.cluster is not None:
            self.cluster.shutdown()
        if self.flask_process is not None:
            app.flask_process.terminate()
        Printer.type("Goodbye!\n - Cristian Turbeville")

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode(), error.decode()

def shell(app):
    while True:
        if (app.web): print("\033[92m-- web interface open --\033[0m")
        command = input("> ")
        if command.lower() == 'cmd':
            Printer.print_help()
            continue
        if command.lower().startswith('upsert'):
            _, upsert_text = command.lower().split(' ', 1)
            # Call to HiveMind, user wants to store information onto the Cassandra DB
            HiveMind.start_hivemind(app, upsert_text)
            continue
        if command.lower().startswith('query'):
            _, query_text = command.lower().split(' ', 1)
            Ansible.start_ansible(app, query_text)
            continue
        if command.lower().startswith('delete'):
            _, uid = command.lower().split(' ', 1)
            Printer.type(uid)
            continue
        if command.lower().startswith('web'):
            _, opt = command.lower().split(' ', 1)
            if opt is not None:
                if opt == 'i':
                    Printer.type("Starting Web Interface")
                    try:
                        app.flask_process = subprocess.Popen([sys.executable, "./Philotic.py"], cwd=os.path.dirname(Philotic.__file__), shell=True)
                        output, error = app.flask_process.communicate()
                    except Exception as e:
                        Printer.error_response(e)
                    app.web = True # set var to true
                if opt == 'o':
                    Printer.type("Stopping Web Interface")
                    try:
                        app.flask_process.terminate()
                    except Exception as e:
                        Printer.error_response(e)
                    app.web = False
            else: Printer.error_response("Incorrect Parameter! Try i || o")
            continue
        if command.lower() == 'tools':
            while True:
                tools_command = input("tools > ")
                if tools_command.lower() == 'webscrape':
                    webscraper.scrape_webpage()
                    continue
                if tools_command.lower() == 'exit':
                    break
                print("Invalid tools command. Available commands: webscrape, exit")
            continue
        output, error = execute_command(command)
        if output:
            print(output)
        if error:
            Printer.error_response(f"{error}")
        if command.lower() == 'exit':
            # Shutdown the connection on exit
            app.shutdown()
            break
        output, error = execute_command(command)
        if output:
            print(output)
        if error:
            Printer.error_response(f"{error}")

if __name__ == '__main__':
    app = Cosine_Cassandra()
    app.connect_to_cassandra()
    app.get_info()

    Printer.print_help()
    # Enter shell interface for the user to enter input!
    shell(app)