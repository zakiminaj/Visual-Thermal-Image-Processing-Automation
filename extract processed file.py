import os
import shutil
import time
from datetime import timedelta

# Define a function to log error folders
def log_error(folder_path, error_message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"Error in folder: {folder_path}\n")
        #log_file.write(f"Error message: {error_message}\n\n")

source_folder = input("\nEnter the path to the directory where you want to start scanning: ")

def copy_folder(source_folder):
    with os.scandir(source_folder) as entries:
        # Checking for every entry in source_folder until it finds "2. PROCESSED"
        for entry in entries:
            if entry.is_dir() and "PROCESSED" in entry.name.upper():
                # Create the RAW folder in the same directory as PROCESSED
                thermal_folder, visual_folder = check_raw_folder(source_folder)
                # Scan PROCESSED folder
                with os.scandir(entry.path) as grid_entries:
                    for grid_entry in grid_entries:
                        if grid_entry.is_dir():
                            grid_folder = os.path.join(entry.path, grid_entry.name)
                            with os.scandir(grid_folder) as pole_entries:
                                for pole_entry in pole_entries:
                                    if pole_entry.is_dir():
                                        pole_folder = os.path.join(grid_folder, pole_entry.name)
                                        if not os.path.exists(os.path.join(thermal_folder, pole_entry.name)):
                                            try:
                                                shutil.copytree(pole_folder, os.path.join(thermal_folder, pole_entry.name))
                                            except Exception as e:
                                                log_error(pole_folder, str(e))
                                        if not os.path.exists(os.path.join(visual_folder, pole_entry.name)):
                                            try:
                                                shutil.copytree(pole_folder, os.path.join(visual_folder, pole_entry.name))
                                            except Exception as e:
                                                log_error(pole_folder, str(e))
        
            elif entry.is_dir():
                # Recursively call this function for the subfolder
                copy_folder(entry.path)

def check_raw_folder(source_folder):
    raw_folder = os.path.join(source_folder, "3. RAW")
    
    # Check if "THERMAL" subfolder exists or create it
    thermal_folder = os.path.join(raw_folder, "THERMAL")
    os.makedirs(thermal_folder, exist_ok=True)

    # Check if "VISUAL" subfolder exists or create it
    visual_folder = os.path.join(raw_folder, "VISUAL")
    os.makedirs(visual_folder, exist_ok=True)

    return thermal_folder, visual_folder

def remove_duplicate(source_folder):
    with os.scandir(source_folder) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name.upper() in ["3. RAW", "RAW"]:
                raw_folder = os.path.join(source_folder, entry.name)
                with os.scandir(raw_folder) as raw_entries:
                    for raw_entry in raw_entries:
                        if raw_entry.is_dir() and raw_entry.name.upper() in ["THERMAL"]:
                            pole_folder = os.path.join(raw_folder, raw_entry.name)
                            with os.scandir(pole_folder) as pole_entries:
                                for pole_entry in pole_entries:
                                    if pole_entry.is_dir():
                                        try:
                                            extract_and_save_images_from_thermal_folders(pole_entry.path)
                                            # Once extracted, remove thermal images with _snapshot.
                                            check_RAW(pole_folder, pole_entry)
                                        except Exception as e:
                                            log_error(pole_folder, str(e))

                        elif raw_entry.is_dir() and raw_entry.name.upper() in ["VISUAL"]:
                            pole_folder = os.path.join(raw_folder, raw_entry.name)
                            with os.scandir(pole_folder) as pole_entries:
                                for pole_entry in pole_entries:
                                    if pole_entry.is_dir():
                                        try:
                                            extract_and_save_images_from_visual_folders(pole_entry.path)
                                            # Once extracted, remove visual images with _snapshot, -200, -720, -1024
                                            check_RAW(pole_folder, pole_entry)
                                        except Exception as e:
                                            log_error(pole_folder, str(e))

            elif entry.is_dir():
                # Recursively call this function for the subfolder
                remove_duplicate(entry.path)
            else:
                continue

# Function to move files of a specific type from subfolders to their parent folder
def extract_files_of_type_to_parent_folder(src_dir, dest_dir):
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(dest_dir, file)
            shutil.move(src_path, dest_path)

def extract_and_save_images_from_thermal_folders(root_dir):                  
    for root, dirs, files in os.walk(root_dir):
        # Loop to extract image files from THERMAL and remove VISUAL folder
        for dir_name in dirs:
            if dir_name.upper() in ["THERMAL"]:
                thermal_folder = os.path.join(root, dir_name)
                parent_folder = os.path.dirname(thermal_folder)
                extract_files_of_type_to_parent_folder(thermal_folder, parent_folder)
            elif dir_name.upper() in ["VISUAL"]:
                visual_folder = os.path.join(root, dir_name)
                if os.path.exists(visual_folder):
                    shutil.rmtree(visual_folder)
        # Loop to delete .pdf file
        for file_name in files:
            if file_name.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file_name)
                os.remove(pdf_path)

    # After extraction is complete, delete the "THERMAL" folders
    for root, dirs, _ in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name.upper() in ["THERMAL"]:
                thermal_folder = os.path.join(root, dir_name)
                if os.path.exists(thermal_folder):
                    shutil.rmtree(thermal_folder)

def extract_and_save_images_from_visual_folders(root_dir):              
    for root, dirs, files in os.walk(root_dir):
        # Loop to extract image files from VISUAL and remove THERMAL folder
        for dir_name in dirs:
            if dir_name.upper() in ["VISUAL"]:
                visual_folder = os.path.join(root, dir_name)
                parent_folder = os.path.dirname(visual_folder)
                extract_files_of_type_to_parent_folder(visual_folder, parent_folder)
            elif dir_name.upper() in ["THERMAL"]:
                thermal_folder = os.path.join(root, dir_name)
                if os.path.exists(thermal_folder):
                    shutil.rmtree(thermal_folder)
        # Loop to delete .pdf file
        for file_name in files:
            if file_name.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file_name)
                os.remove(pdf_path)
   
    # After extraction is complete, delete the "VISUAL" folders
    for root, dirs, _ in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name.upper() in ["VISUAL"]:
                visual_folder = os.path.join(root, dir_name)
                if os.path.exists(visual_folder):
                    shutil.rmtree(visual_folder)

# Function to remove unnecessary files (snapshot & thumbnails) in RAW folder                     
def check_RAW(pole_folder, pole_entry):
    image_folder = os.path.join(pole_folder, pole_entry.name)
    with os.scandir(image_folder) as image_entries:
        for image_entry in image_entries:   
            filename = image_entry.name
            if "_snapshot" in filename or "-200" in filename or "-720" in filename or "-1024" in filename:
                try:
                    os.remove(image_entry.path)
                except Exception as e:
                    log_error(image_folder, str(e))

# Create an error log file or clear the existing one
with open("error_log.txt", "w") as log_file:
    log_file.write("Error Log:\n\n")

start_time = time.time()
copy_folder(source_folder)
end_time = time.time()
elapsed_time = timedelta(seconds = end_time - start_time)
print(f"\nCopying completed in {elapsed_time}!")

start_time = time.time()
remove_duplicate(source_folder)
end_time = time.time()
elapsed_time = timedelta(seconds = end_time - start_time)
print(f"\nData cleaning completed in {elapsed_time}!")
