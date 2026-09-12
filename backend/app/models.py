import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

def get_datetime_utc() -> datetime:
    return datetime.now(UTC)

class WorkOrderBase(SQLModel):        
    title: str
    status: str
    location_id: uuid.UUID = Field(
            foreign_key="location.id", nullable=False, ondelete="CASCADE"
        )
    
class WorkOrder(WorkOrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
    )
    location: Location = Relationship(back_populates="work_orders")

class LocationBase(SQLModel):
    title: str
    coordinates: str

class Location(LocationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True), 
    )
    work_orders: list[WorkOrder] = Relationship(back_populates="location", cascade_delete=True)