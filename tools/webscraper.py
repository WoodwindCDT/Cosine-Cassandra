import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import date, datetime
import re

# extractor
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist

import pandas as pd

def drop_non_alpha_numeric(csv_file):
    data = pd.read_csv(csv_file)

    # Iterate over each cell in the DataFrame
    for col in data.columns:
        data[col] = data[col].apply(lambda cell: re.sub(r'[^a-zA-Z0-9$%+\-:\s]+', '', str(cell)) if pd.notnull(cell) else '')
    
    for col in data.columns:
        data[col] = data[col].apply(lambda row: re.sub(r'(.)\1+', r'\1', row))
    
    # Save the modified DataFrame back to the original CSV file
    data.to_csv(csv_file, index=False)

def filter_csv_data(csv_file, keyword_file):
    keywords = set()
    with open(keyword_file, "r") as keyword_csv:
        reader = csv.reader(keyword_csv)
        next(reader)
        for row in reader:
            keyword = row[0].strip()
            keywords.add(keyword.lower())  # Lowercase the keyword

    filtered_rows = []
    unique_rows = set()

    with open(csv_file, "r") as input_csv:
        reader = csv.reader(input_csv)
        header = next(reader)
        filtered_rows.append(header)

        for row in reader:
            lowercased_row = [field.lower() for field in row]  # Lowercase all fields in the row
            row_tuple = tuple(lowercased_row)
            if row_tuple not in unique_rows and any(keyword in field for field in lowercased_row for keyword in keywords):
                unique_rows.add(row_tuple)
                filtered_rows.append(lowercased_row)

    file_name, extension = os.path.splitext(csv_file)
    filtered_csv_file = file_name + "_filtered" + extension
    with open(filtered_csv_file, "w", newline="", encoding="utf-8") as output_csv:
        writer = csv.writer(output_csv)
        writer.writerows(filtered_rows)

    drop_non_alpha_numeric(filtered_csv_file)
    print("Filtered CSV file with only alphanumerics and necessary excpetions.")

def clean_filename(filename):
    # remove those invalid characters from the filename
    cleaned_filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return cleaned_filename

def extract_keywords(csv_file):
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        data = list(reader)

    text = " ".join([row[0] for row in data])

    tokens = word_tokenize(text)

    stop_words = set(stopwords.words("english"))
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]

    # Calc the freq distribution
    fdist = FreqDist(filtered_tokens)
    
    keywords = fdist.most_common(None)

    return keywords

def scrape_webpage():
    url = input("Enter the URL of the webpage you want to scrape: ")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Had some utf-8 errors here
    page_title = clean_filename(soup.title.string)

    paragraphs = soup.find_all("p")
    paragraph_texts = [p.get_text() for p in paragraphs]

    divs = soup.find_all("div")
    div_texts = [div.get_text() for div in divs]

    data = zip(
        (text.strip() for text in div_texts),
        (text.strip() for text in paragraph_texts),
    )

    folder_name = "site_data"
    tools_directory = "tools"
    site_data_directory = os.path.join(tools_directory, folder_name)
    if not os.path.exists(site_data_directory):
        os.makedirs(site_data_directory)

    csv_file = os.path.join(site_data_directory, f"{page_title}.csv")
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Site Title", "Site URL", "Date Accessed", "Time Accessed"])
        writer.writerow([page_title, url, date.today(), datetime.now().time()])
        writer.writerow(["Site Data"])
        writer.writerows([[text] for text in data])

    print("Data has been exported to:", csv_file)

    # Call keyword extraction code
    keywords = extract_keywords(csv_file)
    
    file_name, extension = os.path.splitext(csv_file)
    new_csv_file = file_name + "_post_extraction" + extension

    # Write the extracted keywords to the new CSV file
    with open(new_csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword"])
        writer.writerows(keywords)

    print("Keyword extraction completed.")

    post_extraction_file = os.path.join(site_data_directory, f"{page_title}_post_extraction.csv")

    filter_csv_data(csv_file, post_extraction_file)