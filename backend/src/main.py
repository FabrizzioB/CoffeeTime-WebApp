import time
import docker
import uvicorn
import signal
import sys

from app import app
from app.db.connection import create_db_pool, close_db_pool

# Initialize the Docker client
client = docker.from_env()

# Specify the container name or ID to start
container_name = "mysql_coffee"

def stop_container():
    try:
        # Stop the container if it is running
        container = client.containers.get(container_name)
        if container.status == "running":
            container.stop()
            print(f"Container {container_name} stopped successfully.")
    except docker.errors.NotFound:
        print(f"Container {container_name} not found for stopping.")
    except Exception as e:
        print(f"An error occurred while stopping the container: {e}")

def handle_exit(signal, frame):
    print("Script is exiting. Cleaning up...")
    stop_container()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # Handle termination signals

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
    try:
        # Start the container
        container = client.containers.get(container_name)
        container.start()
        print(f"Container {container_name} started successfully.")

        # Sleep for a specified duration
        sleep_duration = 3  # Time in seconds
        print(f"Catching some ZZZzzzZZZ just wait {sleep_duration} seconds...")
        time.sleep(sleep_duration)

        uvicorn.run(app, host="127.0.0.1", port=8000)
    except docker.errors.NotFound:
        print(f"Container {container_name} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
