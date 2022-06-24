from uuid import UUID

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from starlette.responses import JSONResponse

from products_aggregator.api.helpers import map_db_nodes, insert_type_validation, create_get_node_result, \
    insert_parent_type_validation
from products_aggregator.api.models import ImportRequest
from products_aggregator.database import actions
from products_aggregator.database.actions import insert
import sqlalchemy

app = FastAPI()

engine = create_engine("postgresql://postgres:p2k8zR347@localhost:5432/postgres")


def get_connection():
    with engine.connect() as connection:
        with connection.begin():
            yield connection


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
          "code": 400,
          "message": "Validation Failed"
        }
    )


@app.exception_handler(sqlalchemy.exc.IntegrityError)
def exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
          "code": 400,
          "message": "Validation Failed"
        }
    )


@app.post("/imports")
def imports(request: ImportRequest, connection: Connection = Depends(get_connection)):
    data = map_db_nodes(request)
    if not insert_type_validation(data, connection) or not insert_parent_type_validation(data, connection):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "Validation Failed"
            }
        )
    insert(data, connection)


@app.delete("/delete/{node_id}")
def delete(node_id: UUID, connection: Connection = Depends(get_connection)):
    result = actions.get_many([str(node_id)], connection)
    if len(result) == 0:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "Item not found"
            },
        )
    actions.delete(str(node_id), connection)


@app.get("/nodes/{node_id}")
def get(node_id: UUID, connection: Connection = Depends(get_connection)):
    result = actions.get_recursive(str(node_id), connection)
    if len(result) == 0:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "Item not found"
            },
        )

    return JSONResponse(
        status_code=200,
        content=create_get_node_result(result, node_id)
    )
