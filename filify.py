import argparse
import os
import shutil
import json
from datetime import datetime
import uuid

CONFIG_FILE = 'config.json'
LOG_FILE = 'filify.log'


def load_config():
    """Load the JSON configuration file."""
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {CONFIG_FILE} not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {CONFIG_FILE} contains invalid JSON.")
        exit(1)


def log_move(original_path, new_path):
    """Log file moves with timestamps."""
    commit_id = generate_commit_id()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp} | {commit_id} | {original_path} -> {new_path}\n")


def generate_commit_id():
    """Generate a unique commit ID."""
    return str(uuid.uuid4())[:8]


# Load settings
config = load_config()
DIRECTORY = config.get("directory", os.getcwd())  # Default to current directory if not set
GROUP_EXTENSIONS = config.get("group_extensions", {})
UNSORTED_FOLDER = config.get("unsorted_folder", "Unsorted")


def list_files_and_folders():
    """List all files and folders in the specified directory."""
    try:
        # Get all files and folders in the directory
        entries = os.listdir(DIRECTORY)

        # Separate files and folders
        files = [entry for entry in entries if os.path.isfile(os.path.join(DIRECTORY, entry))]
        folders = [entry for entry in entries if os.path.isdir(os.path.join(DIRECTORY, entry))]

        return files, folders

    except FileNotFoundError:
        print(f"The directory {DIRECTORY} does not exist.")
        exit(1)
    except PermissionError:
        print(f"Permission denied to access {DIRECTORY}.")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


def categorize_files(dir_files):
    """Categorize and move files based on their extensions."""
    try:
        # Create categorized folders if they don't exist
        for category in GROUP_EXTENSIONS:
            category_folder = os.path.join(DIRECTORY, category)
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)

        # Create 'Unsorted' folder for unknown files
        unsorted_folder = os.path.join(DIRECTORY, 'Unsorted')
        if not os.path.exists(unsorted_folder):
            os.makedirs(unsorted_folder)

        # Categorize and move files
        for file in dir_files:
            file_path = os.path.join(DIRECTORY, file)

            if '.' not in file:
                new_path = os.path.join(unsorted_folder, file)
                shutil.move(file_path, new_path)
                log_move(file_path, new_path)
                print(f"Moved: {file} to {UNSORTED_FOLDER}")
                continue

            file_extension = file.split('.')[-1].lower()

            # Check if the file extension belongs to any category
            moved = False
            for category, extensions in GROUP_EXTENSIONS.items():
                if file_extension in extensions:
                    destination_folder = os.path.join(DIRECTORY, category)
                    new_path = os.path.join(destination_folder, file)

                    shutil.move(file_path, new_path)
                    log_move(file_path, new_path)
                    print(f'Moved: {file} to {category}')
                    moved = True
                    break

            if not moved:
                new_path = os.path.join(unsorted_folder, file)
                shutil.move(file_path, new_path)
                log_move(file_path, new_path)
                print(f'Moved: {file} to {UNSORTED_FOLDER}')

    except FileNotFoundError:
        print(f"The directory {DIRECTORY} does not exist.")
        exit(1)
    except PermissionError:
        print(f"Permission denied to access {DIRECTORY}.")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


def undo_by_commit_id(commit_id):
    """Undo the move by the given commit ID."""
    if not os.path.exists(LOG_FILE):
        print("No log file found. Nothing to undo.")
        return

    with open(LOG_FILE, "r") as log_file:
        lines = log_file.readlines()

    undone = False
    for i, line in enumerate(reversed(lines)):
        if commit_id in line:
            try:
                _, _, move_entry = line.strip().split(" | ")
                original, new = move_entry.split(" -> ")
                if os.path.exists(new):
                    shutil.move(new, original)
                    print(f"Restored: {new} -> {original}")
                    lines.pop(len(lines) - 1 - i)  # Remove this line from the log
                    undone = True
                    break
                else:
                    print(f"Error: {new} not found. Cannot restore.")
                    return
            except Exception as e:
                print(f"Error undoing commit {commit_id}: {e}")
                return
    if undone:
        # Rewrite the log file without the undone action
        with open(LOG_FILE, "w") as log_file:
            log_file.writelines(lines)
    else:
        print(f"Commit ID {commit_id} not found in the log.")


def undo_last_moves(n):
    """Undo the last N moves based on the log."""
    if not os.path.exists(LOG_FILE):
        print("No log file found. Nothing to undo.")
        return

    with open(LOG_FILE, "r") as log_file:
        lines = log_file.readlines()

    if not lines:
        print("Log file is empty. Nothing to undo.")
        return

    last_moves = lines[-n:]  # Get last N moves
    successful_undos, failed_undos = [], []

    for move in reversed(last_moves):  # Undo in reverse order
        try:
            commit_id, _, move_entry = move.strip().split(" | ")
            original, new = move_entry.split(" -> ")
            if os.path.exists(new):
                shutil.move(new, original)
                successful_undos.append(f"Restored: {new} -> {original} (Commit ID: {commit_id})")
            else:
                failed_undos.append(f"Missing: {new} (Cannot restore) (Commit ID: {commit_id})")
        except Exception as e:
            failed_undos.append(f"Error undoing commit {commit_id}: {e}")

    if successful_undos:
        print("\nUndo Successful:")
        for entry in successful_undos:
            print(entry)

    if failed_undos:
        print("\nUndo Failed:")
        for entry in failed_undos:
            print(entry)

    # Remove the undone actions from the log
    with open(LOG_FILE, "w") as log_file:
        log_file.writelines(lines[:-n])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filify - Organize files with commit-based undo.")
    parser.add_argument("--undo", type=int, default=0, help="Undo the last N moves")
    parser.add_argument("--undo_commit", type=str, help="Undo the move by specific commit ID")
    args = parser.parse_args()

    files, folders = list_files_and_folders()
    if args.undo > 0:
        undo_last_moves(args.undo)
    elif args.undo_commit:
        undo_by_commit_id(args.undo_commit)
    else:
        categorize_files(files)
