# Filify - File Organizer 🗂️

Filify is a Python-based tool designed to automatically organize files in a specified directory (e.g., `Downloads`) based on their file extensions. It categorizes files into predefined folders, logs file movements, and supports undo functionality with commit IDs.

## Features:
- **Organize Files**: Automatically sorts files into categorized folders based on their extensions (e.g., images, documents, media).
- **Undo Functionality**: Restore files by commit ID or undo the last N moves.
- **Log File Movements**: Keeps a log of all file movements with unique commit IDs for easy tracking and undoing.
- **Cron Job Support**: Schedule the script to run daily at a set time (e.g., 10 AM) using `cron`.

## Usage:

### Basic Usage
1. **Organize Files**: Simply run the script to organize files in the desired folder:
```commandline
python3 filify.py
```
2. **Undo the Last N Moves**: To undo the last N file moves:
```commandline
python3 filify.py --undo <N>
```
3. **Undo by Commit ID**: To undo a specific move by commit ID:
```commandline
python3 filify.py --undo_commit <commit_id>
```

### Schedule with Cron (macOS):
1. Edit the `crontab`
```commandline
crontab -e
```
2. Add the following cron job to run the script daily at 10 AM: ([ref: cron-expression](https://crontab.guru/))
```commandline
0 10 * * * /usr/bin/python3 /path/to/filify.py >> /Users/vikas.chaurasiya/Desktop/All/vikasc-personal/filify/cron.log 2>&1
```
3. Save and Exit

## Configuration:
Modify `config.json` to change the directory and file extensions as per your needs.

## Log File:
All file moves are logged in a `filify.log` file, with each action having a unique commit ID. This allows for easy tracking and undoing of specific file moves.


Enjoy a cleaner, more organized workspace with Filify! 🚀