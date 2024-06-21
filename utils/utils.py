import json

def load_products(file_path):
    with open(file_path) as f:
        return json.load(f)
