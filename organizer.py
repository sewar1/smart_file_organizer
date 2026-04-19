import os
import time
import shutil
import logging
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ==========================================
# LOAD CONFIGURATION FROM JSON
# ==========================================

CONFIG_PATH = "config.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Folder to monitor
FOLDER_TO_WATCH = config["watch_folder"]

# File categories
FILE_TYPES = config["categories"]

# Delay between file checks (optional tuning)
DELAY = config.get("delay_seconds", 2)

# ==========================================
# LOGGING SETUP
# ==========================================

logging.basicConfig(
    filename="organizer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print(f"🚀 File Organizer started. Watching: {FOLDER_TO_WATCH}")

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def create_folder(folder_name):
    """
    Create a folder inside the monitored directory if it doesn't exist.
    """
    path = os.path.join(FOLDER_TO_WATCH, folder_name)
    os.makedirs(path, exist_ok=True)
    return path


def wait_until_file_is_ready(file_path, timeout=10):
    """
    Ensure file is fully downloaded before moving it.
    Prevents corrupted or incomplete moves.
    """
    start_time = time.time()
    previous_size = -1

    while True:
        if not os.path.exists(file_path):
            return False

        current_size = os.path.getsize(file_path)

        # File size stable → file is ready
        if current_size == previous_size:
            return True

        previous_size = current_size

        if time.time() - start_time > timeout:
            return True

        time.sleep(1)


def move_file(file_path):
    """
    Move file into its correct category based on extension.
    """
    if not os.path.isfile(file_path):
        return

    file_name = os.path.basename(file_path)

    # Ignore hidden/system files
    if file_name.startswith("."):
        return

    # Ignore script itself
    if file_name == os.path.basename(__file__):
        return

    # Ignore temporary download files
    if file_name.endswith((".crdownload", ".tmp")):
        return

    logging.info(f"Processing: {file_name}")

    # Wait until file is fully downloaded
    if not wait_until_file_is_ready(file_path):
        return

    moved = False

    for folder, extensions in FILE_TYPES.items():
        if file_name.lower().endswith(tuple(extensions)):

            destination_folder = create_folder(folder)
            destination_path = os.path.join(destination_folder, file_name)

            try:
                shutil.move(file_path, destination_path)
                logging.info(f"Moved: {file_name} → {folder}")
                print(f"✅ {file_name} → {folder}")
            except Exception as e:
                logging.error(f"Error moving {file_name}: {e}")

            moved = True
            break

    # If no category matched → Others
    if not moved:
        destination_folder = create_folder("Others")
        destination_path = os.path.join(destination_folder, file_name)

        try:
            shutil.move(file_path, destination_path)
            logging.info(f"Moved: {file_name} → Others")
            print(f"📦 {file_name} → Others")
        except Exception as e:
            logging.error(f"Error moving {file_name}: {e}")


def organize_existing_files():
    """
    Organize files that already exist in the folder.
    """
    print("🧹 Organizing existing files...")

    try:
        for filename in os.listdir(FOLDER_TO_WATCH):
            file_path = os.path.join(FOLDER_TO_WATCH, filename)

            if os.path.isdir(file_path):
                continue

            move_file(file_path)

        print("✅ Initial cleanup completed.")
        logging.info("Initial cleanup completed.")

    except Exception as e:
        logging.error(f"Error during initial cleanup: {e}")


# ==========================================
# WATCHDOG EVENT HANDLER
# ==========================================

class OrganizerHandler(FileSystemEventHandler):
    """
    Handles real-time file system events.
    """

    def on_created(self, event):
        if not event.is_directory:
            time.sleep(DELAY)
            move_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            time.sleep(DELAY)
            move_file(event.src_path)


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    organize_existing_files()

    observer = Observer()
    event_handler = OrganizerHandler()

    observer.schedule(event_handler, FOLDER_TO_WATCH, recursive=False)
    observer.start()

    print("👀 Monitoring folder in real-time...")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()