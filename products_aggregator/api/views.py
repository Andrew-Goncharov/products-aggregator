from typing import Literal, Optional
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, validator, root_validator, NonNegativeInt
from pydantic.validators import datetime
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from starlette.responses import JSONResponse
from products_aggregator.database import actions
from uuid import UUID
from products_aggregator.database.actions import insert, get_many

app = FastAPI()

engine = create_engine("postgresql://postgres:p2k8zR347@localhost:5432/postgres")


def calculate_average_price(node: dict) -> tuple[int, int]:     # (price, sum_count)
    if node["type"] == "OFFER":
        return node["price"], 1

    total_price = 0
    total_count = 0
    for child in node["children"]:
        price, count = calculate_average_price(child)
        total_price += price
        total_count += count

    node["price"] = total_price // total_count
    return total_price, total_count


def map_node(node_db: dict) -> dict:
    return {
        "id": node_db["id"],
        "name": node_db["name"],
        "type": node_db["type"],
        "parentId": node_db["parent_id"],
        "date": node_db["updated_dt"].strftime('%Y-%m-%dT%H:%M:%SZ'),
        "price": node_db["price"] if node_db["type"] == "OFFER" else None,
        "children": None if node_db["type"] == "OFFER" else []
    }


def create_get_node_result(nodes: list[dict], root_node_id: str) -> dict:
    id_to_node = dict()
    for node in nodes:
        id_to_node[node["id"]] = map_node(node)

    for node in id_to_node.values():
        if node["id"] == root_node_id:
            continue
        parent_node = id_to_node[node["parentId"]]
        parent_node["children"].append(node)

    root_node = id_to_node[root_node_id]
    calculate_average_price(root_node)

    return root_node


def get_connection():
    with engine.connect() as connection:
        with connection.begin():
            yield connection


def is_valid_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except Exception:
        return False


class Item(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID]
    type: Literal["OFFER", "CATEGORY"]
    price: Optional[NonNegativeInt]

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

        for item in v:
            if item["parentId"] in (all_ids - category_ids):
                # item["parentId"] not in category_ids and item["parentId"] is not None:
                raise ValueError("parentId does not belong to category ids.")
        return v


def map_db_node(item: Item, update_date: datetime) -> dict:
    return {
        "id": item.id,
        "parent_id": item.parentId,
        "name": item.name,
        "price": item.price,
        "updated_dt": update_date,
        "type": item.type
    }


def map_db_nodes(request: ImportRequest) -> list[dict]:
    result = []
    update_date = request.updateDate
    for item in request.items:
        result.append(map_db_node(item, update_date))
    return result


def insert_type_validation(nodes: list[dict], connection: Connection = Depends(get_connection)) -> bool:
    id_to_node = dict()
    for node in nodes:
        id_to_node[node["id"]] = node
    available_nodes = get_many(list(id_to_node.keys()), connection)
    for node in available_nodes:
        curr_node = id_to_node[node["id"]]
        for key in node.keys():
            if not isinstance(curr_node[key], type(node[key])):
                return False
    return True


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
          "code": 400,
          "message": "Validation Failed"
        }
    )


@app.post("/imports")
def imports(request: ImportRequest, connection: Connection = Depends(get_connection)):
    data = map_db_nodes(request)

    if type(item[key]) != type(pattern[key]):
        JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "Validation Failed"
            }
        )

    insert(imported_data, connection)


@app.delete("/delete/{node_id}")
def delete(node_id: str, connection: Connection = Depends(get_connection)):
    if not is_valid_uuid(node_id):
        return JSONResponse(
            status_code=400,
            content={
              "code": 400,
              "message": "Validation Failed"
            }
        )

    result = actions.get_many([node_id], connection)

    if len(result) == 0:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "Item not found"
            },
        )

    actions.delete(node_id, connection)


@app.get("/nodes/{node_id}")
def get(node_id: str, connection: Connection = Depends(get_connection)):
    # if not is_valid_uuid(node_id): # Invalid id
    #     return JSONResponse(
    #         status_code=400,
    #         content={
    #           "code": 400,
    #           "message": "Validation Failed"
    #         }
    #     )

    result = actions.get_recursive(node_id, connection)

    if len(result) == 0:            # Nothing found
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "Item not found"
            },
        )

    return JSONResponse(
        status_code=200,
        content=create_get_node_result(result, node_id)
    )
