from pydantic import BaseModel, Field
from typing import Literal


class FinancialAction(BaseModel):
    action: Literal["refund"]
    payment_id: str
    amount: float = Field(gt=0)
    reason: str


class GuardDecision(BaseModel):
    decision: Literal["APPROVE", "REVIEW", "BLOCK"]
    reason: str
    risk_score: float = Field(ge=0, le=1)