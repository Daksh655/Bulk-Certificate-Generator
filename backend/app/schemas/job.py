from datetime import date
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    computed_field,
)

StrippedString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class RecipientRequest(BaseModel):
    name: StrippedString
    email: EmailStr

class CreateJobRequest(BaseModel):
    event_name: StrippedString
    event_date: date
    recipients: list[RecipientRequest] = Field(..., min_length=1)

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    event_name: str
    event_date: date
    status: str
    total_count: int
    success_count: int
    failure_count: int


class JobStatusResponse(JobResponse):
    @computed_field
    @property
    def progress(self) -> float:
        if self.total_count == 0:
            return 0.0
        processed = self.success_count + self.failure_count
        return round(processed / self.total_count * 100, 1)
