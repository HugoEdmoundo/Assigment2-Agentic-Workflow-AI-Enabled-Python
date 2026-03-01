from pydantic import BaseModel
from typing import Optional, Dict, Any

class WorkflowRequest(BaseModel):
    user_id: str
    topic: str

class WorkflowResponse(BaseModel):
    task_id: str
    status: str
    message: str

class WorkflowStatus(BaseModel):
    task_id: str
    user_id: Optional[str] = None
    topic: Optional[str] = None
    status: str
    current_step: int
    total_steps: int
    result: Optional[Dict[str, Any]] = None
    pdf_path: Optional[str] = None
    error: Optional[str] = None
