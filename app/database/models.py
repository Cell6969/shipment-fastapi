from datetime import datetime
from typing import ClassVar
from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from enum import Enum


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment" #type:ignore

    # auto generated id by None and Primary Key
    id: int = Field(default=None, primary_key=True)
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime


class Seller(SQLModel, table=True):
    __tablename__ = "seller" #type:ignore

    id: int = Field(default=None, primary_key=True)
    name: str
    email: EmailStr
    password: str
