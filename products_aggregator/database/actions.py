from sqlalchemy import text
from sqlalchemy.engine import Connection
from products_aggregator.database import schema
import datetime


def delete(node_id: str, connection: Connection) -> None:    # delete parent -> delete all children test
    query = schema.nodes_table.delete().where(schema.nodes_table.c.id == node_id)
    connection.execute(query)


def update(node: dict, connection: Connection) -> None:
    node["updated_dt"] = datetime.datetime.now()
    query = schema.nodes_table.update().values(node).where(schema.nodes_table.c.id == node["id"])
    connection.execute(query)


def insert(nodes: list[dict], connection: Connection) -> None:
    for node in nodes:
        node["updated_dt"] = datetime.datetime.now()
    connection.execute(schema.nodes_table.insert(), nodes)


def get_recursive(node_id: str, connection: Connection) -> list[dict]:
    query = text("""
        WITH RECURSIVE recursive_nodes AS (
            SELECT * FROM nodes WHERE nodes.id = :node_id
        
            UNION
        
            SELECT nodes.* FROM nodes
            JOIN recursive_nodes ON nodes.parent_id = recursive_nodes.id
        )
        
        SELECT * FROM recursive_nodes;
    """)
    return [dict(row) for row in connection.execute(query, {'node_id': node_id})]


def get_many(node_ids: list[str], connection: Connection) -> list[dict]:
    query = schema.nodes_table.select().where(schema.nodes_table.c.id.in_(node_ids))
    return [dict(row) for row in connection.execute(query)]

