from app.domain.models import CalculationResult, VolumetricInput

class VolumetricCalculationModel:

    name = "volumetric"
    def calculate(self, data: VolumetricInput) -> CalculationResult:
        delta_t = max(data.reservoir_temperature_c - data.reference_temperature_c, 0)
        thermal_energy_kj = (
            data.reservoir_volume_m3
            * data.porosity
            * data.recovery_factor
            * data.fluid_density_kg_m3
            * data.specific_heat_kj_kg_k
            * delta_t
        )
        thermal_energy_gj = thermal_energy_kj / 1_000_000
        seconds = data.project_lifetime_years * 365.25 * 24 * 3600
        electrical_power_mw = (thermal_energy_kj * data.conversion_efficiency / seconds) / 1000
        return CalculationResult(
            model=self.name,
            thermal_energy_gj=round(thermal_energy_gj, 3),
            electrical_power_mw=round(electrical_power_mw, 3),
        )
