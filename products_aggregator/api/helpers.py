from uuid import UUID
from fastapi import Depends
from pydantic.validators import datetime
from products_aggregator.api.models import Item, ImportRequest

from sqlalchemy.engine import Connection
from products_aggregator.api.views import get_connection
from products_aggregator.database.actions import get_many


def calculate_price_date(node: dict) -> tuple[int, int, str]:
    if node["type"] == "OFFER":
        return node["price"], 1, node["date"]

    total_price = 0
    total_count = 0
    max_date = node["date"]
    for child in node["children"]:
        price, count, date = calculate_price_date(child)
        total_price += price
        total_count += count
        max_date = max(max_date, date)

    node["price"] = total_price // total_count
    node["date"] = max_date
    return total_price, total_count, max_date


def format_datetime(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def map_node(node_db: dict) -> dict:
    return {
        "id": node_db["id"],
        "name": node_db["name"],
        "type": node_db["type"],
        "parentId": node_db["parent_id"],
        "date": format_datetime(node_db["updated_dt"]),
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
    calculate_price_date(root_node)

    return root_node


def is_valid_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except Exception:
        return False


def map_db_node(item: Item, update_date: datetime) -> dict:
    return {
        "id": str(item.id),
        "parent_id": str(item.parentId) if item.parentId is not None else item.parentId,
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
