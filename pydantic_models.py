from pydantic import BaseModel, Field
from typing import Optional, List


class CabinetModel(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Name of the cabinet")
    number: int = Field(..., ge=1, le=100, description="Cabinet number, must be a positive integer")

class CabinetResponseModel(CabinetModel):
    id: int
    # students: List["StudentResponseModel"] = []

class StudentModel(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100, description="Full name of the student")
    cabinet_name: Optional[str] = Field(None, description="Name of the cabinet assigned to the student")
    cabinet_number: Optional[int] = Field(None, description="Number of the cabinet assigned to the student")


class StudentResponseModel(StudentModel):
    id: int
    full_name: str
    cabinet: Optional[CabinetResponseModel] = None

CabinetResponseModel.update_forward_refs()
StudentResponseModel.update_forward_refs()

    
