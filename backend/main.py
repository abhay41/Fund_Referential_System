from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Fund Referential API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j connection
class Neo4jConnection:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

db = Neo4jConnection()

@app.get("/")
def read_root():
    return {"message": "Fund Referential API"}

@app.get("/funds/{fund_id}")
def get_fund(fund_id: str):
    """Get fund details by ID"""
    query = """
    MATCH (f:Fund {id: $fund_id})
    RETURN f
    """
    result = db.query(query, {"fund_id": fund_id})
    if not result:
        raise HTTPException(status_code=404, detail="Fund not found")
    return result[0]

@app.get("/funds/{fund_id}/hierarchy")
def get_fund_hierarchy(fund_id: str, direction: str = "children", levels: int = 1):
    """Get fund hierarchy (children or parents) up to specified levels"""
    if direction not in ["children", "parents"]:
        raise HTTPException(status_code=400, detail="Invalid direction")
    
    if direction == "children":
        query = """
        MATCH (f:Fund {id: $fund_id})-[r:HAS_SUBFUND*1..${levels}]->(child)
        RETURN f, r, child
        """
    else:
        query = """
        MATCH (f:Fund {id: $fund_id})<-[r:HAS_SUBFUND*1..${levels}]-(parent)
        RETURN f, r, parent
        """
    
    result = db.query(query, {"fund_id": fund_id, "levels": levels})
    return result

@app.get("/funds/management/{mgmt_id}")
def get_funds_by_management(mgmt_id: str):
    """Get all funds managed by a specific management entity"""
    query = """
    MATCH (m:ManagementEntity {id: $mgmt_id})-[:MANAGES]->(f:Fund)
    RETURN f
    """
    result = db.query(query, {"mgmt_id": mgmt_id})
    return result

@app.on_event("shutdown")
def shutdown_event():
    db.close()