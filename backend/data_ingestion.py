import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

class DataIngestion:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            # Create constraints for uniqueness
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (m:ManagementEntity) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Fund) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:SubFund) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (l:LegalEntity) REQUIRE l.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (sc:ShareClass) REQUIRE sc.id IS UNIQUE"
            ]
            for constraint in constraints:
                session.run(constraint)

    def ingest_management_entities(self, file_path):
        df = pd.read_csv(file_path)
        with self.driver.session() as session:
            for _, row in df.iterrows():
                query = """
                MERGE (m:ManagementEntity {id: $id})
                SET m += $properties
                """
                session.run(query, {
                    "id": row["id"],
                    "properties": row.to_dict()
                })

    def ingest_funds(self, file_path):
        df = pd.read_csv(file_path)
        with self.driver.session() as session:
            for _, row in df.iterrows():
                query = """
                MERGE (f:Fund {id: $id})
                SET f += $properties
                WITH f
                MATCH (m:ManagementEntity {id: $mgmt_id})
                MERGE (m)-[:MANAGES]->(f)
                """
                session.run(query, {
                    "id": row["id"],
                    "mgmt_id": row["management_entity_id"],
                    "properties": row.to_dict()
                })

    def ingest_subfunds(self, file_path):
        df = pd.read_csv(file_path)
        with self.driver.session() as session:
            for _, row in df.iterrows():
                query = """
                MERGE (s:SubFund {id: $id})
                SET s += $properties
                WITH s
                MATCH (f:Fund {id: $fund_id})
                MERGE (f)-[:HAS_SUBFUND]->(s)
                """
                session.run(query, {
                    "id": row["id"],
                    "fund_id": row["master_fund_id"],
                    "properties": row.to_dict()
                })

    def ingest_legal_entities(self, file_path):
        df = pd.read_csv(file_path)
        with self.driver.session() as session:
            for _, row in df.iterrows():
                query = """
                MERGE (l:LegalEntity {id: $id})
                SET l += $properties
                """
                session.run(query, {
                    "id": row["id"],
                    "properties": row.to_dict()
                })

    def ingest_share_classes(self, file_path):
        df = pd.read_csv(file_path)
        with self.driver.session() as session:
            for _, row in df.iterrows():
                query = """
                MERGE (sc:ShareClass {id: $id})
                SET sc += $properties
                WITH sc
                MATCH (f:Fund {id: $fund_id})
                MERGE (f)-[:HAS_SHARE_CLASS]->(sc)
                """
                session.run(query, {
                    "id": row["id"],
                    "fund_id": row["fund_id"],
                    "properties": row.to_dict()
                })

def main():
    ingestion = DataIngestion()
    
    try:
        print("Creating constraints...")
        ingestion.create_constraints()

        print("Ingesting management entities...")
        ingestion.ingest_management_entities("data/management_entities.csv")

        print("Ingesting funds...")
        ingestion.ingest_funds("data/master_funds.csv")

        print("Ingesting subfunds...")
        ingestion.ingest_subfunds("data/subfunds.csv")

        print("Ingesting legal entities...")
        ingestion.ingest_legal_entities("data/legal_entities.csv")

        print("Ingesting share classes...")
        ingestion.ingest_share_classes("data/share_classes.csv")

        print("Data ingestion completed successfully!")

    finally:
        ingestion.close()

if __name__ == "__main__":
    main()