import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

def get_datetime_utc() -> datetime:
    return datetime.now(UTC)

class WorkOrderBase(SQLModel):        
    title: str
    status: str

class WorkOrder(WorkOrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
    )

