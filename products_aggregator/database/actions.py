from sqlalchemy.engine import Connection

from products_aggregator.database import schema


def delete(node_id: str, connection: Connection) -> None:    # delete parent -> delete all children test
    query = schema.nodes_table.delete().where(schema.nodes_table.c.id == node_id)
    connection.execute(query)


def update():
    pass


def insert(data: list, connection: Connection) -> None:
    for obj in data:
        pass
        # query = schema.nodes_table.insert()


def get_data():
    pass


def exists(node_id: str, connection: Connection) -> bool:
    pass
