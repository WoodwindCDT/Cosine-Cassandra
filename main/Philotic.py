from flask import Flask, render_template
from cassandra.cluster import Cluster
import threading

app = Flask(__name__)

def connect_to_cassandra():
    cluster = Cluster(['127.0.0.1'])  # Specify the Cassandra cluster IP address
    session = cluster.connect()
    return session

def get_keyspaces_data(session, keyspace):
    query_tables = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{keyspace}'"
    rows_tables = session.execute(query_tables)

    tables_data = []

    for row in rows_tables:
        table_name = row.table_name

        query_columns = f"SELECT column_name, type FROM system_schema.columns WHERE keyspace_name = '{keyspace}' AND table_name = '{table_name}'"
        rows_columns = session.execute(query_columns)

        columns = [(row.column_name, row.type) for row in rows_columns if row.column_name != 'embedding']

        columns_list = ', '.join([column[0] for column in columns])
        query_data = f"SELECT {columns_list} FROM {keyspace}.{table_name}"
        rows_data = session.execute(query_data)

        table_data = {
            'table': table_name,
            'columns': columns,
            'data': rows_data
        }

        tables_data.append(table_data)

    return tables_data

def run_flask(session, keyspace):
    # Store the session and keyspace in the Flask app's config
    app.config['session'] = session
    app.config['keyspace'] = keyspace

    app.run()

@app.route('/')
def index():
    # Retrieve the session and keyspace from the app's config
    session = app.config['session']
    keyspace = app.config['keyspace']

    tables_data = get_keyspaces_data(session, keyspace)
    session.shutdown()

    return render_template('index.html', tables_data=tables_data)

if __name__ == '__main__':
    keyspace = input("Enter the KeySpace to query: ")

    session = connect_to_cassandra()

    # Start web ui in separate thread
    flask_thread = threading.Thread(target=run_flask, args=(session, keyspace))
    flask_thread.start()