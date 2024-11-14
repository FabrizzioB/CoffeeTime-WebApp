from pydantic import BaseModel

# The Member class defines the structure of the data related to each team member
class Member(BaseModel):
    name: str
    coffees: int = 0  # Default value set to 0

# Pydantic model for updating
class MemberUpdate(BaseModel):
    name: str
    coffees: int