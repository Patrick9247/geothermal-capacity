from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class CalculationRecord(Base):
    __tablename__ = "calculation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(50))
    thermal_energy_gj: Mapped[float] = mapped_column(Float)
    electrical_power_mw: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class HeatFlowRecord(Base):
    __tablename__ = "heat_flow_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="记录序号")
    time: Mapped[datetime] = mapped_column(DateTime, index=True, comment="时间（time）")
    p1_mpa: Mapped[float] = mapped_column(Float, comment="P1（地热水压力 MPa）")
    t1_c: Mapped[float] = mapped_column(Float, comment="T1（地热水温度 ℃）")
    p2_mpa: Mapped[float] = mapped_column(Float, comment="P2（地热蒸汽压力 MPa）")
    t2_c: Mapped[float] = mapped_column(Float, comment="T2（地热蒸汽温度 ℃）")
    w1_kg_s: Mapped[float] = mapped_column(Float, comment="W1（地热水质量流量 kg/s）")
    w2_kg_s: Mapped[float] = mapped_column(Float, comment="W2（地热蒸汽质量流量 kg/s）")
    qw_mw: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Qw（地热水热流量 MW）")
    qs_mw: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Qs（地热蒸汽热流量 MW）")
    q_total_mw: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Q总（总产能：Qw + Qs，MW）")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
