from fastapi import HTTPException, status

from app.domain.heat_flow import HeatFlowCalculationModel, HeatFlowInput
from app.domain.models import VolumetricInput
from app.domain.volumetric import VolumetricCalculationModel
from app.repositories.calculation_repository import CalculationRepository
from app.repositories.heat_flow_repository import HeatFlowRepository
from app.schemas.calculation import (
    CalculationResponse,
    HeatFlowCalculationRequest,
    HeatFlowCalculationResponse,
    HeatFlowDraftResponse,
    HeatFlowPointResponse,
    HeatFlowRecordResponse,
    VolumetricCalculationRequest,
)


class CalculationService:
    def __init__(self, repository: CalculationRepository, heat_flow_repository: HeatFlowRepository | None = None):
        self.repository = repository
        self.heat_flow_repository = heat_flow_repository
        self.model = VolumetricCalculationModel()
        self.heat_flow_model = HeatFlowCalculationModel()

    def calculate_volumetric(self, request: VolumetricCalculationRequest) -> CalculationResponse:
        data = VolumetricInput(**request.model_dump(exclude={"name"}))
        result = self.model.calculate(data)
        record = self.repository.save(name=request.name, **result.__dict__)
        return CalculationResponse(id=record.id, **result.__dict__)

    def calculate_heat_flow(self, request: HeatFlowCalculationRequest) -> HeatFlowCalculationResponse:
        if self.heat_flow_repository is None:
            raise RuntimeError("缺少热流量记录仓储")
        results: list[HeatFlowPointResponse] = []
        for index, point in enumerate(request.points, start=1):
            try:
                data = HeatFlowInput(**point.model_dump(exclude={"id"}))
                result = self.heat_flow_model.calculate(data)
            except ValueError as error:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"第 {index} 行：{error}",
                ) from error
            record = self.heat_flow_repository.save_calculation(point.id, data, result)
            results.append(
                HeatFlowPointResponse(
                    id=record.id,
                    time=f"{result.time:%Y-%m-%d} {result.time.hour}:{result.time:%M}",
                    qw_mw=result.qw_mw,
                    qs_mw=result.qs_mw,
                    q_total_mw=result.q_total_mw,
                )
            )
        self.heat_flow_repository.commit()
        return HeatFlowCalculationResponse(results=results)

    def save_heat_flow_inputs(self, request: HeatFlowCalculationRequest) -> HeatFlowDraftResponse:
        if self.heat_flow_repository is None:
            raise RuntimeError("缺少热流量记录仓储")
        ids: list[int] = []
        for point in request.points:
            data = HeatFlowInput(**point.model_dump(exclude={"id"}))
            ids.append(self.heat_flow_repository.save_inputs(point.id, data).id)
        self.heat_flow_repository.commit()
        return HeatFlowDraftResponse(ids=ids)

    def list_heat_flow_records(self) -> list[HeatFlowRecordResponse]:
        if self.heat_flow_repository is None:
            raise RuntimeError("缺少热流量记录仓储")
        return [
            HeatFlowRecordResponse(
                id=record.id,
                time=f"{record.time:%Y-%m-%d} {record.time.hour}:{record.time:%M}",
                p1_mpa=record.p1_mpa,
                t1_c=record.t1_c,
                p2_mpa=record.p2_mpa,
                t2_c=record.t2_c,
                w1_kg_s=record.w1_kg_s,
                w2_kg_s=record.w2_kg_s,
                qw_mw=record.qw_mw,
                qs_mw=record.qs_mw,
                q_total_mw=record.q_total_mw,
            )
            for record in self.heat_flow_repository.list()
        ]

    def delete_heat_flow_record(self, record_id: int) -> bool:
        if self.heat_flow_repository is None:
            raise RuntimeError("缺少热流量记录仓储")
        return self.heat_flow_repository.delete(record_id)
