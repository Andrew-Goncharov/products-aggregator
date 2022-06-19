from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from starlette.responses import JSONResponse

from products_aggregator.database import actions

app = FastAPI()

engine = create_engine("postgresql://postgres:p2k8zR347@localhost:5432/postgres")


def get_connection():
    with engine.connect() as connection:  # context manager
        with connection.begin():
            yield connection


@app.delete("/delete/{node_id}")
def delete(node_id: str, connection: Connection = Depends(get_connection)):  # change type -> uuid
    result = actions.get_many([node_id], connection)
    if len(result) == 0:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "Item not found"
            },
        )  # create json

    actions.delete(node_id, connection)
    # return {"item_id": item_id}
