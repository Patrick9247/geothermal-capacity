from sqlalchemy.orm import Session
from app.persistence.entities import CalculationRecord
class CalculationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, *, name: str, model: str, thermal_energy_gj: float, electrical_power_mw: float) -> CalculationRecord:
        record = CalculationRecord(
            name=name,
            model=model,
            thermal_energy_gj=thermal_energy_gj,
            electrical_power_mw=electrical_power_mw,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
