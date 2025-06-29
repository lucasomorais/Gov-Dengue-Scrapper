import os
import shutil
import glob
import re
from datetime import datetime


current_date = datetime.now().strftime("%Y_%m_%d")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMP_DIR = "temp/"
SOURCE_DIR = "_results/"
OUTPUT_DIR = "output/"
DENGUE_DIR = "dengue_" + current_date + "/"

def ensure_directories_exist(*folders):
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def get_latest_epidemiology_file(source_folder):
    pattern = os.path.join(source_folder, "Epidemiology_Dengue_*.xlsx")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError("No Epidemiology_Dengue_*.xlsx files found.")
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def copy_latest_file_to_temp():
    source_dir = SOURCE_DIR
    temp_dir = TEMP_DIR
    ensure_directories_exist(source_dir, temp_dir)
    latest_file = get_latest_epidemiology_file(source_dir)
    destination = os.path.join(temp_dir, os.path.basename(latest_file))
    shutil.copy2(latest_file, destination)
    print(f"Copied {latest_file} to {destination}")

def find_latest_file_in_subfolders(pattern, output_dir='output'):
    """
    Finds the most recent file matching the given pattern in the specified directory and its subdirectories,
    prioritizing folders named 'dengue_*' if present.
    
    :param pattern: The file name pattern to search for (e.g., 'SE-Y-*.yaml')
    :param output_dir: The directory to search in (default is 'output')
    :return: The path to the most recent file
    :raises FileNotFoundError: If no files are found matching the pattern
    """
    # First, find all dengue_* folders in the output directory
    dengue_folders = glob.glob(os.path.join(output_dir, 'dengue_*'), recursive=False)
    files = []
    
    # Search for files matching the pattern in dengue_* folders
    for folder in dengue_folders:
        files.extend(glob.glob(os.path.join(folder, pattern)))
    
    # If no files found in dengue_* folders, search in output_dir and other subdirectories
    if not files:
        files = glob.glob(os.path.join(output_dir, '**', pattern), recursive=True)
    
    if not files:
        raise FileNotFoundError(f"No files found matching {pattern} in {output_dir}")
    
    def extract_date(filename):
        match = re.search(r'(\d{4}_\d{2}_\d{2})', filename)
        if match:
            return datetime.strptime(match.group(1), "%Y_%m_%d")
        return datetime.min
    
    latest_file = max(files, key=extract_date)
    return latest_file