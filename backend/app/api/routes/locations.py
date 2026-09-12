import uuid

from fastapi import APIRouter, HTTPException

from app.core.db import SessionDep
from app.models import LocationBase, Location, WorkOrder

router = APIRouter(prefix="/locations", tags=["locations"])

@router.post("")
def create_location(location_in: LocationBase,
                    session: SessionDep) -> Location:
    location = Location.model_validate(location_in)
    session.add(location)
    session.commit()
    session.refresh(location)
    return location

@router.get("/{id}")
def read_location(id: uuid.UUID, session: SessionDep) -> Location:
    location = session.get(Location, id)
    if not location:
        raise HTTPException(status_code=404, detail="location not found")
    return location

@router.get("/{id}/work-orders")
def read_work_orders_in_location(id: uuid.UUID, session: SessionDep) -> list[WorkOrder]:
    location = session.get(Location, id)
    if not location:
        raise HTTPException(status_code=404, detail="location not found")
    return location.work_orders