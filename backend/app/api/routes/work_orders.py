import uuid

from fastapi import APIRouter, HTTPException

from app.core.db import SessionDep
from app.models import WorkOrderBase, WorkOrder

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

@router.post("")
def Create_work_order(work_order_in: WorkOrderBase, 
                      session: SessionDep) -> WorkOrder: 
    work_order = WorkOrder.model_validate(work_order_in)
    session.add(work_order)
    session.commit()
    session.refresh(work_order)

    return work_order

@router.get("/{id}")
def read_work_order(id: uuid.UUID, session: SessionDep) -> WorkOrder:
    work_order = session.get(WorkOrder, id)
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return work_order
