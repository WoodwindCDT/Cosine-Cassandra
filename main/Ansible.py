import helpers.Messenger as Messenger
import helpers.Printer as Printer
from sklearn.metrics.pairwise import cosine_similarity

def start_ansible(app, text):
    # Get the text from the user and then continue
    res = Messenger.main(text)

    if (res['status']):
        session = app.session

        Printer.print_tables(app.tables)
        table_name = input("Enter the table name to query: ")

        # Enter the amount of similarities to expect
        num_similarities = int(input("Enter the number of similar responses to display: "))

        if (num_similarities > 0): 
            # Retrieve all embeddings and corresponding texts from the Cassandra table
            query = f"SELECT embedding, text, id FROM {app.keyspace}.{table_name}"
            try:
                rows = session.execute(query)
            except Exception as e:
                print(f"Error accessing that Table: {e}")
                exit(0)
            
            # Calculate cosine similarity between input embedding and database
            similarities = []
            for row in rows:
                db_embedding = row.embedding
                similarity = cosine_similarity([res['embedding_values']], [db_embedding])[0][0]
                similarities.append((similarity, row.text, row.id))

            similarities.sort(reverse=True)

            # Display top 5 similar
            print(f"Displaying {num_similarities} Responses:\n")
            for similarity, text, id in similarities[:num_similarities]:
                Printer.type(f"Similarity: {similarity:.4f} | Text: {text} | ID: {id}")
        else:
            print("Please enter a number of similarities greater than 0")
            exit(1)