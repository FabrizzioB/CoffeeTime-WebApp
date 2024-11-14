from backend.src.app.crud.crud import *

# This is a service that handles member-related operations
class MemberService:

    @staticmethod
    async def add_new_member(name: str, coffees: int):
        if await check_member_exists(name):
            raise Exception(f"Member {name} already exists.")
        await insert_member(name, coffees)
        return f"Member {name} with {coffees} coffees added."

    @staticmethod
    async def delete_member(name: str):
        success = await delete_member(name)
        if success:
            return f"Member {name} deleted successfully."
        else:
            raise Exception(f"Failed to delete membere {name}.")
