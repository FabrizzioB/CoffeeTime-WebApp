from backend.src.app.crud.crud import *

# Service that handles coffee-related logic
class CoffeeService:

    @staticmethod
    async def update_coffee(name: str, number: int):
        if number < 0:
            raise Exception("Coffee count cannot be negative.")
        await update_coffee(name, number)
        return f"Added {number} coffees to {name}."
