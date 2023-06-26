import subprocess
import threading
from cassandra.cluster import Cluster
import helpers.Printer as Printer
import main.Ansible as Ansible
import main.HiveMind as HiveMind
import main.Philotic as Philotic

class Cosine_Cassandra:
    def __init__(self):
        self.cluster = None
        self.session = None

    def connect_to_cassandra(self):
        stop_event = threading.Event()  # Create a threading.Event object
        waiting_thread = threading.Thread(target=Printer.waiting, args=("Connecting to Cassandra", stop_event))
        waiting_thread.start()
        try:
            self.cluster = Cluster(['127.0.0.1'])
            self.session = self.cluster.connect()
            stop_event.set()
            Printer.type("\033[32mConnected to Cassandra Successfully!\033[0m\n------------------------------------")
        except Exception as e:
            Printer.error_response(f"Error connecting to Cassandra: {e}")
            exit(0)
    
        # Wait for the waiting thread to finish
        waiting_thread.join()

    def shutdown(self):
        if self.session is not None:
            self.session.shutdown()
        if self.cluster is not None:
            self.cluster.shutdown()
        Printer.type("Goodbye!\n - Cristian Turbeville")

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode(), error.decode()

def shell(app):
    while True:
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

    Printer.print_help()
    # Enter shell interface for the user to enter input!
    shell(app)
