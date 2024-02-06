import pandas as pd
from pymongo import MongoClient
import gzip
import json
import os

# Connect to local MongoDB server
client = MongoClient("mongodb://127.0.0.1:27017/")
mydb = client["ie212_o11_group7"]

# Đường dẫn đến file ZIP
collection_reviews = mydb.reviews
gz_file_path_reviews = "./review_results.jsonl.gz"

collection_places = mydb.places
gz_file_path_places = "./places_results.jsonl.gz"

# Giải nén file GZ
def read_jsonl_gz(file_path):
    data = []
    with gzip.open(file_path, 'rt', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data

# Convert DataFrame to a list of dictionaries (documents)
reviews_records = read_jsonl_gz(gz_file_path_reviews)
places_records = read_jsonl_gz(gz_file_path_places)

# Insert documents (rows) into the MongoDB collection (table)
collection_reviews.insert_many(reviews_records)
collection_places.insert_many(places_records)
