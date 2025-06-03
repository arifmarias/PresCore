"""
MedScript Pro - Database Configuration and Connection Management
This file handles SQLite database connections, configuration, and connection pooling.
"""

import sqlite3
import os
import threading
import time
from contextlib import contextmanager
from typing import Optional, Any, Dict, List, Tuple
import streamlit as st
from config.settings import DATABASE_PATH, DATABASE_NAME

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.database_path = DATABASE_PATH
        self.connection_timeout = 30
        self.check_same_thread = False
        self.isolation_level = None  # Autocommit mode
        self.row_factory = sqlite3.Row  # Enable column access by name
        self._lock = threading.Lock()
        
    def get_connection_params(self) -> Dict[str, Any]:
        """Get database connection parameters"""
        return {
            'database': self.database_path,
            'timeout': self.connection_timeout,
            'check_same_thread': self.check_same_thread,
            'isolation_level': self.isolation_level
        }

# Global database configuration instance
db_config = DatabaseConfig()

def get_connection() -> sqlite3.Connection:
    """
    Get a new database connection with proper configuration
    
    Returns:
        sqlite3.Connection: Configured database connection
    """
    try:
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_config.database_path), exist_ok=True)
        
        # Create connection with configuration
        conn = sqlite3.connect(**db_config.get_connection_params())
        
        # Set row factory for named column access
        conn.row_factory = sqlite3.Row
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set journal mode for better performance
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Set synchronous mode for better performance
        conn.execute("PRAGMA synchronous = NORMAL")
        
        # Set cache size for better performance
        conn.execute("PRAGMA cache_size = 10000")
        
        # Set temp store in memory
        conn.execute("PRAGMA temp_store = MEMORY")
        
        return conn
        
    except sqlite3.Error as e:
        st.error(f"Database connection error: {str(e)}")
        raise
    except Exception as e:
        st.error(f"Unexpected error connecting to database: {str(e)}")
        raise

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Ensures proper connection cleanup
    
    Yields:
        sqlite3.Connection: Database connection
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: Optional[Tuple] = None, fetch: str = 'none') -> Any:
    """
    Execute a database query with proper error handling
    
    Args:
        query (str): SQL query to execute
        params (Optional[Tuple]): Query parameters
        fetch (str): Fetch mode - 'one', 'all', or 'none'
    
    Returns:
        Any: Query result based on fetch mode
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Handle different fetch modes
            if fetch == 'one':
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch == 'all':
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return cursor.lastrowid
                
        except sqlite3.Error as e:
            conn.rollback()
            st.error(f"Database query error: {str(e)}")
            raise
        except Exception as e:
            conn.rollback()
            st.error(f"Unexpected error executing query: {str(e)}")
            raise

def execute_many(query: str, params_list: List[Tuple]) -> int:
    """
    Execute multiple queries with the same statement
    
    Args:
        query (str): SQL query to execute
        params_list (List[Tuple]): List of parameter tuples
    
    Returns:
        int: Number of affected rows
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
            
        except sqlite3.Error as e:
            conn.rollback()
            st.error(f"Database executemany error: {str(e)}")
            raise
        except Exception as e:
            conn.rollback()
            st.error(f"Unexpected error executing multiple queries: {str(e)}")
            raise

def check_database_exists() -> bool:
    """
    Check if the database file exists
    
    Returns:
        bool: True if database exists, False otherwise
    """
    return os.path.exists(db_config.database_path)

def get_database_info() -> Dict[str, Any]:
    """
    Get database information and statistics
    
    Returns:
        Dict[str, Any]: Database information
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get database file size
            file_size = os.path.getsize(db_config.database_path) if check_database_exists() else 0
            
            # Get number of tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Get database version
            cursor.execute("PRAGMA user_version")
            db_version = cursor.fetchone()[0]
            
            # Get page count and size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            return {
                'file_path': db_config.database_path,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'table_count': table_count,
                'db_version': db_version,
                'page_count': page_count,
                'page_size': page_size,
                'total_pages_size': page_count * page_size
            }
            
    except Exception as e:
        st.error(f"Error getting database info: {str(e)}")
        return {}

def test_database_connection() -> bool:
    """
    Test database connection and basic operations
    
    Returns:
        bool: True if connection test successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            # Test foreign keys are enabled
            cursor.execute("PRAGMA foreign_keys")
            fk_enabled = cursor.fetchone()[0]
            
            return result[0] == 1 and fk_enabled == 1
            
    except Exception as e:
        st.error(f"Database connection test failed: {str(e)}")
        return False

