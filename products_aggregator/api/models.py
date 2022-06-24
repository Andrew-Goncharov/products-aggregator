from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, NonNegativeInt, root_validator, validator
from pydantic.validators import datetime

from products_aggregator.api.helpers import is_valid_datetime


class Item(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID]
    price: Optional[NonNegativeInt]
    type: Literal["OFFER", "CATEGORY"]

    def __getitem__(self, item):
        return getattr(self, item)

    @root_validator
    def price_validator(cls, values):
        if "type" not in values:
            raise ValueError("Type is missing.")

        if values["type"] == "OFFER" and values["price"] is None:
            raise ValueError("Unacceptable price value for offer: Null.")
        if values["type"] == "CATEGORY" and values["price"] is not None:
            raise ValueError("Unacceptable price value for category: not Null.")
        return values


class ImportRequest(BaseModel):
    items: list[Item]
    updateDate: datetime

    @validator("items")
    def items_validator(cls, v):
        all_ids = set()
        category_ids = set()
        for item in v:
            if item["id"] not in all_ids:
                all_ids.add(item["id"])
                if item["type"] == "CATEGORY":
                    category_ids.add(item["id"])
            else:
                raise ValueError("Non-unique values exist.")
        offer_ids = all_ids - category_ids
        for item in v:
            if item["parentId"] in offer_ids:
                raise ValueError("parentId does not belong to category ids.")
        return v

    @validator("updateDate", pre=True)
    def updateDate_validator(cls, v):
        if not isinstance(v, str) or not is_valid_datetime(v):
            raise ValueError("Invalid datetime value.")
        return v