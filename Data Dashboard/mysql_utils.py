import mysql.connector
from mysql.connector import Error
import os
from typing import Optional, List, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MySQLConnection:
    """MySQL database connection manager with utility methods."""
    
    def __init__(self, host: str = 'localhost', port: int = 3306, 
                 database: str = None, user: str = None, password: str = None):
        """
        Initialize MySQL connection parameters.
        
        Args:
            host: MySQL server hostname
            port: MySQL server port
            database: Database name
            user: MySQL username
            password: MySQL password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establish connection to MySQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                autocommit=True
            )
            
            if self.connection.is_connected():
                logger.info(f"Successfully connected to MySQL database: {self.database}")
                return True
                
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            return False
            
        return False
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed.")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Tuple]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of tuples containing query results, or None if error
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
                
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except Error as e:
            logger.error(f"Error executing query: {e}")
            return None
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            logger.error(f"Error executing update: {e}")
            return False
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """
        Execute multiple INSERT, UPDATE, or DELETE queries.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            logger.error(f"Error executing batch update: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get information about table columns.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of dictionaries containing column information
        """
        query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        
        results = self.execute_query(query, (self.database, table_name))
        if results:
            columns = []
            for row in results:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2],
                    'default': row[3],
                    'key': row[4]
                })
            return columns
        return None
    
    def get_tables(self) -> Optional[List[str]]:
        """
        Get list of all tables in the database.
        
        Returns:
            List of table names
        """
        query = "SHOW TABLES"
        results = self.execute_query(query)
        if results:
            return [row[0] for row in results]
        return None
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        query = """
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        
        results = self.execute_query(query, (self.database, table_name))
        if results:
            return results[0][0] > 0
        return False
    
    def get_row_count(self, table_name: str) -> Optional[int]:
        """
        Get the number of rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows, or None if error
        """
        query = f"SELECT COUNT(*) FROM {table_name}"
        results = self.execute_query(query)
        if results:
            return results[0][0]
        return None


def create_connection_from_env() -> Optional[MySQLConnection]:
    """
    Create MySQL connection using environment variables.
    
    Environment variables expected:
    - MYSQL_HOST
    - MYSQL_PORT
    - MYSQL_DATABASE
    - MYSQL_USER
    - MYSQL_PASSWORD
    
    Returns:
        MySQLConnection object or None if environment variables are missing
    """
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', '3306'))
    database = os.getenv('MYSQL_DATABASE')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    
    if not all([database, user, password]):
        logger.error("Missing required environment variables for MySQL connection")
        return None
    
    return MySQLConnection(host, port, database, user, password)


def test_connection(connection: MySQLConnection) -> bool:
    """
    Test if the MySQL connection is working.
    
    Args:
        connection: MySQLConnection object
        
    Returns:
        bool: True if connection test successful, False otherwise
    """
    try:
        if connection.connect():
            # Test with a simple query
            result = connection.execute_query("SELECT 1")
            connection.disconnect()
            return result is not None and len(result) > 0
        return False
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
