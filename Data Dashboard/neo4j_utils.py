from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, ClientError
import os
from typing import Optional, List, Dict, Any, Tuple, Union
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Neo4j database connection manager with utility methods."""
    
    def __init__(self, uri: str = 'bolt://localhost:7687', 
                 username: str = 'neo4j', password: str = 'password',
                 database: str = 'neo4j'):
        """
        Initialize Neo4j connection parameters.
        
        Args:
            uri: Neo4j server URI (bolt://host:port)
            username: Neo4j username
            password: Neo4j password
            database: Database name (default: neo4j)
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver = None
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            
            # Test the connection
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
            return True
            
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Error connecting to Neo4j: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            
        Returns:
            List of dictionaries containing query results or None if error
        """
        if not self.driver:
            if not self.connect():
                return None
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                records = [dict(record) for record in result]
                logger.info(f"Query executed successfully, returned {len(records)} records")
                return records
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None
    
    def execute_write_query(self, query: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Execute a write Cypher query (CREATE, UPDATE, DELETE, MERGE).
        
        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.driver:
            if not self.connect():
                return False
        
        try:
            with self.driver.session(database=self.database) as session:
                with session.begin_transaction() as tx:
                    result = tx.run(query, parameters or {})
                    tx.commit()
                logger.info("Write query executed successfully")
                return True
        except Exception as e:
            logger.error(f"Error executing write query: {e}")
            return False
    
    def create_node(self, labels: List[str], properties: Dict[str, Any]) -> Optional[str]:
        """
        Create a node with specified labels and properties.
        
        Args:
            labels: List of labels for the node
            properties: Node properties
            
        Returns:
            Node ID as string or None if error
        """
        labels_str = ':'.join(labels) if labels else ''
        properties_str = ', '.join([f"{k}: ${k}" for k in properties.keys()])
        
        query = f"CREATE (n:{labels_str} {{{properties_str}}}) RETURN id(n) as node_id"
        
        result = self.execute_query(query, properties)
        if result and len(result) > 0:
            return str(result[0]['node_id'])
        return None
    
    def create_relationship(self, from_node_id: str, to_node_id: str, 
                          relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """
        Create a relationship between two nodes.
        
        Args:
            from_node_id: ID of the source node
            to_node_id: ID of the target node
            relationship_type: Type of relationship
            properties: Relationship properties (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        properties = properties or {}
        properties_str = ', '.join([f"{k}: ${k}" for k in properties.keys()]) if properties else ''
        
        if properties_str:
            query = f"""
            MATCH (a), (b) 
            WHERE id(a) = $from_id AND id(b) = $to_id 
            CREATE (a)-[r:{relationship_type} {{{properties_str}}}]->(b) 
            RETURN r
            """
        else:
            query = f"""
            MATCH (a), (b) 
            WHERE id(a) = $from_id AND id(b) = $to_id 
            CREATE (a)-[r:{relationship_type}]->(b) 
            RETURN r
            """
        
        parameters = {'from_id': int(from_node_id), 'to_id': int(to_node_id), **properties}
        return self.execute_write_query(query, parameters)
    
    def find_nodes(self, labels: List[str] = None, properties: Dict[str, Any] = None, 
                  limit: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        Find nodes with specified labels and properties.
        
        Args:
            labels: List of labels to filter by (optional)
            properties: Properties to filter by (optional)
            limit: Maximum number of nodes to return
            
        Returns:
            List of node dictionaries or None if error
        """
        labels_str = ':'.join(labels) if labels else 'n'
        properties_str = ' AND '.join([f"n.{k} = ${k}" for k in properties.keys()]) if properties else ''
        
        query = f"MATCH (n:{labels_str})"
        if properties_str:
            query += f" WHERE {properties_str}"
        query += " RETURN n"
        if limit > 0:
            query += f" LIMIT {limit}"
        
        result = self.execute_query(query, properties or {})
        if result:
            return [dict(record['n']) for record in result]
        return None
    
    def find_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a node by its ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node dictionary or None if not found
        """
        query = "MATCH (n) WHERE id(n) = $node_id RETURN n"
        result = self.execute_query(query, {'node_id': int(node_id)})
        if result and len(result) > 0:
            return dict(result[0]['n'])
        return None
    
    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update node properties.
        
        Args:
            node_id: Node ID
            properties: New properties
            
        Returns:
            bool: True if successful, False otherwise
        """
        properties_str = ', '.join([f"n.{k} = ${k}" for k in properties.keys()])
        query = f"MATCH (n) WHERE id(n) = $node_id SET {properties_str} RETURN n"
        
        parameters = {'node_id': int(node_id), **properties}
        result = self.execute_query(query, parameters)
        return result is not None and len(result) > 0
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and its relationships.
        
        Args:
            node_id: Node ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "MATCH (n) WHERE id(n) = $node_id DETACH DELETE n"
        return self.execute_write_query(query, {'node_id': int(node_id)})
    
    def find_relationships(self, from_node_id: str = None, to_node_id: str = None,
                         relationship_type: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        Find relationships between nodes.
        
        Args:
            from_node_id: Source node ID (optional)
            to_node_id: Target node ID (optional)
            relationship_type: Type of relationship (optional)
            
        Returns:
            List of relationship dictionaries or None if error
        """
        query = "MATCH (a)-[r]->(b)"
        conditions = []
        parameters = {}
        
        if from_node_id:
            conditions.append("id(a) = $from_id")
            parameters['from_id'] = int(from_node_id)
        
        if to_node_id:
            conditions.append("id(b) = $to_id")
            parameters['to_id'] = int(to_node_id)
        
        if relationship_type:
            conditions.append(f"type(r) = '{relationship_type}'")
        
        if conditions:
            query += f" WHERE {' AND '.join(conditions)}"
        
        query += " RETURN a, r, b"
        
        result = self.execute_query(query, parameters)
        if result:
            return [
                {
                    'from_node': dict(record['a']),
                    'relationship': dict(record['r']),
                    'to_node': dict(record['b'])
                }
                for record in result
            ]
        return None
    
    def get_node_count(self, labels: List[str] = None) -> Optional[int]:
        """
        Get the count of nodes with specified labels.
        
        Args:
            labels: List of labels to count (optional)
            
        Returns:
            Number of nodes or None if error
        """
        labels_str = ':'.join(labels) if labels else 'n'
        query = f"MATCH (n:{labels_str}) RETURN count(n) as count"
        
        result = self.execute_query(query)
        if result and len(result) > 0:
            return result[0]['count']
        return None
    
    def get_relationship_count(self, relationship_type: str = None) -> Optional[int]:
        """
        Get the count of relationships.
        
        Args:
            relationship_type: Type of relationship to count (optional)
            
        Returns:
            Number of relationships or None if error
        """
        if relationship_type:
            query = f"MATCH ()-[r:{relationship_type}]->() RETURN count(r) as count"
        else:
            query = "MATCH ()-[r]->() RETURN count(r) as count"
        
        result = self.execute_query(query)
        if result and len(result) > 0:
            return result[0]['count']
        return None
    
    def get_labels(self) -> Optional[List[str]]:
        """
        Get all node labels in the database.
        
        Returns:
            List of label names or None if error
        """
        query = "CALL db.labels() YIELD label RETURN label"
        result = self.execute_query(query)
        if result:
            return [record['label'] for record in result]
        return None
    
    def get_relationship_types(self) -> Optional[List[str]]:
        """
        Get all relationship types in the database.
        
        Returns:
            List of relationship type names or None if error
        """
        query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
        result = self.execute_query(query)
        if result:
            return [record['relationshipType'] for record in result]
        return None
    
    def create_index(self, label: str, property_name: str) -> bool:
        """
        Create an index on a node label and property.
        
        Args:
            label: Node label
            property_name: Property name to index
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = f"CREATE INDEX FOR (n:{label}) ON (n.{property_name})"
        return self.execute_write_query(query)
    
    def create_constraint(self, label: str, property_name: str, constraint_type: str = "UNIQUE") -> bool:
        """
        Create a constraint on a node label and property.
        
        Args:
            label: Node label
            property_name: Property name
            constraint_type: Type of constraint (UNIQUE, EXISTS, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if constraint_type.upper() == "UNIQUE":
            query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
        elif constraint_type.upper() == "EXISTS":
            query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property_name} IS NOT NULL"
        else:
            logger.error(f"Unsupported constraint type: {constraint_type}")
            return False
        
        return self.execute_write_query(query)
    
    def clear_database(self) -> bool:
        """
        Clear all nodes and relationships from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        query = "MATCH (n) DETACH DELETE n"
        return self.execute_write_query(query)
    
    def get_database_info(self) -> Optional[Dict[str, Any]]:
        """
        Get database information.
        
        Returns:
            Dictionary with database info or None if error
        """
        info = {}
        
        # Get node count
        node_count = self.get_node_count()
        if node_count is not None:
            info['node_count'] = node_count
        
        # Get relationship count
        rel_count = self.get_relationship_count()
        if rel_count is not None:
            info['relationship_count'] = rel_count
        
        # Get labels
        labels = self.get_labels()
        if labels is not None:
            info['labels'] = labels
        
        # Get relationship types
        rel_types = self.get_relationship_types()
        if rel_types is not None:
            info['relationship_types'] = rel_types
        
        return info if info else None


def create_connection_from_env() -> Optional[Neo4jConnection]:
    """
    Create Neo4j connection using environment variables.
    
    Environment variables expected:
    - NEO4J_URI
    - NEO4J_USERNAME
    - NEO4J_PASSWORD
    - NEO4J_DATABASE (optional)
    
    Returns:
        Neo4jConnection object or None if environment variables are missing
    """
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    if not username or not password:
        logger.error("Missing required environment variables for Neo4j connection")
        return None
    
    return Neo4jConnection(uri, username, password, database)


def test_connection(connection: Neo4jConnection) -> bool:
    """
    Test if the Neo4j connection is working.
    
    Args:
        connection: Neo4jConnection object
        
    Returns:
        bool: True if connection test successful, False otherwise
    """
    try:
        if connection.connect():
            # Test with a simple query
            result = connection.execute_query("RETURN 1 as test")
            connection.disconnect()
            return result is not None and len(result) > 0
        return False
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
