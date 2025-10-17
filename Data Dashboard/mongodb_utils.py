from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
from pymongo.database import Database
from pymongo.collection import Collection
import os
from typing import Optional, List, Dict, Any, Union
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBConnection:
    """MongoDB database connection manager with utility methods."""
    
    def __init__(self, host: str = 'localhost', port: int = 27017, 
                 database: str = None, username: str = None, password: str = None,
                 auth_source: str = 'admin', auth_mechanism: str = 'SCRAM-SHA-256'):
        """
        Initialize MongoDB connection parameters.
        
        Args:
            host: MongoDB server hostname
            port: MongoDB server port
            database: Database name
            username: MongoDB username (optional for authentication)
            password: MongoDB password (optional for authentication)
            auth_source: Authentication database
            auth_mechanism: Authentication mechanism
        """
        self.host = host
        self.port = port
        self.database_name = database
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.auth_mechanism = auth_mechanism
        self.client = None
        self.database = None
        
    def connect(self) -> bool:
        """
        Establish connection to MongoDB database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Build connection string
            if self.username and self.password:
                connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.auth_source}?authMechanism={self.auth_mechanism}"
            else:
                connection_string = f"mongodb://{self.host}:{self.port}"
            
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Test the connection
            self.client.admin.command('ping')
            
            if self.database_name:
                self.database = self.client[self.database_name]
            
            logger.info(f"Successfully connected to MongoDB at {self.host}:{self.port}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
    
    def get_database(self, database_name: str = None) -> Optional[Database]:
        """
        Get a database instance.
        
        Args:
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Database object or None if connection failed
        """
        if not self.client:
            if not self.connect():
                return None
        
        db_name = database_name or self.database_name
        if not db_name:
            logger.error("No database name specified")
            return None
        
        return self.client[db_name]
    
    def get_collection(self, collection_name: str, database_name: str = None) -> Optional[Collection]:
        """
        Get a collection instance.
        
        Args:
            collection_name: Name of the collection
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Collection object or None if connection failed
        """
        database = self.get_database(database_name)
        if not database:
            return None
        
        return database[collection_name]
    
    def insert_document(self, collection_name: str, document: Dict[str, Any], 
                       database_name: str = None) -> Optional[str]:
        """
        Insert a single document into a collection.
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            ObjectId of inserted document or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            result = collection.insert_one(document)
            logger.info(f"Document inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error inserting document: {e}")
            return None
    
    def insert_many_documents(self, collection_name: str, documents: List[Dict[str, Any]], 
                             database_name: str = None) -> Optional[List[str]]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to insert
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            List of ObjectIds of inserted documents or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            result = collection.insert_many(documents)
            logger.info(f"{len(result.inserted_ids)} documents inserted")
            return [str(oid) for oid in result.inserted_ids]
        except PyMongoError as e:
            logger.error(f"Error inserting documents: {e}")
            return None
    
    def find_documents(self, collection_name: str, filter_dict: Dict[str, Any] = None,
                      projection: Dict[str, Any] = None, limit: int = 0,
                      database_name: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        Find documents in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria (default: find all)
            projection: Fields to include/exclude
            limit: Maximum number of documents to return
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            List of documents or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            cursor = collection.find(filter_dict or {}, projection or {})
            if limit > 0:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            logger.info(f"Found {len(documents)} documents")
            return documents
        except PyMongoError as e:
            logger.error(f"Error finding documents: {e}")
            return None
    
    def find_one_document(self, collection_name: str, filter_dict: Dict[str, Any] = None,
                         projection: Dict[str, Any] = None,
                         database_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Find a single document in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria (default: find first)
            projection: Fields to include/exclude
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Document or None if not found or error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            document = collection.find_one(filter_dict or {}, projection or {})
            if document:
                logger.info("Document found")
            else:
                logger.info("No document found")
            return document
        except PyMongoError as e:
            logger.error(f"Error finding document: {e}")
            return None
    
    def update_document(self, collection_name: str, filter_dict: Dict[str, Any],
                       update_dict: Dict[str, Any], upsert: bool = False,
                       database_name: str = None) -> Optional[int]:
        """
        Update a single document in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria to find document
            update_dict: Update operations
            upsert: Create document if it doesn't exist
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Number of documents modified or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            result = collection.update_one(filter_dict, update_dict, upsert=upsert)
            logger.info(f"Modified {result.modified_count} document(s)")
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"Error updating document: {e}")
            return None
    
    def update_many_documents(self, collection_name: str, filter_dict: Dict[str, Any],
                             update_dict: Dict[str, Any], upsert: bool = False,
                             database_name: str = None) -> Optional[int]:
        """
        Update multiple documents in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria to find documents
            update_dict: Update operations
            upsert: Create document if it doesn't exist
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Number of documents modified or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            result = collection.update_many(filter_dict, update_dict, upsert=upsert)
            logger.info(f"Modified {result.modified_count} document(s)")
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"Error updating documents: {e}")
            return None
    
    def delete_document(self, collection_name: str, filter_dict: Dict[str, Any],
                       database_name: str = None) -> Optional[int]:
        """
        Delete a single document from a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria to find document
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Number of documents deleted or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            result = collection.delete_one(filter_dict)
            logger.info(f"Deleted {result.deleted_count} document(s)")
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"Error deleting document: {e}")
            return None
    
    def delete_many_documents(self, collection_name: str, filter_dict: Dict[str, Any],
                             database_name: str = None) -> Optional[int]:
        """
        Delete multiple documents from a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria to find documents
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Number of documents deleted or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            result = collection.delete_many(filter_dict)
            logger.info(f"Deleted {result.deleted_count} document(s)")
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"Error deleting documents: {e}")
            return None
    
    def get_collections(self, database_name: str = None) -> Optional[List[str]]:
        """
        Get list of all collections in a database.
        
        Args:
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            List of collection names or None if error
        """
        database = self.get_database(database_name)
        if not database:
            return None
        
        try:
            collections = database.list_collection_names()
            logger.info(f"Found {len(collections)} collections")
            return collections
        except PyMongoError as e:
            logger.error(f"Error getting collections: {e}")
            return None
    
    def get_databases(self) -> Optional[List[str]]:
        """
        Get list of all databases.
        
        Returns:
            List of database names or None if error
        """
        if not self.client:
            if not self.connect():
                return None
        
        try:
            databases = self.client.list_database_names()
            logger.info(f"Found {len(databases)} databases")
            return databases
        except PyMongoError as e:
            logger.error(f"Error getting databases: {e}")
            return None
    
    def collection_exists(self, collection_name: str, database_name: str = None) -> bool:
        """
        Check if a collection exists in a database.
        
        Args:
            collection_name: Name of the collection to check
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            bool: True if collection exists, False otherwise
        """
        collections = self.get_collections(database_name)
        if collections:
            return collection_name in collections
        return False
    
    def get_document_count(self, collection_name: str, filter_dict: Dict[str, Any] = None,
                          database_name: str = None) -> Optional[int]:
        """
        Get the number of documents in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria (optional)
            database_name: Name of the database (uses default if not specified)
            
        Returns:
            Number of documents or None if error
        """
        collection = self.get_collection(collection_name, database_name)
        if not collection:
            return None
        
        try:
            count = collection.count_documents(filter_dict or {})
            logger.info(f"Collection {collection_name} has {count} documents")
            return count
        except PyMongoError as e:
            logger.error(f"Error counting documents: {e}")
            return None


def create_connection_from_env() -> Optional[MongoDBConnection]:
    """
    Create MongoDB connection using environment variables.
    
    Environment variables expected:
    - MONGODB_HOST
    - MONGODB_PORT
    - MONGODB_DATABASE
    - MONGODB_USERNAME (optional)
    - MONGODB_PASSWORD (optional)
    - MONGODB_AUTH_SOURCE (optional)
    
    Returns:
        MongoDBConnection object or None if environment variables are missing
    """
    host = os.getenv('MONGODB_HOST', 'localhost')
    port = int(os.getenv('MONGODB_PORT', '27017'))
    database = os.getenv('MONGODB_DATABASE')
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PASSWORD')
    auth_source = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    
    if not database:
        logger.error("Missing required environment variable MONGODB_DATABASE")
        return None
    
    return MongoDBConnection(host, port, database, username, password, auth_source)


def test_connection(connection: MongoDBConnection) -> bool:
    """
    Test if the MongoDB connection is working.
    
    Args:
        connection: MongoDBConnection object
        
    Returns:
        bool: True if connection test successful, False otherwise
    """
    try:
        if connection.connect():
            # Test with a simple command
            connection.client.admin.command('ping')
            connection.disconnect()
            return True
        return False
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
