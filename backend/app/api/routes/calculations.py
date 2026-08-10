from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.persistence.entities import User
from app.repositories.calculation_repository import CalculationRepository
from app.repositories.heat_flow_repository import HeatFlowRepository
from app.schemas.calculation import (
    CalculationResponse,
    HeatFlowCalculationRequest,
    HeatFlowCalculationResponse,
    HeatFlowDraftResponse,
    HeatFlowRecordResponse,
    VolumetricCalculationRequest,
)
from app.services.calculation_service import CalculationService
router = APIRouter(prefix="/calculations", tags=["calculations"])

@router.post("/volumetric", response_model=CalculationResponse)
def calculate_volumetric(
    request: VolumetricCalculationRequest,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(get_current_user)] = None,
):
    return CalculationService(CalculationRepository(db)).calculate_volumetric(request)

@router.get("/heat-flow", response_model=list[HeatFlowRecordResponse])
def list_heat_flow_records(
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(get_current_user)] = None,
):
    service = CalculationService(CalculationRepository(db), HeatFlowRepository(db))
    return service.list_heat_flow_records()

@router.put("/heat-flow", response_model=HeatFlowDraftResponse)
def save_heat_flow_inputs(
    request: HeatFlowCalculationRequest,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(get_current_user)] = None,
):
    service = CalculationService(CalculationRepository(db), HeatFlowRepository(db))
    return service.save_heat_flow_inputs(request)

@router.post("/heat-flow", response_model=HeatFlowCalculationResponse)
def calculate_heat_flow(
    request: HeatFlowCalculationRequest,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(get_current_user)] = None,
):
    service = CalculationService(CalculationRepository(db), HeatFlowRepository(db))
    return service.calculate_heat_flow(request)


@router.delete("/heat-flow/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_heat_flow_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(get_current_user)] = None,
):
    service = CalculationService(CalculationRepository(db), HeatFlowRepository(db))
    if not service.delete_heat_flow_record(record_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
