from neo4j import GraphDatabase
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.validate_connection()

    def validate_connection(self):
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) RETURN count(n) AS count LIMIT 1")
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {str(e)}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> list:
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            logger.error(f"Full error details: ", exc_info=True)
            raise Exception(f"Database error: {str(e)}")

    def create_constraints(self):
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (m:ManagementEntity) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Fund) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:SubFund) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:LegalEntity) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (sc:ShareClass) REQUIRE sc.id IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint}")
                except Exception as e:
                    logger.error(f"Failed to create constraint: {str(e)}")
                    logger.error(f"Constraint: {constraint}")
                    raise
    
    def get_session(self):
        """Get a new Neo4j session"""
        if not self.driver:
            raise Exception("Driver not initialized. Call connect() first.")
        return self.driver.session()
    
    def connect(self):
        """Connect to Neo4j (for compatibility with main.py)"""
        # Connection is already established in __init__, but verify it
        self.validate_connection()


# Global connection instance - will be initialized in main.py
neo4j_conn = None


def initialize_connection():
    """Initialize the global Neo4j connection"""
    global neo4j_conn
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    neo4j_conn = Neo4jConnection(uri=uri, user=user, password=password)
    return neo4j_conn


def get_db():
    """Dependency for getting database session"""
    session = neo4j_conn.get_session()
    try:
        yield session
    finally:
        session.close()