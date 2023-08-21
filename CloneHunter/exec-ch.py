import os
import hashlib
import shutil
import re
from collections import defaultdict
import datetime

# Very simple duplicate file detector by sx66
os.system('clear') 

LOG_FILENAME = "log.txt"

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = "[{}] {}".format(timestamp, message)
    with open(LOG_FILENAME, "a") as log_file:
        log_file.write(log_entry + "\n")

def move_files(files, destination):
    for file in files[1:]: 
        base_name, extension = os.path.splitext(os.path.basename(file))
        dest_path = os.path.join(destination, os.path.basename(file))
        counter = 1
        while os.path.exists(dest_path):
            new_base_name = "{} (copy {})".format(base_name, counter)
            dest_path = os.path.join(destination, "{}{}".format(new_base_name, extension))
            counter += 1
        shutil.move(file, dest_path)
        log_message("Moved '{}' to '{}'".format(file, dest_path))

def find_duplicates(directory):
    duplicates = defaultdict(list)
    filenames_to_hash = defaultdict(list)

    for root, dirs, files in os.walk(directory):
        for filename in files:
            match = re.search(r'\(copy(?: \d+)?\)', filename)
            if match:
                file_path = os.path.join(root, filename)
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                duplicates[file_hash].append(file_path)
            else:
                file_size = os.path.getsize(os.path.join(root, filename))
                filenames_to_hash[(filename, file_size)].append(os.path.join(root, filename))

    for _, file_list in filenames_to_hash.items():
        if len(file_list) > 1:
            for file_path in file_list:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                duplicates[file_hash].append(file_path)

    return {hash_value: file_list for hash_value, file_list in duplicates.items() if len(file_list) > 1}

def print_ascii_art():
    ascii_art_file = "ASCII.txt"
    if os.path.exists(ascii_art_file):
        with open(ascii_art_file, "r") as f:
            ascii_art = f.read()
            print(ascii_art)

def main():
    print_ascii_art()  # Print ASCII art at the beginning

    enable_logging = input("Do you want to enable logging? (yes/no): ")
    if enable_logging.lower() == "yes":
        if os.path.exists(LOG_FILENAME):
            os.remove(LOG_FILENAME)

    directory = input("Enter the directory path: ")

    duplicates = find_duplicates(directory)

    if not duplicates:
        print("No duplicate files found.")
        return

    if enable_logging.lower() == "yes":
        log_message("Duplicate files found:")
    for hash_value, file_list in duplicates.items():
        if enable_logging.lower() == "yes":
            log_message("Hash: {}".format(hash_value))
        for file_path in file_list:
            if enable_logging.lower() == "yes":
                log_message("  - {}".format(file_path))

    action = input("What do you want to do? (delete/move/quit): ")

    if action.lower() == "delete":
        for hash_value, file_list in duplicates.items():
            if enable_logging.lower() == "yes":
                log_message("Moving duplicates with hash {} to trash.".format(hash_value))
            move_to_trash(file_list[1:])
    elif action.lower() == "move":
        destination = input("Enter the destination directory for duplicates: ")
        if not os.path.exists(destination):
            os.makedirs(destination)
        for hash_value, file_list in duplicates.items():
            if enable_logging.lower() == "yes":
                log_message("Moving duplicates with hash {} to {}.".format(hash_value, destination))
            move_files(file_list, destination)
    elif action.lower() == "quit":
        print("Exiting without making any changes.")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
