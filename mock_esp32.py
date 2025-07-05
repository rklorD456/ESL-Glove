import requests
import pandas as pd
import sys
import json

# The URL of your local Flask server's prediction endpoint
SERVER_URL = "http://127.0.0.1:5000/predict"

def send_csv_data(file_path):
    """Reads a CSV, formats it as JSON, and sends it to the server."""
    
    print(f"Attempting to send data from: {file_path}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"❌ Error: File not found at '{file_path}'")
        return

    # Define the sensor columns your model expects
    selected_columns = ["flex0", "flex1", "flex2", "flex3", "flex4", "accX", "accY", "gyroX", "gyroY"]

    # Check if the CSV has the required columns and rows
    if not all(col in df.columns for col in selected_columns):
        print("❌ Error: The CSV file is missing one or more required sensor columns.")
        return
    if df.shape[0] != 750:
        print(f"❌ Error: The CSV file must have exactly 750 rows, but it has {df.shape[0]}.")
        return

    # Prepare the data in the correct format (a list of lists)
    sensor_values = df[selected_columns].values.tolist()

    # Create the final JSON payload
    payload = {"sensor_data": sensor_values}

    # Set the correct header
    headers = {"Content-Type": "application/json"}

    # Send the POST request to the server
    try:
        response = requests.post(SERVER_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        print("✅ Data sent successfully!")
        print(f"✅ Server responded with: {response.json()}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending data to server: {e}")

if __name__ == '__main__':
    # Check if a file path was provided as an argument
    if len(sys.argv) < 2:
        print("Usage: python mock_esp32.py <path_to_your_csv_file>")
    else:
        # Get the file path from the command line argument
        csv_file = sys.argv[1]
        send_csv_data(csv_file)