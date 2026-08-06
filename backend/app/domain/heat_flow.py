from dataclasses import dataclass
from datetime import datetime

import seuif97


@dataclass(frozen=True)
class HeatFlowInput:
    time: datetime
    p1_mpa: float
    t1_c: float
    p2_mpa: float
    t2_c: float
    w1_kg_s: float
    w2_kg_s: float


@dataclass(frozen=True)
class HeatFlowResult:
    time: datetime
    qw_mw: float
    qs_mw: float
    q_total_mw: float


class HeatFlowCalculationModel:
    """Heat-flow calculator based on IAPWS-IF97 properties from seuif97."""

    def calculate(self, data: HeatFlowInput) -> HeatFlowResult:
        try:
            water_enthalpy_kj_kg = seuif97.pt2h(data.p1_mpa, data.t1_c)
            steam_enthalpy_kj_kg = seuif97.pt2h(data.p2_mpa, data.t2_c)
        except (ArithmeticError, OverflowError, ValueError) as error:
            raise ValueError("压力或温度超出 seuif97 的有效计算范围") from error

        qw_mw = data.w1_kg_s * water_enthalpy_kj_kg / 1000
        qs_mw = data.w2_kg_s * steam_enthalpy_kj_kg / 1000
        return HeatFlowResult(
            time=data.time,
            qw_mw=round(qw_mw, 4),
            qs_mw=round(qs_mw, 4),
            q_total_mw=round(qw_mw + qs_mw, 4),
        )
