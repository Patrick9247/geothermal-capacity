from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VolumetricInput:
    reservoir_volume_m3: float
    porosity: float
    recovery_factor: float
    fluid_density_kg_m3: float
    specific_heat_kj_kg_k: float
    reservoir_temperature_c: float
    reference_temperature_c: float
    conversion_efficiency: float
    project_lifetime_years: float


@dataclass(frozen=True)
class CalculationResult:
    model: str
    thermal_energy_gj: float
    electrical_power_mw: float


class CalculationModel(Protocol):
    name: str

    def calculate(self, data: VolumetricInput) -> CalculationResult: ...
