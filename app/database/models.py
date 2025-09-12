from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Column, Field, Relationship, SQLModel, col, select
from enum import Enum
from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlalchemy import ARRAY, INTEGER
from collections.abc import Sequence


# MANY TO MANY
class ShipmentTag(SQLModel, table=True):
    __tablename__ = "shipment_tag"  # type:ignore

    shipment_id: UUID = Field(foreign_key="shipment.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)


class TagName(str, Enum):
    EXPRESS = "express"
    STANDARD = "standard"
    FRAGILE = "fragile"
    HEAVY = "heavy"
    INTERNATIONAL = "international"
    DOMESTIC = "domestic"
    TEMPERATURE_CONTROLLED = "temperature_controlled"
    GIFT = "gift"
    RETURN = "return"
    DOCUMENTS = "documents"

    async def tag(self, session: AsyncSession):
        return await session.scalar(select(Tag).where(Tag.name == self.value))


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # type:ignore

    # auto generated id by uuid and Primary Key
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    # property
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)

    content: str
    weight: float = Field(le=25)
    destination: int
    estimated_delivery: datetime

    timeline: list["ShipmentEvent"] = Relationship(
        back_populates="shipment", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def status(self):
        return self.timeline[-1].status if len(self.timeline) > 0 else None

    # Seller
    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Partner
    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Reviews
    review: "Review" = Relationship(
        back_populates="shipment", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Tags
    tags: list["Tag"] = Relationship(
        back_populates="shipments",
        link_model=ShipmentTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_event"  # type:ignore

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    location: int
    status: ShipmentStatus
    description: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: "Shipment" = Relationship(
        back_populates="timeline", sa_relationship_kwargs={"lazy": "selectin"}
    )


class User(SQLModel):
    name: str
    email: EmailStr
    email_verified: bool = Field(default=False)
    password: str = Field(exclude=True)


class Seller(User, table=True):
    __tablename__ = "seller"  # type:ignore

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    address: str | None = Field(default=None)
    zip_code: int | None = Field(default=None)

    shipments: list[Shipment] = Relationship(
        back_populates="seller", sa_relationship_kwargs={"lazy": "selectin"}
    )


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"  # type:ignore

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    serviceable_zip_codes: Sequence[int] = Field(sa_column=Column(ARRAY(INTEGER)))

    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(
        back_populates="delivery_partner", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def active_shipment(self) -> list[Shipment]:
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
            or shipment.status != ShipmentStatus.cancelled
        ]

    @property
    def current_handling_capacity(self) -> int:
        return self.max_handling_capacity - len(self.active_shipment)


class Review(SQLModel, table=True):
    __tablename__ = "review"  # type:ignore

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(
        back_populates="review", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Tag(SQLModel, table=True):
    __tablename__ = "tag"  # type:ignore

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    name: TagName
    instruction: str

    shipments: list[Shipment] = Relationship(
        back_populates="tags",
        link_model=ShipmentTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
