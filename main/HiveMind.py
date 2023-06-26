import helpers.Messenger as Messenger
import helpers.Printer as Printer
import threading
import uuid

def start_hivemind(app, text):
    # Get the text from the user and then continue
    res = Messenger.main(text)

    if (res['status']):
        session = app.session

        table_name = input("Enter the table name to query: ")

        # Generate a unique UUID
        unique_id = uuid.uuid4()

        stop_event = threading.Event()  # Create a threading.Event object
        waiting_thread = threading.Thread(target=Printer.waiting, args=("Inserting Data", stop_event))
        waiting_thread.start()
        # Insert the embedding vector into the Cassandra table
        try:
            session.execute(
                f"INSERT INTO hive.{table_name} (id, embedding, text) VALUES (%s, %s, %s)",
                (unique_id, res['embedding_values'], res['text'])
            )
            stop_event.set()
            Printer.print_ascii()
        except Exception as e:
            Printer.error_response(f"Error accessing that Table, most likely does not exist!: {e}")
            exit(0)