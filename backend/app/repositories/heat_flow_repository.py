from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domain.heat_flow import HeatFlowInput, HeatFlowResult
from app.persistence.entities import HeatFlowRecord

class HeatFlowRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[HeatFlowRecord]:
        return list(self.db.scalars(select(HeatFlowRecord).order_by(HeatFlowRecord.time, HeatFlowRecord.id)).all())

    def save_calculation(self, record_id: int | None, data: HeatFlowInput, result: HeatFlowResult) -> HeatFlowRecord:
        record = self.db.get(HeatFlowRecord, record_id) if record_id else None
        if record is None:
            record = HeatFlowRecord()
            self.db.add(record)
        record.time = data.time
        record.p1_mpa = data.p1_mpa
        record.t1_c = data.t1_c
        record.p2_mpa = data.p2_mpa
        record.t2_c = data.t2_c
        record.w1_kg_s = data.w1_kg_s
        record.w2_kg_s = data.w2_kg_s
        record.qw_mw = result.qw_mw
        record.qs_mw = result.qs_mw
        record.q_total_mw = result.q_total_mw
        self.db.flush()
        return record

    def save_inputs(self, record_id: int | None, data: HeatFlowInput) -> HeatFlowRecord:
        record = self.db.get(HeatFlowRecord, record_id) if record_id else None
        if record is None:
            record = HeatFlowRecord()
            self.db.add(record)
        record.time = data.time
        record.p1_mpa = data.p1_mpa
        record.t1_c = data.t1_c
        record.p2_mpa = data.p2_mpa
        record.t2_c = data.t2_c
        record.w1_kg_s = data.w1_kg_s
        record.w2_kg_s = data.w2_kg_s
        record.qw_mw = None
        record.qs_mw = None
        record.q_total_mw = None
        self.db.flush()
        return record

    def commit(self) -> None:
        self.db.commit()

    def delete(self, record_id: int) -> bool:
        record = self.db.get(HeatFlowRecord, record_id)
        if record is None:
            return False
        self.db.delete(record)
        self.db.commit()
        return True
