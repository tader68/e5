import os
import logging
import threading
from auto_backup import create_backup
from db_versioning import create_db_snapshot
from file_change_tracker import start_file_tracking

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instance/logs/update_app.log'
)

def integrate_change_tracking(app, db):
    """
    Integrate all change tracking components into the Flask application.
    This should be called after the app and db are initialized.
    """
    try:
        # Ensure logs directory exists
        if not os.path.exists('instance/logs'):
            os.makedirs('instance/logs')
        
        # Import DB event logger and set it up
        from db_event_logger import setup_db_event_logging
        event_logger = setup_db_event_logging(app, db)
        
        # Create initial database snapshot if it doesn't exist
        from db_versioning import DatabaseVersioning
        db_version = DatabaseVersioning()
        if not db_version.version_history.get('versions'):
            create_db_snapshot("Initial application state")
        
        # Hook into app lifecycle events
        @app.before_first_request
        def before_first_request():
            """Run before the first request to the application."""
            logging.info("Application received first request")
            # Create a backup when the app starts serving
            create_backup()
        
        # Start file tracking in a separate thread
        def start_file_tracking_thread():
            try:
                # Import and start the file change tracking
                from file_change_tracker import FileChangeHandler
                from watchdog.observers import Observer
                
                event_handler = FileChangeHandler()
                observer = Observer()
                observer.schedule(event_handler, '.', recursive=True)
                
                logging.info("Starting file change tracking")
                observer.start()
                
                # Store the observer in the app context for potential shutdown
                app.file_observer = observer
                
            except Exception as e:
                logging.error(f"Error starting file tracking: {str(e)}")
        
        # Start file tracking in a background thread
        file_tracking_thread = threading.Thread(target=start_file_tracking_thread)
        file_tracking_thread.daemon = True  # Make thread a daemon so it exits when the main thread exits
        file_tracking_thread.start()
        
        # Hook into app teardown events
        @app.teardown_appcontext
        def teardown_db_event_logger(exception=None):
            """Close any resources when the app context ends."""
            pass  # Nothing to do for now, but could be used for cleanup
        
        # Register command to create a code backup
        @app.cli.command('backup')
        def backup_command():
            """Create a backup of the code and database."""
            backup_path = create_backup()
            if backup_path:
                logging.info(f"Backup created at {backup_path}")
                return f"Backup created at {backup_path}"
            return "Backup failed"
        
        # Register command to create a db snapshot
        @app.cli.command('db-snapshot')
        def db_snapshot_command():
            """Create a snapshot of the database schema."""
            result = create_db_snapshot("Manual snapshot")
            if result:
                return "Database snapshot created"
            return "Database snapshot failed"
        
        logging.info("Change tracking components integrated successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error integrating change tracking: {str(e)}")
        return False

def update_app_with_change_tracking():
    """
    Main function to update the Flask app with change tracking.
    This should be run once to modify the app.py file.
    """
    try:
        # Read the current app.py file
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if we've already added the change tracking imports
        if 'import update_app' in content:
            logging.info("Change tracking already integrated into app.py")
            return False
        
        # Add the import and function call to the app.py
        import_line = "import update_app\n"
        init_line = "    update_app.integrate_change_tracking(app, db)\n"
        
        # Find where to insert the lines
        lines = content.split('\n')
        
        # Find the import section
        import_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_index = i + 1
        
        # Find a good place to call our initialization, usually after db init
        init_index = None
        for i, line in enumerate(lines):
            if 'db.init_app(app)' in line:
                init_index = i + 1
        
        if not init_index:
            # Try to find another good insertion point
            for i, line in enumerate(lines):
                if 'app.config.from_' in line:
                    init_index = i + 1
        
        if not init_index:
            # Last resort, add it near the beginning of the file
            init_index = import_index + 1
        
        # Insert the lines
        lines.insert(import_index, import_line)
        lines.insert(init_index + 1, init_line)  # +1 because we added a line earlier
        
        # Write the updated content back to the file
        with open('app.py', 'w') as f:
            f.write('\n'.join(lines))
        
        logging.info("Successfully updated app.py with change tracking integration")
        return True
        
    except Exception as e:
        logging.error(f"Error updating app.py: {str(e)}")
        return False

if __name__ == "__main__":
    # Ensure logs directory exists
    if not os.path.exists('instance/logs'):
        os.makedirs('instance/logs')
    
    # Update the app with change tracking
    success = update_app_with_change_tracking()
    
    if success:
        print("Successfully integrated change tracking into the application.")
        print("The following features are now available:")
        print("1. Automatic code backups")
        print("2. Database schema versioning")
        print("3. File change tracking")
        print("4. Database event logging")
        print("5. New Flask CLI commands: 'flask backup' and 'flask db-snapshot'")
    else:
        print("Failed to integrate change tracking. Check the logs for details.") 