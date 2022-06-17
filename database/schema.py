from sqlalchemy import (
    Column, Date, Enum as PgEnum, ForeignKey, ForeignKeyConstraint, Integer,
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


products_table = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("parentId", Integer, ForeignKey("categories.id"), nullable=True),
    Column("productName", String, nullable=False),
    Column("price", Integer, nullable=False),
    Column("date", Date, nullable=False),
)

categories_table = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("parentId", Integer, ForeignKey("categories.id"), nullable=False),
    Column("categoryName", String, nullable=False),
    Column("price", Integer, nullable=False),
    Column("date", Date, nullable=False),
)