import os
import logging
import json
from datetime import datetime
from sqlalchemy import event, inspect
from sqlalchemy.engine import Engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instance/logs/db_events.log'
)

class DbEventLogger:
    def __init__(self, db, log_file='instance/db_logs/db_operations.json'):
        self.db = db
        self.log_file = log_file
        self.operations = self.load_operations()
        self.ensure_log_dir()
        self.setup_event_listeners()
    
    def ensure_log_dir(self):
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def load_operations(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'operations': []}
        return {'operations': []}
    
    def save_operations(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.operations, f, indent=4)
    
    def log_operation(self, operation_type, table_name, record_id=None, details=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        operation = {
            'timestamp': timestamp,
            'type': operation_type,
            'table': table_name,
        }
        
        if record_id is not None:
            operation['record_id'] = record_id
            
        if details is not None:
            operation['details'] = details
        
        self.operations['operations'].append(operation)
        self.save_operations()
        
        # Also log to regular log file
        log_message = f"DB {operation_type.upper()}: {table_name}"
        if record_id is not None:
            log_message += f" ID: {record_id}"
        logging.info(log_message)
    
    def setup_event_listeners(self):
        # Listen for before_commit events
        @event.listens_for(self.db.session, 'before_commit')
        def before_commit(session):
            for obj in session.new:
                table_name = obj.__tablename__ if hasattr(obj, '__tablename__') else str(obj.__class__.__name__)
                record_id = getattr(obj, 'id', None)
                # Get object attributes
                insp = inspect(obj)
                attrs = {}
                for attr in insp.attrs:
                    if not attr.key.startswith('_'):
                        attrs[attr.key] = str(getattr(obj, attr.key))
                
                self.log_operation('insert', table_name, record_id, attrs)
            
            for obj in session.dirty:
                if not session.is_modified(obj):
                    continue
                    
                table_name = obj.__tablename__ if hasattr(obj, '__tablename__') else str(obj.__class__.__name__)
                record_id = getattr(obj, 'id', None)
                
                # Get changed attributes
                insp = inspect(obj)
                changes = {}
                for attr in insp.attrs:
                    if not attr.key.startswith('_') and session.is_modified(obj, include_collections=False):
                        hist = attr.history
                        if hist.has_changes():
                            changes[attr.key] = {
                                'old': str(hist.deleted[0]) if hist.deleted else None,
                                'new': str(hist.added[0]) if hist.added else None
                            }
                
                self.log_operation('update', table_name, record_id, changes)
            
            for obj in session.deleted:
                table_name = obj.__tablename__ if hasattr(obj, '__tablename__') else str(obj.__class__.__name__)
                record_id = getattr(obj, 'id', None)
                self.log_operation('delete', table_name, record_id)
        
        # Listen for after_commit events
        @event.listens_for(self.db.session, 'after_commit')
        def after_commit(session):
            logging.info("Transaction committed")
        
        # Listen for after_rollback events
        @event.listens_for(self.db.session, 'after_rollback')
        def after_rollback(session):
            logging.info("Transaction rolled back")

        # Listen for SQL statements
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(datetime.now())
            
            if statement.strip().upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE')):
                log_message = f"SQL: {statement}"
                if not executemany and parameters:
                    log_message += f" Parameters: {parameters}"
                logging.debug(log_message)
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            start_time = conn.info['query_start_time'].pop(-1)
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.debug(f"Execution time: {execution_time:.6f}s")

def setup_db_event_logging(app, db):
    """Initialize the database event logger for the Flask app"""
    # Ensure logs directory exists
    if not os.path.exists('instance/logs'):
        os.makedirs('instance/logs')
    
    # Register the event logger with the app
    with app.app_context():
        event_logger = DbEventLogger(db)
        
    # Store it on the app for future reference
    app.db_event_logger = event_logger
    
    return event_logger 