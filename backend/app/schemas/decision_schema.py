from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    decision: str = Field(..., min_length=1)
    comment: str = Field(..., min_length=1, max_length=1000)
    reviewed_by: str = Field(..., min_length=1, max_length=120)


class DecisionResponse(BaseModel):
    case_id: str
    decision: str
    status: str
    message: str
    requires_human_review: bool = True
