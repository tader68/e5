import os
import shutil
import datetime
import zipfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instance/logs/backup.log'
)

def create_backup():
    """Create a backup of the entire codebase as a ZIP file."""
    try:
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join('instance', 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        # Create a timestamp for the backup file
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_filename = f'lingoboost_backup_{timestamp}.zip'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Create a zip file containing the entire codebase
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the project directory and add files to the zip
            for root, dirs, files in os.walk('.'):
                # Skip some directories
                dirs[:] = [d for d in dirs if d not in ['.conda', '__pycache__', 'instance/backups']]
                
                for file in files:
                    # Skip backup files and database files
                    if not (file.endswith('.zip') or file.endswith('.bak') or 
                            file == 'lingoboost.db' or file.endswith('.pyc')):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, '.')
                        zipf.write(file_path, arcname)
        
        # Also backup the database
        if os.path.exists('lingoboost.db'):
            db_backup_filename = f'lingoboost.db.bak.{timestamp}'
            shutil.copy2('lingoboost.db', db_backup_filename)
            
        logging.info(f"Backup created successfully: {backup_path}")
        logging.info(f"Database backup created: {db_backup_filename}")
        
        # Cleanup old backups (keep only last 10)
        cleanup_old_backups(backup_dir, 10)
        
        return backup_path
    except Exception as e:
        logging.error(f"Backup failed: {str(e)}")
        return None

def cleanup_old_backups(backup_dir, keep_count=10):
    """Remove old backups, keeping only the specified number of recent ones."""
    try:
        # Get all zip backups
        backups = [f for f in os.listdir(backup_dir) if f.startswith('lingoboost_backup_') and f.endswith('.zip')]
        backups.sort(reverse=True)  # Most recent first
        
        # Remove excess backups
        if len(backups) > keep_count:
            for old_backup in backups[keep_count:]:
                os.remove(os.path.join(backup_dir, old_backup))
                logging.info(f"Removed old backup: {old_backup}")
        
        # Cleanup old DB backups, keep only 10
        db_backups = [f for f in os.listdir('.') if f.startswith('lingoboost.db.bak.')]
        db_backups.sort(reverse=True)
        
        if len(db_backups) > keep_count:
            for old_db_backup in db_backups[keep_count:]:
                os.remove(old_db_backup)
                logging.info(f"Removed old DB backup: {old_db_backup}")
                
    except Exception as e:
        logging.error(f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    # Ensure logs directory exists
    if not os.path.exists('instance/logs'):
        os.makedirs('instance/logs')
    
    create_backup() 