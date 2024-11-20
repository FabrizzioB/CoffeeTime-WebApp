import uvicorn
from app import app
from app.db.connection import create_db_pool, close_db_pool

@app.on_event("startup")
async def startup_event():
    print("Initializing database pool...")
    await create_db_pool()
    print("Database pool initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Closing database pool...")
    await close_db_pool()
    print("Database pool closed.")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
