import json
import logging

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from starlette.responses import JSONResponse
from products_aggregator.database import actions
from uuid import UUID


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
    with engine.connect() as connection:  # context manager
        with connection.begin():
            yield connection


def is_valid_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except Exception:
        return False


@app.post("/imports")
def imports():
    pass


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
