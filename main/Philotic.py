from flask import Flask, render_template

app = Flask(__name__)

# note that the webpage will not work at the moment as it must have the cluster and session passed
# cmd to run: flask --app Philotic.py run
def get_keyspaces_data(cluster, session):
    keyspace_name = input("Enter the KeySpace to query ")

    # Retrieve all tables in the "hive" keyspace
    query_tables = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = {keyspace_name}"
    rows_tables = session.execute(query_tables)

    tables_data = []

    # Retrieve column information and data for each table
    for row in rows_tables:
        table_name = row.table_name

        # Retrieve column information for the table
        query_columns = f"SELECT column_name, type FROM system_schema.columns WHERE keyspace_name = 'hive' AND table_name = '{table_name}'"
        rows_columns = session.execute(query_columns)

        # Exclude the embedding column from the column list
        columns = [(row.column_name, row.type) for row in rows_columns if row.column_name != 'embedding']

        # Retrieve data for the table excluding the embedding column
        columns_list = ', '.join([column[0] for column in columns])
        query_data = f"SELECT {columns_list} FROM hive.{table_name}"
        rows_data = session.execute(query_data)

        # Store the table data in a dictionary
        table_data = {
            'table': table_name,
            'columns': columns,
            'data': rows_data
        }

        # Add the table data to the list
        tables_data.append(table_data)

    # Close the Cassandra connection
    cluster.shutdown()

    return tables_data

@app.route('/')
def index(app):
    # Get the tables data
    tables_data = get_keyspaces_data(app.cluster, app.session)

    # Render the HTML template with the tables data
    return render_template('index.html', tables_data=tables_data)

if __name__ == '__main__':
    app.run()