import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.src.app.routes import api, pages
from backend.src.app.db.connection import create_db_pool, close_db_pool

app = FastAPI(
    title="CoffeeTime",
    description="FastAPI based web application for managing a team's coffee purchases.",
    version="0.1",
    terms_of_service="http://127.0.0.1:8000/terms",
    contact={"name": "Fabri", "email": "ffpbrandao@gmail.com"}
)

# Register the routes for api and pages
app.include_router(api.router)
app.include_router(pages.router)

# Mount the static files and set the templates path
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


""" Connections """

# Lifespan event for managing database connection
@app.on_event("startup")
async def startup():
    await create_db_pool()  # Initialize the database connection

@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()  # Shutdown the database connection