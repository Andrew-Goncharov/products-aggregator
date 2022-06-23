from random import randint

from sqlalchemy import create_engine
from products_aggregator.database.actions import delete, insert, get_many, get_recursive
from uuid import uuid4

from pprint import pprint
import json
import datetime

engine = create_engine("postgresql://postgres:p2k8zR347@localhost:5432/postgres")

# delete("4e50b7e5-1585-4260-b068-12d0942da745", engine.connect())
# delete("c463eaad-24ce-49e4-81bb-3208bd0e8b67", engine.connect())

# # id != parent_id -> check
#
# ids = [str(uuid4()) for _ in range(10)]
# prices = [randint(0, 1000) for _ in range(10)]

# insert([{"id": ids[0], "parent_id": None,   "name": "category_0", "price": prices[0], "updated_dt": datetime.datetime.now(), "type": "CATEGORY"},
#         {"id": ids[1], "parent_id": ids[0], "name": "product_1",  "price": prices[1], "updated_dt": datetime.datetime.now(), "type": "OFFER"},
#         {"id": ids[2], "parent_id": ids[0], "name": "category_2", "price": prices[2], "updated_dt": datetime.datetime.now(), "type": "CATEGORY"},
#         {"id": ids[3], "parent_id": ids[2], "name": "product_3",  "price": prices[3], "updated_dt": datetime.datetime.now(), "type": "OFFER"},
#         {"id": ids[4], "parent_id": ids[2], "name": "product_4",  "price": prices[4], "updated_dt": datetime.datetime.now(), "type": "OFFER"}], engine.connect())

#
# insert([{"id": "5596a3d1-e57b-4709-8801-6999db92b666", "parent_id": None, "name": "category_2_updated",  "price": prices[4], "updated_dt": datetime.datetime.now(), "type": "CATEGORY"}], engine.connect())

# update("0", {"price": 400}, engine.connect())
# update("0", {"id": "0", "parent_id": None, "name": "category", "price": 400, "updated_dt": datetime.datetime.now(), "type": "category"}, engine.connect())

# print(exists("0", engine.connect()))
# print(get_many(["1", "2"], engine.connect()))

# data = get_recursive("4", engine.connect())
# pprint(data)
#
# print(len(data))

# def test(data: list):
#
#     if len(data) == 0:
#         pass
#     elif len(data) == 1:
#         pass
#     else:
#         average_price = 0
#         total_price = 0
#         count = len(data)
#
#         for row in reversed(data):
#             curr_id = row["parent_id"]



#
#
# def date_info(date):
#     if isinstance(date, datetime.datetime):
#         return date.__str__()
#
#
# print(json.dumps(data, default=date_info))

#
# print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'))
# print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),)

# .toISOString()
# datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

if __name__ == "__main__":
    pass
