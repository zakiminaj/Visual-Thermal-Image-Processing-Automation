import os
import shutil
import pandas as pd

# Define the paths
csv_file = 'D:\\SPECIAL PROJECT\\2024\\JUN\\PULAU INDAH\\FLIGHT 1\\FINDING\\PULAU INDAH LATERAL (TULIP) LATERAL June 2024 - FULL.csv'
source_dir = 'D:\\SPECIAL PROJECT\\2024\\JUN\\PULAU INDAH\\FLIGHT 1\\RAW'
target_dir = 'D:\\SPECIAL PROJECT\\2024\\JUN\\PULAU INDAH\\FLIGHT 1\\FINDING'

# Read the CSV file
data = pd.read_csv(csv_file)

# Extract the filenames
file_column = '!"Filename'  # Adjust the column name if necessary
filenames = data[file_column].tolist()

# Ensure the target directory exists
os.makedirs(target_dir, exist_ok=True)

# Copy the files
for filename in filenames:
    source_path = os.path.join(source_dir, filename)
    target_path = os.path.join(target_dir, filename)
    
    if os.path.exists(source_path):
        shutil.copy(source_path, target_path)
        print(f"Copied: {filename}")
    else:
        print(f"File not found: {filename}")

print("File copying process completed.")
