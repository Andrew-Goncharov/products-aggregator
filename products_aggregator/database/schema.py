from sqlalchemy import (
    Column, DateTime,  ForeignKey, Integer,
    MetaData, String, Table,
)

convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)

nodes_table = Table(
    "nodes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("parent_id", Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=True),
    Column("name", String, nullable=False),
    Column("price", Integer, nullable=True),
    Column("updated_dt", DateTime, nullable=False),
    Column("type", String, nullable=False)
)