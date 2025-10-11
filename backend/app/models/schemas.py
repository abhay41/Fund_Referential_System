"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums
class FundType(str, Enum):
    UCITS = "UCITS"
    AIF = "AIF"
    ETF = "ETF"
    MUTUAL_FUND = "MUTUAL_FUND"
    HEDGE_FUND = "HEDGE_FUND"


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    SUSPENDED = "SUSPENDED"


class EntityType(str, Enum):
    MANAGER = "MANAGER"
    FUND = "FUND"
    SUBFUND = "SUBFUND"


class DistributionType(str, Enum):
    ACCUMULATING = "ACCUMULATING"
    INCOME = "INCOME"
    DRIP = "DRIP"


# Base Models
class LegalEntityBase(BaseModel):
    le_id: str = Field(..., description="Legal Entity ID")
    lei: str = Field(..., description="Legal Entity Identifier")
    legal_name: str = Field(..., description="Legal name of entity")
    jurisdiction: str = Field(..., description="Jurisdiction")
    entity_type: str = Field(..., description="Type of entity")


class LegalEntityResponse(LegalEntityBase):
    """Legal Entity response model"""
    pass


class ManagementEntityBase(BaseModel):
    mgmt_id: str = Field(..., description="Management Entity ID")
    le_id: str = Field(..., description="Associated Legal Entity ID")
    registration_no: str = Field(..., description="Registration number")
    domicile: str = Field(..., description="Domicile country")
    entity_type: str = Field(..., description="Entity type")


class ManagementEntityResponse(ManagementEntityBase):
    """Management Entity response with legal entity details"""
    legal_entity: Optional[LegalEntityResponse] = None


class FundBase(BaseModel):
    fund_id: str = Field(..., description="Fund ID")
    mgmt_id: str = Field(..., description="Management Entity ID")
    le_id: str = Field(..., description="Legal Entity ID")
    fund_code: str = Field(..., description="Fund code")
    fund_name: str = Field(..., description="Fund name")
    fund_type: str = Field(..., description="Fund type")
    base_currency: str = Field(..., description="Base currency")
    domicile: str = Field(..., description="Domicile")
    isin_master: str = Field(..., description="Master ISIN")
    status: str = Field(..., description="Fund status")


class FundResponse(FundBase):
    """Fund response with related entities"""
    management_entity: Optional[ManagementEntityResponse] = None
    legal_entity: Optional[LegalEntityResponse] = None
    share_classes: Optional[List[Dict[str, Any]]] = None
    subfunds: Optional[List[Dict[str, Any]]] = None


class SubFundBase(BaseModel):
    subfund_id: str = Field(..., description="Subfund ID")
    parent_fund_id: str = Field(..., description="Parent fund ID")
    le_id: str = Field(..., description="Legal Entity ID")
    mgmt_id: str = Field(..., description="Management Entity ID")
    isin_sub: str = Field(..., description="Subfund ISIN")
    currency: str = Field(..., description="Currency")


class SubFundResponse(SubFundBase):
    """Subfund response with parent fund details"""
    parent_fund: Optional[FundResponse] = None
    management_entity: Optional[ManagementEntityResponse] = None
    legal_entity: Optional[LegalEntityResponse] = None


class ShareClassBase(BaseModel):
    sc_id: str = Field(..., description="Share Class ID")
    fund_id: str = Field(..., description="Associated Fund ID")
    isin_sc: str = Field(..., description="Share Class ISIN")
    currency: str = Field(..., description="Currency")
    distribution: str = Field(..., description="Distribution type")
    fee_mgmt: float = Field(..., description="Management fee")
    perf_fee: float = Field(..., description="Performance fee")
    expense_ratio: float = Field(..., description="Expense ratio")
    nav: float = Field(..., description="Net Asset Value")
    aum: float = Field(..., description="Assets Under Management")
    status: str = Field(..., description="Status")


class ShareClassResponse(ShareClassBase):
    """Share Class response with fund details"""
    fund: Optional[FundResponse] = None


# Create requests
class FundCreate(BaseModel):
    fund_code: str
    fund_name: str
    fund_type: str
    base_currency: str
    domicile: str
    isin_master: str
    status: str = "ACTIVE"
    mgmt_id: str
    le_id: str


class SubFundCreate(BaseModel):
    parent_fund_id: str
    le_id: str
    mgmt_id: str
    isin_sub: str
    currency: str


class ShareClassCreate(BaseModel):
    fund_id: str
    isin_sc: str
    currency: str
    distribution: str
    fee_mgmt: float
    perf_fee: float
    expense_ratio: float
    nav: float
    aum: float
    status: str = "ACTIVE"


# Hierarchy response models
class HierarchyNode(BaseModel):
    node_id: str
    node_type: str
    properties: Dict[str, Any]
    relationships: Optional[List[Dict[str, Any]]] = None


class HierarchyResponse(BaseModel):
    root: HierarchyNode
    children: Optional[List[HierarchyNode]] = None
    parents: Optional[List[HierarchyNode]] = None
    depth: int


# Search and filter models
class FundSearchParams(BaseModel):
    fund_code: Optional[str] = None
    fund_id: Optional[str] = None
    ticker: Optional[str] = None
    isin: Optional[str] = None
    mgmt_id: Optional[str] = None
    fund_type: Optional[str] = None
    status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
