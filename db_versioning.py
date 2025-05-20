import os
import sqlite3
import json
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instance/logs/db_versioning.log'
)

class DatabaseVersioning:
    def __init__(self, db_file='lingoboost.db', version_file='instance/db_versions/version_history.json'):
        self.db_file = db_file
        self.version_file = version_file
        self.version_history = self.load_version_history()
        self.ensure_version_dir()
        
    def ensure_version_dir(self):
        version_dir = os.path.dirname(self.version_file)
        if not os.path.exists(version_dir):
            os.makedirs(version_dir)
            
    def load_version_history(self):
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'versions': []}
        return {'versions': []}
    
    def save_version_history(self):
        with open(self.version_file, 'w') as f:
            json.dump(self.version_history, f, indent=4)
    
    def create_snapshot(self, description=""):
        """Create a snapshot of the current database schema"""
        try:
            if not os.path.exists(self.db_file):
                logging.error(f"Database file {self.db_file} does not exist")
                return False
                
            # Create a timestamp for this version
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            version_id = f"v{timestamp}"
            
            # Create a backup of the database
            backup_file = f"{self.db_file}.bak.{timestamp}"
            shutil.copy2(self.db_file, backup_file)
            
            # Get schema information
            schema = self.get_current_schema()
            
            # Add this version to our history
            version_info = {
                'version_id': version_id,
                'timestamp': timestamp,
                'description': description,
                'backup_file': backup_file,
                'schema': schema
            }
            
            self.version_history['versions'].append(version_info)
            self.save_version_history()
            
            logging.info(f"Created database snapshot: {version_id} - {description}")
            return True
            
        except Exception as e:
            logging.error(f"Error creating database snapshot: {str(e)}")
            return False
    
    def get_current_schema(self):
        """Extract the current database schema"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema = {}
            
            for table in tables:
                table_name = table[0]
                # Skip sqlite internal tables
                if table_name.startswith('sqlite_'):
                    continue
                    
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                # Format column info
                column_info = []
                for col in columns:
                    column_info.append({
                        'cid': col[0],
                        'name': col[1],
                        'type': col[2],
                        'notnull': col[3],
                        'default': col[4],
                        'pk': col[5]
                    })
                
                schema[table_name] = {
                    'columns': column_info
                }
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                foreign_keys = cursor.fetchall()
                
                if foreign_keys:
                    schema[table_name]['foreign_keys'] = []
                    for fk in foreign_keys:
                        schema[table_name]['foreign_keys'].append({
                            'id': fk[0],
                            'seq': fk[1],
                            'table': fk[2],
                            'from': fk[3],
                            'to': fk[4]
                        })
            
            conn.close()
            return schema
            
        except Exception as e:
            logging.error(f"Error getting database schema: {str(e)}")
            return {}
    
    def compare_with_previous(self):
        """Compare current schema with the previous version"""
        if len(self.version_history['versions']) < 1:
            logging.info("No previous versions to compare with")
            return None
            
        current_schema = self.get_current_schema()
        previous_schema = self.version_history['versions'][-1]['schema']
        
        differences = {
            'new_tables': [],
            'dropped_tables': [],
            'modified_tables': {}
        }
        
        # Check for new and modified tables
        for table_name, table_schema in current_schema.items():
            if table_name not in previous_schema:
                differences['new_tables'].append(table_name)
            else:
                # Check for modified columns
                table_diffs = {
                    'new_columns': [],
                    'dropped_columns': [],
                    'modified_columns': []
                }
                
                current_columns = {col['name']: col for col in table_schema['columns']}
                previous_columns = {col['name']: col for col in previous_schema[table_name]['columns']}
                
                # New columns
                for col_name in current_columns:
                    if col_name not in previous_columns:
                        table_diffs['new_columns'].append(col_name)
                
                # Dropped columns
                for col_name in previous_columns:
                    if col_name not in current_columns:
                        table_diffs['dropped_columns'].append(col_name)
                
                # Modified columns
                for col_name in current_columns:
                    if col_name in previous_columns:
                        if current_columns[col_name] != previous_columns[col_name]:
                            table_diffs['modified_columns'].append(col_name)
                
                # Only add to differences if there are actual changes
                if (table_diffs['new_columns'] or table_diffs['dropped_columns'] 
                        or table_diffs['modified_columns']):
                    differences['modified_tables'][table_name] = table_diffs
        
        # Check for dropped tables
        for table_name in previous_schema:
            if table_name not in current_schema:
                differences['dropped_tables'].append(table_name)
        
        return differences
    
    def restore_version(self, version_id):
        """Restore the database to a specific version"""
        try:
            # Find the version
            version = None
            for v in self.version_history['versions']:
                if v['version_id'] == version_id:
                    version = v
                    break
            
            if not version:
                logging.error(f"Version {version_id} not found")
                return False
            
            # Check if backup file exists
            if not os.path.exists(version['backup_file']):
                logging.error(f"Backup file {version['backup_file']} not found")
                return False
            
            # Create a backup of the current database first
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            current_backup = f"{self.db_file}.before_restore.{timestamp}"
            shutil.copy2(self.db_file, current_backup)
            
            # Restore the database
            shutil.copy2(version['backup_file'], self.db_file)
            
            logging.info(f"Database restored to version {version_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error restoring database: {str(e)}")
            return False
    
    def list_versions(self):
        """List all available versions"""
        return self.version_history['versions']

def create_db_snapshot(description=""):
    """Utility function to create a database snapshot"""
    # Ensure logs directory exists
    if not os.path.exists('instance/logs'):
        os.makedirs('instance/logs')
    
    db_version = DatabaseVersioning()
    return db_version.create_snapshot(description)

if __name__ == "__main__":
    create_db_snapshot("Initial database version") 