from contextlib import asynccontextmanager
from fastapi import FastAPI

from rich import print, panel

@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    print(panel.Panel("Server started....", style="bold green"))
    yield
    print(panel.Panel("Server stopped....", style="bold red"))


app = FastAPI(lifespan=lifespan_handler)

@app.get("/")
def read_root():
    return {"Hello": "World"}
