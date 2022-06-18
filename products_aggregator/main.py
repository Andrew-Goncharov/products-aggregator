from sqlalchemy import create_engine

from products_aggregator.database.actions import delete

engine = create_engine("postgresql://postgres:p2k8zR347@localhost:5432/postgres")

delete("0", engine.connect())

if __name__ == "__main__":
    pass
