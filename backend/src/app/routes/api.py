import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from backend.src.app.auth import create_access_token, verify_token
from backend.src.app.crud.crud import *
from backend.src.app.models.member import Member
from backend.src.app.models.user import User

router = APIRouter()

# Set up OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return an access token.
    """
    username = form_data.username
    password = form_data.password

    # Verify the user's credentials
    if await verify_user(username, password):
        # Generate the JWT token
        access_token = create_access_token(data={"sub": username})
        response = RedirectResponse(url="/index", status_code=302)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# User registration
@router.post("/register")
async def register(user_data: User):
# """Register user in the database."""
    """
        Register a new user.
    """
    username = user_data.username
    password = user_data.password

    # Check if the username already exists
    if await check_username_exists(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Create the user if doesn't exist
    if await create_user_in_db(username, password):
        return {"message": "User created successfully!"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


# Method to check if user exists
async def check_username_exists(username: str) -> bool:
    pool = get_db_pool()
    query = "SELECT COUNT(*) FROM users WHERE username = %s;"

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (username,))
            result = await cursor.fetchone()
            return result[0] > 0  # Returns True if user exists


# Method to create user in the database
async def create_user_in_db(username: str, password: str) -> bool:
    pool = get_db_pool()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    insert_user_query = """
        INSERT INTO users (username, password_hash) 
        VALUES (%s, %s);
    """

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            try:
                await cursor.execute(insert_user_query, (username, hashed_password))
                await connection.commit()
                return True
            except Exception as e:
                print(f"Error creating user: {e}")
                return False



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
