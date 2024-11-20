import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

from backend.src.app.models.member import Member
from backend.src.app.crud.crud import *

router = APIRouter()


# Insert new member
@router.put("/add")
async def add_new_member(member: Member):
    try:
        if await check_member_exists(member.name):
            raise HTTPException(status_code=400, detail=f"Member {member.name} already exists.")
        await insert_member(member.name, member.coffees)
        return PlainTextResponse(content=f"New member was added: {member.name} with {member.coffees} coffees.")
    except Exception as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error has occurred: {str(e)}")

# Delete team member
@router.delete("/delete/{name}")
async def remove_member(name: str):
    success = await delete_member(name)
    if success:
        return PlainTextResponse(content=f"Member {name} was deleted successfully.")
    else:
        return PlainTextResponse(content=f"Failed to delete member {name}.", status_code=404)

# Increment the coffee count for a team member by a specific number
@router.put("/add-coffee/{name}/{number}")
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
@router.put("/remove-coffee")
async def remove_coffees(member: Member):
    await remove_coffee(member.name)
    return PlainTextResponse(content=f"Coffee count reset for {member.name}.")

# Showcase all team members and their coffee counts
@router.get("/team-members", response_model=list[Member])
async def team_members():
    team_member = await show_team_members()
    return JSONResponse(content={"team_members": team_member})

# Showcase all team members
@router.get("/team-members-names")
async def team_members_names():
    team_members_name = await show_team_members_names()
    team_members_str = json.dumps({"team_members": team_members_name}, indent=2)
    return PlainTextResponse(content=team_members_str)

# Sort the member with the most coffee's paid
@router.get("/sort-most")
async def sort_most_coffee_payer():
    sorted_name = await sort_most_coffees()
    sort_most_coffee_str = json.dumps({"most_coffees_paid": sorted_name}, indent=2)
    return PlainTextResponse(content=sort_most_coffee_str)

# Sort the member with the least coffee's paid
@router.get("/sort-least")
async def sort_least_coffee_payer():
    sorted_name = await sort_least_coffees()
    sort_least_coffee_str = json.dumps({"least_coffees_paid": sorted_name}, indent=2)
    return PlainTextResponse(content=sort_least_coffee_str)
