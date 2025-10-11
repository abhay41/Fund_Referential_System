"""
Comprehensive data ingestion script for loading CSV data into Neo4j graph database
"""
import pandas as pd
import logging
from neo4j import GraphDatabase
from pathlib import Path
import os
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Data directory
DATA_DIR = Path(__file__).parent / "UC6_input_datasetd6889de"


class FundDataIngestion:
    """Handle data ingestion into Neo4j for Fund Referential system"""
    
    def __init__(self, uri, user, password):
        """Initialize Neo4j driver"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
        
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def clear_database(self):
        """Clear all existing data from the database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("✓ Database cleared")
    
    def create_constraints(self):
        """Create uniqueness constraints for all node types"""
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (le:LegalEntity) REQUIRE le.le_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (m:ManagementEntity) REQUIRE m.mgmt_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Fund) REQUIRE f.fund_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (sf:SubFund) REQUIRE sf.subfund_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (sc:ShareClass) REQUIRE sc.sc_id IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.debug(f"Constraint might already exist: {e}")
            
            logger.info("✓ Constraints created")
    
    def load_legal_entities(self, file_path):
        """Load legal entities from CSV"""
        df = pd.read_csv(file_path)
        logger.info(f"Loading {len(df)} legal entities...")
        
        with self.driver.session() as session:
            count = 0
            for _, row in df.iterrows():
                query = """
                CREATE (le:LegalEntity {
                    le_id: $le_id,
                    lei: $lei,
                    legal_name: $legal_name,
                    jurisdiction: $jurisdiction,
                    entity_type: $entity_type
                })
                """
                session.run(query, 
                    le_id=row['LE_ID'],
                    lei=row['LEI'],
                    legal_name=row['LEGAL_NAME'],
                    jurisdiction=row['JURISDICTION'],
                    entity_type=row['ENTITY_TYPE']
                )
                count += 1
        
        logger.info(f"✓ Loaded {count} legal entities")
    
    def load_management_entities(self, file_path):
        """Load management entities from CSV and link to legal entities"""
        df = pd.read_csv(file_path)
        logger.info(f"Loading {len(df)} management entities...")
        
        with self.driver.session() as session:
            count = 0
            for _, row in df.iterrows():
                query = """
                MATCH (le:LegalEntity {le_id: $le_id})
                CREATE (m:ManagementEntity {
                    mgmt_id: $mgmt_id,
                    le_id: $le_id,
                    registration_no: $registration_no,
                    domicile: $domicile,
                    entity_type: $entity_type
                })
                CREATE (m)-[:HAS_LEGAL_ENTITY]->(le)
                """
                session.run(query,
                    mgmt_id=row['MGMT_ID'],
                    le_id=row['LE_ID'],
                    registration_no=row['REGISTRATION_NO'],
                    domicile=row['DOMICILE'],
                    entity_type=row['ENTITY_TYPE']
                )
                count += 1
        
        logger.info(f"✓ Loaded {count} management entities")
    
    def load_funds(self, file_path):
        """Load funds from CSV and create relationships"""
        df = pd.read_csv(file_path)
        logger.info(f"Loading {len(df)} funds...")
        
        with self.driver.session() as session:
            count = 0
            for _, row in df.iterrows():
                query = """
                MATCH (m:ManagementEntity {mgmt_id: $mgmt_id})
                MATCH (le:LegalEntity {le_id: $le_id})
                CREATE (f:Fund {
                    fund_id: $fund_id,
                    mgmt_id: $mgmt_id,
                    le_id: $le_id,
                    fund_code: $fund_code,
                    fund_name: $fund_name,
                    fund_type: $fund_type,
                    base_currency: $base_currency,
                    domicile: $domicile,
                    isin_master: $isin_master,
                    status: $status
                })
                CREATE (f)-[:MANAGED_BY]->(m)
                CREATE (f)-[:HAS_LEGAL_ENTITY]->(le)
                """
                session.run(query,
                    fund_id=row['FUND_ID'],
                    mgmt_id=row['MGMT_ID'],
                    le_id=row['LE_ID'],
                    fund_code=row['FUND_CODE'],
                    fund_name=row['FUND_NAME'],
                    fund_type=row['FUND_TYPE'],
                    base_currency=row['BASE_CURRENCY'],
                    domicile=row['DOMICILE'],
                    isin_master=row['ISIN_MASTER'],
                    status=row['STATUS']
                )
                count += 1
        
        logger.info(f"✓ Loaded {count} funds")
    
    def load_subfunds(self, file_path):
        """Load subfunds from CSV and create relationships"""
        df = pd.read_csv(file_path)
        logger.info(f"Loading {len(df)} subfunds...")
        
        with self.driver.session() as session:
            count = 0
            for _, row in df.iterrows():
                query = """
                MATCH (pf:Fund {fund_id: $parent_fund_id})
                MATCH (le:LegalEntity {le_id: $le_id})
                MATCH (m:ManagementEntity {mgmt_id: $mgmt_id})
                CREATE (sf:SubFund {
                    subfund_id: $subfund_id,
                    parent_fund_id: $parent_fund_id,
                    le_id: $le_id,
                    mgmt_id: $mgmt_id,
                    isin_sub: $isin_sub,
                    currency: $currency
                })
                CREATE (sf)-[:PARENT_FUND]->(pf)
                CREATE (sf)-[:HAS_LEGAL_ENTITY]->(le)
                CREATE (sf)-[:MANAGED_BY]->(m)
                """
                session.run(query,
                    subfund_id=row['SUBFUND_ID'],
                    parent_fund_id=row['PARENT_FUND_ID'],
                    le_id=row['LE_ID'],
                    mgmt_id=row['MGMT_ID'],
                    isin_sub=row['ISIN_SUB'],
                    currency=row['CURRENCY']
                )
                count += 1
        
        logger.info(f"✓ Loaded {count} subfunds")
    
    def load_share_classes(self, file_path):
        """Load share classes from CSV and create relationships"""
        df = pd.read_csv(file_path)
        logger.info(f"Loading {len(df)} share classes...")
        
        with self.driver.session() as session:
            count = 0
            for _, row in df.iterrows():
                query = """
                MATCH (f:Fund {fund_id: $fund_id})
                CREATE (sc:ShareClass {
                    sc_id: $sc_id,
                    fund_id: $fund_id,
                    isin_sc: $isin_sc,
                    currency: $currency,
                    distribution: $distribution,
                    fee_mgmt: $fee_mgmt,
                    perf_fee: $perf_fee,
                    expense_ratio: $expense_ratio,
                    nav: $nav,
                    aum: $aum,
                    status: $status
                })
                CREATE (f)-[:HAS_SHARE_CLASS]->(sc)
                """
                session.run(query,
                    sc_id=row['SC_ID'],
                    fund_id=row['FUND_ID'],
                    isin_sc=row['ISIN_SC'],
                    currency=row['CURRENCY'],
                    distribution=row['DISTRIBUTION'],
                    fee_mgmt=float(row['FEE_MGMT']),
                    perf_fee=float(row['PERF_FEE']),
                    expense_ratio=float(row['EXPENSE_RATIO']),
                    nav=float(row['NAV']),
                    aum=float(row['AUM']),
                    status=row['STATUS']
                )
                count += 1
        
        logger.info(f"✓ Loaded {count} share classes")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX IF NOT EXISTS FOR (f:Fund) ON (f.fund_code)",
                "CREATE INDEX IF NOT EXISTS FOR (f:Fund) ON (f.isin_master)",
                "CREATE INDEX IF NOT EXISTS FOR (f:Fund) ON (f.fund_type)",
                "CREATE INDEX IF NOT EXISTS FOR (f:Fund) ON (f.status)",
                "CREATE INDEX IF NOT EXISTS FOR (sf:SubFund) ON (sf.isin_sub)",
                "CREATE INDEX IF NOT EXISTS FOR (sc:ShareClass) ON (sc.isin_sc)",
                "CREATE INDEX IF NOT EXISTS FOR (m:ManagementEntity) ON (m.registration_no)",
                "CREATE INDEX IF NOT EXISTS FOR (le:LegalEntity) ON (le.lei)",
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    logger.debug(f"Index might already exist: {e}")
        
        logger.info("✓ Indexes created")
    
    def print_summary(self):
        """Print summary of loaded data"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (le:LegalEntity) WITH count(le) as legal_entities
                MATCH (m:ManagementEntity) WITH legal_entities, count(m) as management_entities
                MATCH (f:Fund) WITH legal_entities, management_entities, count(f) as funds
                MATCH (sf:SubFund) WITH legal_entities, management_entities, funds, count(sf) as subfunds
                MATCH (sc:ShareClass) WITH legal_entities, management_entities, funds, subfunds, count(sc) as share_classes
                RETURN legal_entities, management_entities, funds, subfunds, share_classes
            """)
            
            record = result.single()
            if record:
                logger.info("\n" + "="*50)
                logger.info("DATABASE SUMMARY")
                logger.info("="*50)
                logger.info(f"Legal Entities:      {record['legal_entities']}")
                logger.info(f"Management Entities: {record['management_entities']}")
                logger.info(f"Funds:               {record['funds']}")
                logger.info(f"SubFunds:            {record['subfunds']}")
                logger.info(f"Share Classes:       {record['share_classes']}")
                logger.info("="*50 + "\n")


