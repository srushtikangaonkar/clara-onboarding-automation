from pydantic import BaseModel
from typing import List, Optional, Dict


class BusinessHours(BaseModel):
    days: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    timezone: Optional[str] = None


class RoutingRule(BaseModel):
    description: Optional[str] = None
    transfer_to: Optional[str] = None
    order: Optional[int] = None
    fallback_action: Optional[str] = None


class CallTransferRules(BaseModel):
    timeout_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None
    failure_message: Optional[str] = None


class AccountMemo(BaseModel):
    account_id: str
    company_name: Optional[str] = None

    business_hours: Optional[BusinessHours] = None
    office_address: Optional[str] = None

    services_supported: List[str] = []
    emergency_definition: List[str] = []

    emergency_routing_rules: List[RoutingRule] = []
    non_emergency_routing_rules: List[RoutingRule] = []

    call_transfer_rules: Optional[CallTransferRules] = None
    integration_constraints: List[str] = []

    after_hours_flow_summary: Optional[str] = None
    office_hours_flow_summary: Optional[str] = None

    questions_or_unknowns: List[str] = []
    notes: Optional[str] = None
    