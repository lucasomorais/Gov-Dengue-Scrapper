from modules.utils import ensure_directories_exist, get_latest_epidemiology_file, copy_latest_file_to_temp, TEMP_DIR, SOURCE_DIR




if __name__ == "__main__":
    ensure_directories_exist()
    get_latest_epidemiology_file(SOURCE_DIR)
    copy_latest_file_to_temp()