def backup_database(backup_path: Optional[str] = None) -> bool:
    """
    Create a backup of the database
    
    Args:
        backup_path (Optional[str]): Path for backup file
    
    Returns:
        bool: True if backup successful, False otherwise
    """
    try:
        if not backup_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = f"{DATABASE_NAME.replace('.db', '')}_{timestamp}.db"
        
        with get_db_connection() as conn:
            # Create backup connection
            backup_conn = sqlite3.connect(backup_path)
            
            # Perform backup
            conn.backup(backup_conn)
            backup_conn.close()
            
            return True
            
    except Exception as e:
        st.error(f"Database backup failed: {str(e)}")
        return False

def vacuum_database() -> bool:
    """
    Vacuum the database to reclaim space and optimize performance
    
    Returns:
        bool: True if vacuum successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            conn.execute("VACUUM")
            return True
            
    except Exception as e:
        st.error(f"Database vacuum failed: {str(e)}")
        return False

def get_table_info(table_name: str) -> List[Dict[str, Any]]:
    """
    Get information about a specific table
    
    Args:
        table_name (str): Name of the table
    
    Returns:
        List[Dict[str, Any]]: Table column information
    """
    try:
        query = f"PRAGMA table_info({table_name})"
        return execute_query(query, fetch='all')
        
    except Exception as e:
        st.error(f"Error getting table info for {table_name}: {str(e)}")
        return []

def get_all_tables() -> List[str]:
    """
    Get list of all tables in the database
    
    Returns:
        List[str]: List of table names
    """
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = execute_query(query, fetch='all')
        return [row['name'] for row in results]
        
    except Exception as e:
        st.error(f"Error getting table list: {str(e)}")
        return []

def get_table_row_count(table_name: str) -> int:
    """
    Get the number of rows in a table
    
    Args:
        table_name (str): Name of the table
    
    Returns:
        int: Number of rows in the table
    """
    try:
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = execute_query(query, fetch='one')
        return result['count'] if result else 0
        
    except Exception as e:
        st.error(f"Error getting row count for {table_name}: {str(e)}")
        return 0

def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database
    
    Args:
        table_name (str): Name of the table to check
    
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = execute_query(query, (table_name,), fetch='one')
        return result is not None
        
    except Exception as e:
        st.error(f"Error checking if table {table_name} exists: {str(e)}")
        return False

def execute_transaction(queries_and_params: List[Tuple[str, Optional[Tuple]]]) -> bool:
    """
    Execute multiple queries in a single transaction
    
    Args:
        queries_and_params (List[Tuple[str, Optional[Tuple]]]): List of (query, params) tuples
    
    Returns:
        bool: True if transaction successful, False otherwise
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Execute all queries
            for query, params in queries_and_params:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            
            # Commit transaction
            conn.commit()
            return True
            
        except Exception as e:
            # Rollback on error
            conn.rollback()
            st.error(f"Transaction failed: {str(e)}")
            return False

def get_database_stats() -> Dict[str, Any]:
    """
    Get comprehensive database statistics
    
    Returns:
        Dict[str, Any]: Database statistics
    """
    try:
        stats = {}
        
        # Get basic info
        stats.update(get_database_info())
        
        # Get table statistics
        tables = get_all_tables()
        stats['tables'] = {}
        
        total_rows = 0
        for table in tables:
            row_count = get_table_row_count(table)
            stats['tables'][table] = row_count
            total_rows += row_count
        
        stats['total_rows'] = total_rows
        
        return stats
        
    except Exception as e:
        st.error(f"Error getting database statistics: {str(e)}")
        return {}

# Connection pool for better performance (simple implementation)
class ConnectionPool:
    """Simple connection pool implementation"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool"""
        with self.lock:
            if self.connections:
                return self.connections.pop()
            else:
                return get_connection()
    
    def return_connection(self, conn: sqlite3.Connection) -> None:
        """Return a connection to the pool"""
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                conn.close()
    
    def close_all(self) -> None:
        """Close all connections in the pool"""
        with self.lock:
            for conn in self.connections:
                conn.close()
            self.connections.clear()

# Global connection pool
connection_pool = ConnectionPool()

@contextmanager
def get_pooled_connection():
    """
    Context manager for pooled database connections
    
    Yields:
        sqlite3.Connection: Database connection from pool
    """
    conn = connection_pool.get_connection()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise
    finally:
        connection_pool.return_connection(conn)

# Utility function for streamlit caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_table_data(table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get table data with caching for better performance
    
    Args:
        table_name (str): Name of the table
        limit (Optional[int]): Limit number of rows
    
    Returns:
        List[Dict[str, Any]]: Table data
    """
    try:
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        return execute_query(query, fetch='all')
        
    except Exception as e:
        st.error(f"Error getting cached data for {table_name}: {str(e)}")
        return []