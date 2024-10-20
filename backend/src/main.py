import asyncio  # A library to write concurrent code using async/await syntax. (Multiple connections)
from coffee_database import *

"""
COFFEE TIME!
-----------------------------------------------------------
Aplicação que tem como objetivo:
1. Criar a base de dados
2. Criar o método de conexão à base de dados
3. Criar os outros métodos de interação com a base de dados
4. 
5. Ser uma página web através de FastAPI e JS Framework
6. Fazer a ligação à base de dados através de tunel SSH ao servidor da BD
7. Ter uma base de dados própria para armazenar informação
8. Criar consultas e escrita de informação na BD
"""


def print_menu():
    print("")
    print("1 - Show the team_members names")
    print("2 - Show the team_members and their coffee's")
    print("3 - Show the member with least coffee's")
    print("4 - Add coffee to a team member")
    print("5 - Add a team member")
    print("6 - Close the connection")
    print("")


if __name__ == '__main__':
    async def main():
        connection = await connect_to_db()
        # await create_table(connection)  # Create the table in the DB server if not exists

        while True:
            print_menu()
            option = input("Please select an option: ")

            # Use a try-except block to handle potential input errors
            try:
                option = int(option)
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if option == SHOW_TEAM_MEMBERS_NAMES:
                # Show the team_members
                await show_team_members_names(connection)
            elif option == SHOW_MEMBERS_COFFEE:
                # Show the team_members and their coffee counts
                await show_team_members(connection)  # You might want to replace this with a specific method
            elif option == SORT_COFFEE_MEMBER:
                # Show the member with the least coffee's -> Do you wish to add the coffee? Yes/No
                name = await sort_coffee(connection)
                if name:
                    choice = input(f"Do you wish to add coffee to {name}? (Y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    await add_coffee(connection, name)
                elif choice in ['n', 'no']:
                    continue
                else:
                    print("Invalid choice. Please enter Y or n.")
            elif option == ADD_COFFEE_MEMBER:
                # Add coffee to a specific team member
                name = input("Write the name of the member: ").strip()
                await add_coffee(connection, name)
            elif option == ADD_TEAM_MEMBER:
                # Add coffee to a specific team member
                name = input("Write the name of the new member: ").strip()
                await add_member(connection, name)
            elif option == EXIT:
                # Close the connection and exit
                await close_db_connection(connection)
                print("Connection closed. Exiting the application.")
                break
            else:
                print("Invalid option. Please choose a valid menu option.")

    asyncio.run(main())
