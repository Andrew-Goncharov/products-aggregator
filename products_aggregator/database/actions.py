from sqlalchemy import text
from sqlalchemy.engine import Connection
from database import schema
from sqlalchemy.dialects import postgresql


def delete(node_id: str, connection: Connection) -> None:
    query = schema.nodes_table.delete().where(schema.nodes_table.c.id == node_id)
    connection.execute(query)


def insert(nodes: list[dict], connection: Connection) -> None:
    query = postgresql.insert(schema.nodes_table)
    query = query.on_conflict_do_update(
        index_elements=[schema.nodes_table.c.id],
        set_=dict(query.excluded)
    )
    connection.execute(query, nodes)


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

