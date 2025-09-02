from typing import cast
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager

from app.database.session import create_db_tables
from app.api.router import master_router

@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    # await create_db_tables() # non-active it because it can run schema db
    yield

app = FastAPI(lifespan=lifespan_handler)

# include router
app.include_router(master_router)


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=cast("str", app.openapi_url),
        title="Scalar API"
    )