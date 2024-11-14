from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route for SPA page
@router.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for adding a member page
@router.get("/add", response_class=HTMLResponse)
async def add_member_page(request: Request):
    return templates.TemplateResponse("add_member.html", {"request": request})

# Route for updating coffee count page
@router.get("/update", response_class=HTMLResponse)
async def update_coffee_page(request: Request):
    return templates.TemplateResponse("update_coffee.html", {"request": request})

# Route for deleting a member page
@router.get("/delete", response_class=HTMLResponse)
async def delete_member_page(request: Request):
    return templates.TemplateResponse("delete_member.html", {"request": request})

# Route to view team members
@router.get("/team", response_class=HTMLResponse)
async def team_members_page(request: Request):
    return templates.TemplateResponse("team_members.html", {"request": request})

# Route to view sort member
@router.get("/sort", response_class=HTMLResponse)
async def sort_member_page(request: Request):
    return templates.TemplateResponse("sort_member.html", {"request": request})

# Route to view sort member
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route to view sort member
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})