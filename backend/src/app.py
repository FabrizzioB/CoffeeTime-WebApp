import uvicorn
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, PlainTextResponse, JSONResponse
from pydantic import BaseModel

from coffee import *
from security import *

app = FastAPI(title="CoffeeTime",
              description="FastAPI based web application for managing a team's coffee purchases.",
              version="0.1",
              terms_of_service="http://127.0.0.1:8000/terms",
              contact={"name": "Fabri", "email": "ffpbrandao@gmail.com"})

# Define the directories for static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# The Member class defines the structure of the data related to each team member
class Member(BaseModel):
    name: str
    coffees: int = 0  # Default value set to 0

# Pydantic model for updating
class MemberUpdate(BaseModel):
    name: str
    coffees: int

""" Connections """

# Lifespan event for managing database connection
@app.on_event("startup")
async def startup():
    await create_db_pool()  # Initialize the database connection

@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()  # Shutdown the database connection

""" Routes """

# Route for adding a home page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route for SPA page
@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for adding a member page
@app.get("/add", response_class=HTMLResponse)
async def add_member_page(request: Request):
    return templates.TemplateResponse("add_member.html", {"request": request})

# Route for updating coffee count page
@app.get("/update", response_class=HTMLResponse)
async def update_coffee_page(request: Request):
    return templates.TemplateResponse("update_coffee.html", {"request": request})

# Route for deleting a member page
@app.get("/delete", response_class=HTMLResponse)
async def delete_member_page(request: Request):
    return templates.TemplateResponse("delete_member.html", {"request": request})

# Route to view team members
@app.get("/team", response_class=HTMLResponse)
async def team_members_page(request: Request):
    return templates.TemplateResponse("team_members.html", {"request": request})

# Route to view sort member
@app.get("/sort", response_class=HTMLResponse)
async def sort_member_page(request: Request):
    return templates.TemplateResponse("sort_member.html", {"request": request})

# Route to view sort member
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Implementing the login route for the application.

    Login route:
    - Verify if the username already exists.
    - Generate a JWT token upon successful login.
    """
    return templates.TemplateResponse("login.html", {"request": request})

# Route to view sort member
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    Implementing the registration route for the application.

    Registration route:
    - Check if the user already exists.
    - Hash the password before storing it in the database.
    """
    return templates.TemplateResponse("register.html", {"request": request})


""" Methods """

# Insert new member
@app.put("/add")
async def add_new_member(member: Member):
    try:
        # Check if the member exists in the database
        if await check_member_exists(member.name):
            raise HTTPException(status_code=400, detail=f"Member {member.name} already exists.")

        # Insert the new member
        await insert_member(member.name, member.coffees)
        return PlainTextResponse(content=f"New member was added: {member.name} with {member.coffees} coffees.")

    except Exception as http_exc:
        raise http_exc
    except Exception as e:
        # Handle unexpected exceptions
        raise HTTPException(status_code=500, detail=f"An error has occurred: {str(e)}")

# Delete team member
@app.delete("/delete/{name}")
async def remove_member(name: str):
    success = await delete_member(name)

    if success:
        return PlainTextResponse(content=f"Member {name} was deleted successfully.")
    else:
        return PlainTextResponse(content=f"Failed to delete member {name}.", status_code=404)

# Increment the coffee count for a team member by a specific number
@app.put("/add-coffee/{name}/{number}")
async def increment_coffees(name: str, number: int):
    try:
        member_exists = await check_member_exists(name)

        if not member_exists:
            return PlainTextResponse(content=f"Error: Member {name} not found.", status_code=404)
        if number < 0:
            return PlainTextResponse(content="Error: Coffee count cannot be negative.", status_code=400)
        await update_coffee(name, number)
        return PlainTextResponse(content=f"Coffee count incremented by {number} for {name}.")
    except Exception as e:
        return PlainTextResponse(content=f"Error updating coffee count: {str(e)}", status_code=500)

# Reset the coffee count for a team member
@app.put("/remove-coffee")
async def remove_coffees(member: Member):
    await remove_coffee(member.name)
    return PlainTextResponse(content=f"Coffee count reset for {member.name}.")

# Showcase all team members and their coffee counts
@app.get("/team-members", response_model=list[Member])
async def team_members():
    team_member = await show_team_members()
    return JSONResponse(content={"team_members": team_member})

# Showcase all team members
@app.get("/team-members-names")
async def team_members_names():
    team_members_name = await show_team_members_names()
    team_members_str = json.dumps({"team_members": team_members_name}, indent=2)
    return PlainTextResponse(content=team_members_str)

# Sort the member with the most coffee's paid
@app.get("/sort-most")
async def sort_most_coffee_payer():
    sorted_name = await sort_most_coffees()
    sort_most_coffee_str = json.dumps({"most_coffees_paid": sorted_name}, indent=2)
    return PlainTextResponse(content=sort_most_coffee_str)

# Sort the member with the least coffee's paid
@app.get("/sort-least")
async def sort_least_coffee_payer():
    sorted_name = await sort_least_coffees()
    sort_least_coffee_str = json.dumps({"least_coffees_paid": sorted_name}, indent=2)
    return PlainTextResponse(content=sort_least_coffee_str)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

