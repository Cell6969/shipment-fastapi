from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.schemas.schemas import ShipmentCreate, ShipmentUpdate, ShipmentUpdatePartial
from app.database.models import Shipment
from app.database.models import ShipmentStatus
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.helper.datetimeconversion import to_naive_utc

class ShipmentService:
    def __init__(self, session:AsyncSession):
        self.session = session

    async def list(self) -> Sequence[Shipment]:
        results = await self.session.execute(select(Shipment))
        return results.scalars().all()

    async def add(self, shipment_create:ShipmentCreate) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.utcnow() + timedelta(days=3)
        )
        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)

        return new_shipment

    async def get(self, id:int) -> Shipment:
        shipment = await self.session.get(Shipment, id)
        if shipment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="shipment is not found")
        return shipment

    async def update(self, id:int, shipment_update:ShipmentUpdate) -> Shipment:
        shipment = await self.get(id)
        data = shipment_update.model_dump()
        if "estimated_delivery" in data:
            data["estimated_delivery"] = to_naive_utc(data["estimated_delivery"])
        shipment.sqlmodel_update(data)
        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)

        return shipment

    async def update_partial(self, id:int, shipment_update_partial:ShipmentUpdatePartial) -> Shipment:
        shipment = await self.get(id)
        update = shipment_update_partial.model_dump(exclude_none=True)
        if "estimated_delivery" in update:
            update["estimated_delivery"] = to_naive_utc(update["estimated_delivery"])
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="no data provided"
            )
        shipment.sqlmodel_update(update)
        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)

        return shipment

    async def delete(self, id:int) -> None:
        shipment = await self.get(id)
        await self.session.delete(shipment)
        await self.session.commit()