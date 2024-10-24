import uvicorn
import json

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, PlainTextResponse, JSONResponse
from pydantic import BaseModel

from coffee import *

app = FastAPI()

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

# Lifespan event for managing database connection
@app.on_event("startup")
async def startup():
    global connection
    connection = await connect_to_db()  # Establish DB connection when app starts
    if connection is None:
        print("Failed to establish database connection.")
    else:
        print("Database connection established!")

@app.on_event("shutdown")
async def shutdown():
    global connection
    if connection:
        await connection.close()  # Cleanly close the DB connection
        print("Database connection closed.")

# Insert new member
@app.put("/add")
async def add_new_member(member: Member):
    global connection
    await insert_member(connection, member.name, member.coffees)
    return PlainTextResponse(content=f"New member was added: {member.name} with {member.coffees} coffees.")

# Delete team member
@app.delete("/delete/{name}")
async def remove_member(name: str):
    global connection
    if connection is None:
        return PlainTextResponse(content="Error: No database connection.", status_code=500)

    success = await delete_member(connection, name)
    if success:
        return PlainTextResponse(content=f"Member {name} was deleted successfully.")
    else:
        return PlainTextResponse(content=f"Failed to delete member {name}.", status_code=404)

# Increment the coffee count for a team member
@app.put("/add-coffee")
async def increment_one_coffee(member: Member):
    global connection
    if connection is None:
        return PlainTextResponse(content="Error: No database connection.", status_code=500)
    await add_one_coffee(connection, member.name)
    return PlainTextResponse(content=f"Coffee count incremented for {member.name}.")

# Increment the coffee count for a team member by a specific number
@app.put("/add-coffee/{name}/{number}")
async def increment_coffees(name: str, number: int):
    global connection
    if connection is None:
        return PlainTextResponse(content="Error: No database connection.", status_code=500)
    try:
        member_exists = await check_member_exists(connection, name)
        if not member_exists:
            return PlainTextResponse(content=f"Error: Member {name} not found.", status_code=404)
        if number < 0:
            return PlainTextResponse(content="Error: Coffee count cannot be negative.", status_code=400)
        await add_multiple_coffees(connection, name, number)
        return PlainTextResponse(content=f"Coffee count incremented by {number} for {name}.")
    except Exception as e:
        return PlainTextResponse(content=f"Error updating coffee count: {str(e)}", status_code=500)

# Reset the coffee count for a team member
@app.put("/remove-coffee")
async def remove_coffees(member: Member):
    global connection
    if connection is None:
        return PlainTextResponse(content="Error: No database connection.", status_code=500)
    await remove_coffee(connection, member.name)
    return PlainTextResponse(content=f"Coffee count reset for {member.name}.")

# Showcase all team members
@app.get("/team-members-names")
async def team_members_names(request: Request):
    global connection
    team_members_name = await show_team_members_names(connection)
    team_members_str = json.dumps({"team_members": team_members_name}, indent=2)
    return PlainTextResponse(content=team_members_str)

# Showcase all team members and their coffee counts
@app.get("/team-members", response_model=list[Member])
async def team_members(request: Request):
    global connection
    team_member = await show_team_members(connection)
    return JSONResponse(content={"team_members": team_member})

# Sort the member with the least coffee's paid
@app.get("/sort-least")
async def sort_least_coffee_payer(request: Request):
    global connection
    sorted_name = await sort_least_coffees(connection)
    sort_least_coffee_str = json.dumps({"least_coffees_paid": sorted_name}, indent=2)
    return PlainTextResponse(content=sort_least_coffee_str)

# Sort the member with the most coffee's paid
@app.get("/sort-most")
async def sort_most_coffee_payer(request: Request):
    global connection
    sorted_name = await sort_most_coffees(connection)
    sort_most_coffee_str = json.dumps({"most_coffees_paid": sorted_name}, indent=2)
    return PlainTextResponse(content=sort_most_coffee_str)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
