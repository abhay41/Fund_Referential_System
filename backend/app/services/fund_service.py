"""
Business logic for fund operations
"""
from typing import List, Dict, Any, Optional
from neo4j import Session
import logging

logger = logging.getLogger(__name__)


class FundService:
    """Service layer for fund operations"""
    
    @staticmethod
    def get_fund_by_code(session: Session, fund_code: str) -> Optional[Dict[str, Any]]:
        """Point lookup of a fund based on fund code"""
        query = """
        MATCH (f:Fund {fund_code: $fund_code})
        OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)-[:HAS_LEGAL_ENTITY]->(mle:LegalEntity)
        OPTIONAL MATCH (f)-[:HAS_LEGAL_ENTITY]->(fle:LegalEntity)
        OPTIONAL MATCH (f)-[:HAS_SHARE_CLASS]->(sc:ShareClass)
        OPTIONAL MATCH (sf:SubFund)-[:PARENT_FUND]->(f)
        RETURN f, 
               m, mle, fle,
               collect(DISTINCT sc) as share_classes,
               collect(DISTINCT sf) as subfunds
        """
        result = session.run(query, fund_code=fund_code)
        record = result.single()
        
        if not record:
            return None
        
        fund = dict(record['f'])
        fund['management_entity'] = dict(record['m']) if record['m'] else None
        if fund['management_entity']:
            fund['management_entity']['legal_entity'] = dict(record['mle']) if record['mle'] else None
        fund['legal_entity'] = dict(record['fle']) if record['fle'] else None
        fund['share_classes'] = [dict(sc) for sc in record['share_classes'] if sc]
        fund['subfunds'] = [dict(sf) for sf in record['subfunds'] if sf]
        
        return fund
    
    @staticmethod
    def get_fund_by_id(session: Session, fund_id: str) -> Optional[Dict[str, Any]]:
        """Point lookup of a fund based on fund ID"""
        query = """
        MATCH (f:Fund {fund_id: $fund_id})
        OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)-[:HAS_LEGAL_ENTITY]->(mle:LegalEntity)
        OPTIONAL MATCH (f)-[:HAS_LEGAL_ENTITY]->(fle:LegalEntity)
        OPTIONAL MATCH (f)-[:HAS_SHARE_CLASS]->(sc:ShareClass)
        OPTIONAL MATCH (sf:SubFund)-[:PARENT_FUND]->(f)
        RETURN f, 
               m, mle, fle,
               collect(DISTINCT sc) as share_classes,
               collect(DISTINCT sf) as subfunds
        """
        result = session.run(query, fund_id=fund_id)
        record = result.single()
        
        if not record:
            return None
        
        fund = dict(record['f'])
        fund['management_entity'] = dict(record['m']) if record['m'] else None
        if fund['management_entity']:
            fund['management_entity']['legal_entity'] = dict(record['mle']) if record['mle'] else None
        fund['legal_entity'] = dict(record['fle']) if record['fle'] else None
        fund['share_classes'] = [dict(sc) for sc in record['share_classes'] if sc]
        fund['subfunds'] = [dict(sf) for sf in record['subfunds'] if sf]
        
        return fund
    
    @staticmethod
    def get_fund_hierarchy_children(session: Session, fund_id: str, depth: int = 1) -> Dict[str, Any]:
        """Retrieve the n+1 children hierarchy of a fund"""
        query = """
        MATCH (f:Fund {fund_id: $fund_id})
        OPTIONAL MATCH path = (f)<-[:PARENT_FUND*1..""" + str(depth) + """..depth]-(sf:SubFund)
        WITH f, collect(DISTINCT {
            subfund: sf,
            depth: length(path)
        }) as subfunds_with_depth
        OPTIONAL MATCH (f)-[:HAS_SHARE_CLASS]->(sc:ShareClass)
        RETURN f, 
               subfunds_with_depth,
               collect(DISTINCT sc) as share_classes
        """
        result = session.run(query, fund_id=fund_id, depth=depth)
        record = result.single()
        
        if not record:
            return None
        
        fund = dict(record['f'])
        fund['subfunds'] = []
        
        for item in record['subfunds_with_depth']:
            if item['subfund']:
                subfund_data = dict(item['subfund'])
                subfund_data['depth'] = item['depth']
                fund['subfunds'].append(subfund_data)
        
        fund['share_classes'] = [dict(sc) for sc in record['share_classes'] if sc]
        
        return {
            'root': fund,
            'children': fund['subfunds'],
            'depth': depth
        }
    
    @staticmethod
    def get_fund_hierarchy_parents(session: Session, identifier: str, depth: int = 1) -> Dict[str, Any]:
        """Retrieve the n-1 parent hierarchy of a fund/subfund"""
        # First check if it's a subfund or fund
        query = """
        MATCH (sf:SubFund {subfund_id: $identifier})
        OPTIONAL MATCH path = (sf)-[:PARENT_FUND*1..""" + str(depth) + """..depth]->(pf:Fund)
        WITH sf, collect(DISTINCT {
            parent: pf,
            depth: length(path)
        }) as parents_with_depth
        RETURN sf as node, 'SubFund' as node_type, parents_with_depth
        UNION
        MATCH (f:Fund {fund_id: $identifier})
        RETURN f as node, 'Fund' as node_type, [] as parents_with_depth
        """
        result = session.run(query, identifier=identifier, depth=depth)
        record = result.single()
        
        if not record:
            return None
        
        node = dict(record['node'])
        parents = []
        
        for item in record['parents_with_depth']:
            if item['parent']:
                parent_data = dict(item['parent'])
                parent_data['depth'] = item['depth']
                parents.append(parent_data)
        
        return {
            'root': node,
            'node_type': record['node_type'],
            'parents': parents,
            'depth': depth
        }
    
    @staticmethod
    def get_funds_by_management_entity(session: Session, mgmt_id: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Find all funds which have the same management entity"""
        skip = (page - 1) * page_size
        
        # Get total count
        count_query = """
        MATCH (f:Fund)-[:MANAGED_BY]->(m:ManagementEntity {mgmt_id: $mgmt_id})
        RETURN count(f) as total
        """
        count_result = session.run(count_query, mgmt_id=mgmt_id)
        total = count_result.single()['total']
        
        # Get paginated results
        query = """
        MATCH (f:Fund)-[:MANAGED_BY]->(m:ManagementEntity {mgmt_id: $mgmt_id})
        OPTIONAL MATCH (f)-[:HAS_LEGAL_ENTITY]->(fle:LegalEntity)
        OPTIONAL MATCH (m)-[:HAS_LEGAL_ENTITY]->(mle:LegalEntity)
        RETURN f, m, mle, fle
        ORDER BY f.fund_id
        SKIP $skip
        LIMIT $limit
        """
        result = session.run(query, mgmt_id=mgmt_id, skip=skip, limit=page_size)
        
        funds = []
        for record in result:
            fund = dict(record['f'])
            fund['management_entity'] = dict(record['m']) if record['m'] else None
            if fund['management_entity'] and record['mle']:
                fund['management_entity']['legal_entity'] = dict(record['mle'])
            fund['legal_entity'] = dict(record['fle']) if record['fle'] else None
            funds.append(fund)
        
        return {
            'data': funds,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    @staticmethod
    def search_funds(session: Session, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Search funds with various filters"""
        page = search_params.get('page', 1)
        page_size = search_params.get('page_size', 10)
        skip = (page - 1) * page_size
        
        # Build WHERE clause dynamically
        where_clauses = []
        params = {'skip': skip, 'limit': page_size}
        
        if search_params.get('fund_code'):
            where_clauses.append("f.fund_code = $fund_code")
            params['fund_code'] = search_params['fund_code']
        
        if search_params.get('fund_id'):
            where_clauses.append("f.fund_id = $fund_id")
            params['fund_id'] = search_params['fund_id']
        
        if search_params.get('isin'):
            where_clauses.append("f.isin_master = $isin")
            params['isin'] = search_params['isin']
        
        if search_params.get('fund_type'):
            where_clauses.append("f.fund_type = $fund_type")
            params['fund_type'] = search_params['fund_type']
        
        if search_params.get('status'):
            where_clauses.append("f.status = $status")
            params['status'] = search_params['status']
        
        if search_params.get('mgmt_id'):
            where_clauses.append("m.mgmt_id = $mgmt_id")
            params['mgmt_id'] = search_params['mgmt_id']
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Count query
        count_query = f"""
        MATCH (f:Fund)
        OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)
        WHERE {where_clause}
        RETURN count(f) as total
        """
        count_result = session.run(count_query, **params)
        total = count_result.single()['total']
        
        # Data query
        query = f"""
        MATCH (f:Fund)
        OPTIONAL MATCH (f)-[:MANAGED_BY]->(m:ManagementEntity)
        OPTIONAL MATCH (f)-[:HAS_LEGAL_ENTITY]->(fle:LegalEntity)
        WHERE {where_clause}
        RETURN f, m, fle
        ORDER BY f.fund_id
        SKIP $skip
        LIMIT $limit
        """
        result = session.run(query, **params)
        
        funds = []
        for record in result:
            fund = dict(record['f'])
            fund['management_entity'] = dict(record['m']) if record['m'] else None
            fund['legal_entity'] = dict(record['fle']) if record['fle'] else None
            funds.append(fund)
        
        return {
            'data': funds,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    @staticmethod
    def create_fund(session: Session, fund_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new fund"""
        # Generate fund_id
        query = """
        MATCH (f:Fund)
        RETURN f.fund_id as fund_id
        ORDER BY f.fund_id DESC
        LIMIT 1
        """
        result = session.run(query)
        record = result.single()
        
        if record and record['fund_id']:
            last_id = record['fund_id']
            num = int(last_id[1:]) + 1
            fund_id = f"F{num:06d}"
        else:
            fund_id = "F000001"
        
        # Create fund node
        create_query = """
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
        RETURN f
        """
        
        params = {
            'fund_id': fund_id,
            **fund_data
        }
        
        result = session.run(create_query, **params)
        record = result.single()
        
        return dict(record['f']) if record else None
    
    @staticmethod
    def update_fund(session: Session, fund_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update fund properties"""
        set_clauses = []
        params = {'fund_id': fund_id}
        
        for key, value in update_data.items():
            if key not in ['fund_id', 'mgmt_id', 'le_id']:  # Don't update IDs
                set_clauses.append(f"f.{key} = ${key}")
                params[key] = value
        
        if not set_clauses:
            return None
        
        query = f"""
        MATCH (f:Fund {{fund_id: $fund_id}})
        SET {', '.join(set_clauses)}
        RETURN f
        """
        
        result = session.run(query, **params)
        record = result.single()
        
        return dict(record['f']) if record else None
