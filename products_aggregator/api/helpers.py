from uuid import UUID
from pydantic.validators import datetime
from sqlalchemy.engine import Connection
from database.actions import get_many
# from api.models import Item, ImportRequest
import datetime as dt


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


def map_api_node(node_db: dict) -> dict:
    return {
        "id": node_db["id"],
        "name": node_db["name"],
        "type": node_db["type"],
        "parentId": node_db["parent_id"],
        "date": format_datetime(node_db["updated_dt"]),
        "price": node_db["price"] if node_db["type"] == "OFFER" else None,
        "children": None if node_db["type"] == "OFFER" else []
    }


def create_get_node_result(nodes: list[dict], root_node_id: UUID) -> dict:
    id_to_node = dict()
    for node in nodes:
        id_to_node[node["id"]] = map_api_node(node)

    for node in id_to_node.values():
        if node["id"] == str(root_node_id):
            continue
        parent_node = id_to_node[node["parentId"]]
        parent_node["children"].append(node)

    root_node = id_to_node[str(root_node_id)]
    calculate_price_date(root_node)

    return root_node


def map_db_node(item, update_date: datetime) -> dict:   # item: Item
    return {
        "id": str(item.id),
        "parent_id": str(item.parentId) if item.parentId is not None else item.parentId,
        "name": item.name,
        "price": item.price,
        "updated_dt": update_date,
        "type": item.type
    }


def map_db_nodes(request) -> list[dict]:    # request: ImportRequest
    result = []
    update_date = request.updateDate
    for item in request.items:
        result.append(map_db_node(item, update_date))
    return result


def insert_type_validation(nodes: list[dict], connection: Connection) -> bool:
    id_to_node = dict()
    for node in nodes:
        id_to_node[node["id"]] = node
    available_nodes = get_many(list(id_to_node.keys()), connection)
    for node in available_nodes:
        curr_node = id_to_node[node["id"]]
        if curr_node["type"] != node["type"]:
            return False
    return True


def insert_parent_type_validation(nodes: list[dict], connection: Connection) -> bool:
    parent_ids = [node["parent_id"] for node in nodes]
    available_nodes = get_many(parent_ids, connection)
    for node in available_nodes:
        if node["type"] != "CATEGORY":
            return False
    return True


def is_valid_datetime(value: str) -> bool:
    try:
        dt.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.000Z')
        return True
    except Exception:
        return False

