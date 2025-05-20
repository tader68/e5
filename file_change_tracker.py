import os
import json
import time
import hashlib
import logging
import sys
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instance/logs/file_changes.log'
)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, changes_file='instance/changes/file_changes.json'):
        self.changes_file = os.path.abspath(changes_file)
        self.changes = self.load_changes()
        self.ensure_changes_dir()
        logging.info(f"Tracking changes, excluding: {self.changes_file}")
    
    def ensure_changes_dir(self):
        changes_dir = os.path.dirname(self.changes_file)
        if not os.path.exists(changes_dir):
            os.makedirs(changes_dir)
    
    def load_changes(self):
        if os.path.exists(self.changes_file):
            try:
                with open(self.changes_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'changes': []}
        return {'changes': []}
    
    def save_changes(self):
        try:
            # First create a temp copy to avoid infinite event loop
            temp_file = f"{self.changes_file}.temp"
            with open(temp_file, 'w') as f:
                json.dump(self.changes, f, indent=4)
            
            # Then rename it to the actual file
            if os.path.exists(self.changes_file):
                os.remove(self.changes_file)
            os.rename(temp_file, self.changes_file)
        except Exception as e:
            logging.error(f"Error saving changes: {str(e)}")
    
    def calculate_file_hash(self, file_path):
        try:
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                return file_hash
            return None
        except Exception as e:
            logging.error(f"Error calculating hash for {file_path}: {str(e)}")
            return None
    
    def on_created(self, event):
        if event.is_directory:
            return
        if self.should_track_file(event.src_path):
            file_hash = self.calculate_file_hash(event.src_path)
            self.log_change('created', event.src_path, file_hash)
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        if self.should_track_file(event.src_path):
            self.log_change('deleted', event.src_path, None)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        if self.should_track_file(event.src_path):
            file_hash = self.calculate_file_hash(event.src_path)
            self.log_change('modified', event.src_path, file_hash)
    
    def on_moved(self, event):
        if event.is_directory:
            return
        if self.should_track_file(event.src_path):
            self.log_change('moved', event.src_path, None, dest_path=event.dest_path)
    
    def should_track_file(self, file_path):
        # Convert to absolute path for exact comparison
        abs_path = os.path.abspath(file_path)
        
        # Skip our own changes file to avoid infinite loop
        if abs_path == self.changes_file or abs_path.endswith('.temp'):
            return False
            
        # Skip backup files, cache files, and other non-essential files
        ignore_patterns = [
            '.pyc', '.pyo', '.bak', '.zip', '__pycache__', 
            'instance/backups', 'instance/logs', '.conda',
            '.git', '.temp'
        ]
        
        for pattern in ignore_patterns:
            if pattern in file_path:
                return False
        
        return True
    
    def log_change(self, change_type, file_path, file_hash, dest_path=None):
        try:
            # Skip our own changes file
            if os.path.abspath(file_path) == self.changes_file:
                return
                
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get relative path for better readability
            rel_path = os.path.relpath(file_path)
            rel_dest = os.path.relpath(dest_path) if dest_path else None
            
            change = {
                'timestamp': timestamp,
                'type': change_type,
                'file': rel_path,
                'hash': file_hash
            }
            
            if dest_path:
                change['destination'] = rel_dest
            
            self.changes['changes'].append(change)
            self.save_changes()
            
            # Also log to regular log file
            log_message = f"{change_type.upper()}: {rel_path}"
            if dest_path:
                log_message += f" to {rel_dest}"
            logging.info(log_message)
            
        except Exception as e:
            logging.error(f"Error logging change: {str(e)}")

def start_file_tracking():
    # Create logs directory if it doesn't exist
    if not os.path.exists('instance/logs'):
        os.makedirs('instance/logs')
    
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    
    logging.info("File change tracking started")
    print("File change tracking started. Press Ctrl+C to stop.")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("File change tracking stopped.")
        logging.info("File change tracking stopped")
    except Exception as e:
        observer.stop()
        print(f"Error: {str(e)}")
        logging.error(f"Error in file tracking: {str(e)}")
    
    observer.join()
    print("File change tracker exited.")

if __name__ == "__main__":
    start_file_tracking() 