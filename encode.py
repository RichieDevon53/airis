
import json
import base64

def encode_json_file(filepath):
    # Read and load the JSON file
    with open(filepath, 'r') as f:
        json_data = json.load(f)
    
    # Convert JSON to string and encode to base64
    json_str = json.dumps(json_data)
    encoded = base64.b64encode(json_str.encode('utf-8'))
    
    return encoded.decode('utf-8')
if __name__ == "__main__":
    # Example usage
    filepath = 'airis-463702-9964449869ac.json'
    encoded_data = encode_json_file(filepath)
    print(encoded_data)
