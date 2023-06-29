import os
import requests
import helpers.Printer as Printer

def main(text): 
    openai_api_url = 'https://api.openai.com/v1/embeddings'
    api_key = os.getenv('API_KEY')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'input': text,
        'model': 'text-embedding-ada-002'
    }

    try:
        response = requests.post(openai_api_url, headers=headers, json=data)
        embedding_response = response.json()
        embedding_values = embedding_response['data'][0]['embedding']
    except Exception as e:
        Printer.error_response(f"There was an error accessing the openai API!: {e}\n")
        Printer.error_response(f"Network Response Error: {response.text}")
        exit(0)

    return {'embedding_values': embedding_values, 'text': text, 'status': response.ok}