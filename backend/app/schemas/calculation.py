from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class VolumetricCalculationRequest(BaseModel):
    name: str = Field(default="未命名方案", max_length=100)
    reservoir_volume_m3: float = Field(gt=0, description="储层体积（m³）")
    porosity: float = Field(gt=0, le=1)
    recovery_factor: float = Field(gt=0, le=1)
    fluid_density_kg_m3: float = Field(gt=0)
    specific_heat_kj_kg_k: float = Field(gt=0)
    reservoir_temperature_c: float
    reference_temperature_c: float
    conversion_efficiency: float = Field(gt=0, le=1)
    project_lifetime_years: float = Field(gt=0)


class CalculationResponse(BaseModel):
    id: int | None = None
    model: str
    thermal_energy_gj: float
    electrical_power_mw: float


class HeatFlowPointRequest(BaseModel):
    id: int | None = None
    time: datetime = Field(default_factory=datetime.now)
    p1_mpa: float = Field(gt=0, description="地热水压力（MPa）")
    t1_c: float = Field(description="地热水温度（℃）")
    p2_mpa: float = Field(gt=0, description="地热蒸汽压力（MPa）")
    t2_c: float = Field(description="地热蒸汽温度（℃）")
    w1_kg_s: float = Field(ge=0, description="地热水质量流量（kg/s）")
    w2_kg_s: float = Field(ge=0, description="地热蒸汽质量流量（kg/s）")

    @field_validator("time", mode="before")
    @classmethod
    def parse_minute_precision_time(cls, value: datetime | str | None) -> datetime | str:
        """Accept both the API display format (e.g. 2026-08-05 8:20) and ISO input."""
        if value is None or value == "":
            return datetime.now()
        if isinstance(value, str):
            for time_format in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(value, time_format)
                except ValueError:
                    continue
        return value


class HeatFlowCalculationRequest(BaseModel):
    points: list[HeatFlowPointRequest] = Field(min_length=1, max_length=5000)


class HeatFlowPointResponse(BaseModel):
    id: int
    time: str
    qw_mw: float
    qs_mw: float
    q_total_mw: float


class HeatFlowCalculationResponse(BaseModel):
    results: list[HeatFlowPointResponse]


class HeatFlowDraftResponse(BaseModel):
    ids: list[int]


class HeatFlowRecordResponse(BaseModel):
    id: int
    time: str
    p1_mpa: float
    t1_c: float
    p2_mpa: float
    t2_c: float
    w1_kg_s: float
    w2_kg_s: float
    qw_mw: float | None
    qs_mw: float | None
    q_total_mw: float | None
