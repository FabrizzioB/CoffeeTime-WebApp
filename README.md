# CoffeeTime Web Application


This project is a FastAPI-based web application for managing a team’s coffee purchases.

It includes a web interface and a set of API endpoints that interact with a MySQL database over an SSH tunnel. 

The project manages a list of team members and tracks the number of times each member has paid for coffee.

### Web Interface

1. Login Page (/): Displays the login page for initial user access.
2. Add Member Page (/add): Provides a form for adding a new team member. 
3. Update Coffee Count Page (/update): Allows users to update the coffee count for an existing member. 
4. Delete Member Page (/delete): Lets users remove a team member from the database. 
5. View Team Members (/team): Displays all team members and their coffee counts. 
6. Sort Members (/sort): Shows options to sort members based on coffee purchases.
7. Single Page Application (SPA) Page (/index): Serves the main interface for the team management functionality.
8. Register (/register): Page to register the user for the app.
9. Password recovery (/recovery): Page to recover the account / password reset.

### API Endpoints

#### Member Management

- PUT /add: Adds a new team member to the database with an initial coffee count.
- DELETE /delete/{name}: Removes a specified member from the database by name.
- Coffee Count Management
- PUT /add-coffee: Increments the coffee count for a specified member by one.
- PUT /add-coffee/{name}/{number}: Increments a specified member’s coffee count by a given number, validating that the number is non-negative.
- PUT /remove-coffee: Resets the coffee count for a specified member to zero.

#### Data Retrieval

- GET /team-members-names: Returns a list of team member names in alphabetical order.
- GET /team-members: Retrieves all team members along with their coffee counts as JSON.
- GET /sort-least: Returns the team member who has paid for the least coffees.
- GET /sort-most: Returns the team member who has paid for the most coffees. 

### Database Management
- Connection Setup: The coffee.py file configures a secure SSH tunnel to access a MySQL database. This allows the app to establish a connection to the database server remotely.
- Database Operations: The database contains a team_members table that stores each team member’s name and the number of times they have paid for coffee.
- Create Table: Ensures that the team_members table is present in the database.
- Insert, Update, and Delete Records: Functions to add, increment, reset, or remove entries related to team members and coffee counts.
- Data Retrieval: Queries to fetch team members by name, sorted lists of members by coffee counts, and individual member checks. 

### Sorting and Filtering

- Sorting functions (sort_least_coffees and sort_most_coffees) identify team members who have paid for the fewest and most coffees, respectively. The results are alphabetically ordered when counts are the same. 

### Startup and Shutdown

- The app opens a connection to the database on startup and closes it gracefully on shutdown, ensuring resource management and connection stability.

### To do list

- Login, register and recovery to finish.
- Only logged in users can use the app.
- Users logged in can use all the functionalities of the app.