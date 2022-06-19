from sqlalchemy import create_engine

from products_aggregator.database.actions import delete, insert, update, get_many, get_recursive

import datetime

engine = create_engine("postgresql://postgres:p2k8zR347@localhost:5432/postgres")

# delete("0", engine.connect())

# # id != parent_id -> check

# insert([{"id": "0", "parent_id": None, "name": "category", "price": 100, "updated_dt": datetime.datetime.now(), "type": "category"},
#         {"id": "1", "parent_id": "0", "name": "product", "price": 100, "updated_dt": datetime.datetime.now(), "type": "product"},
#         {"id": "2", "parent_id": "0", "name": "product", "price": 100, "updated_dt": datetime.datetime.now(), "type": "product"},
#         {"id": "3", "parent_id": "2", "name": "product", "price": 100, "updated_dt": datetime.datetime.now(), "type": "product"},
#         {"id": "4", "parent_id": "2", "name": "product", "price": 100, "updated_dt": datetime.datetime.now(), "type": "product"}], engine.connect())

# update("0", {"price": 400}, engine.connect())
# update("0", {"id": "0", "parent_id": None, "name": "category", "price": 400, "updated_dt": datetime.datetime.now(), "type": "category"}, engine.connect())

# print(exists("0", engine.connect()))
# print(get_many(["1", "2"], engine.connect()))

# print(get_recursive("0", engine.connect()))


if __name__ == "__main__":
    pass