def main():
    """Main ingestion process"""
    logger.info("\n" + "="*50)
    logger.info("FUND REFERENTIAL DATA INGESTION")
    logger.info("="*50 + "\n")
    
    ingestion = FundDataIngestion(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Step 1: Clear existing data
        logger.info("[1/7] Clearing existing data...")
        ingestion.clear_database()
        
        # Step 2: Create constraints
        logger.info("[2/7] Creating constraints...")
        ingestion.create_constraints()
        
        # Step 3-7: Load data in order (dependencies matter!)
        logger.info("[3/7] Loading legal entities...")
        ingestion.load_legal_entities(DATA_DIR / "legal_entity.csv")
        
        logger.info("[4/7] Loading management entities...")
        ingestion.load_management_entities(DATA_DIR / "management_entity.csv")
        
        logger.info("[5/7] Loading funds...")
        ingestion.load_funds(DATA_DIR / "fund_master.csv")
        
        logger.info("[6/7] Loading subfunds...")
        ingestion.load_subfunds(DATA_DIR / "sub_fund.csv")
        
        logger.info("[7/7] Loading share classes...")
        ingestion.load_share_classes(DATA_DIR / "share_class.csv")
        
        # Create indexes
        logger.info("Creating indexes for performance...")
        ingestion.create_indexes()
        
        # Print summary
        ingestion.print_summary()
        
        logger.info("✅ DATA INGESTION COMPLETED SUCCESSFULLY!\n")
        
    except Exception as e:
        logger.error(f"❌ Error during ingestion: {e}")
        raise
    finally:
        ingestion.close()


if __name__ == "__main__":
    main()
