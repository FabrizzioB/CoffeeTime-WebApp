from pydantic import BaseModel

# Pydantic model to define the input data
class User():
    username: str
    password: str
