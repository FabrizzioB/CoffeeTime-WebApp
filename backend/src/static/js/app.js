document.addEventListener('DOMContentLoaded', function () {
    const membersTable = document.querySelector('#members-table tbody');
    const updateForm = document.getElementById('update-member-form');
    const updateNameInput = document.getElementById('update-name');
    const updateCoffeesInput = document.getElementById('update-coffees');
    const updateFormElement = document.getElementById('update-form');
    let currentMemberId = null;

    // Load and display all members on page load
    function loadMembers() {
        fetch('/team-members')
            .then(response => response.json())
            .then(data => {
                membersTable.innerHTML = '';
                data.team_members.forEach(member => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${member.name}</td>
                        <td>${member.coffees}</td>
                        <td>
                            <button class="btn" onclick="showUpdateForm('${member.name}', ${member.coffees})">Update</button>
                            <button class="btn" onclick="increaseCoffees('${member.name}')">+1 Coffee</button>
                            <button class="btn" onclick="decreaseCoffees('${member.name}')">-1 Coffee</button>
                            <button class="btn delete-btn" onclick="deleteMember('${member.name}')">🗑️</button>
                        </td>
                    `;
                    membersTable.appendChild(row);
                });
            })
            .catch(error => console.error('Error loading members:', error));
    }

    // Show the update form for a specific member
    window.showUpdateForm = function (name, coffees) {
        currentMemberId = name;
        updateNameInput.value = name;
        updateCoffeesInput.value = coffees;
        updateForm.style.display = 'block';
    };

    // Hide the update form
    window.hideUpdateForm = function () {
        updateForm.style.display = 'none';
        currentMemberId = null;
    };

    // Handle member update
    updateFormElement.addEventListener('submit', function (e) {
        e.preventDefault();
        const updatedName = updateNameInput.value;
        const updatedCoffees = parseInt(updateCoffeesInput.value, 10);

        fetch(`/update-coffee/${currentMemberId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: updatedName, coffees: updatedCoffees })
        })
            .then(response => {
                if (response.ok) {
                    hideUpdateForm();
                    loadMembers(); // Reload the members list after update
                } else {
                    console.error('Error updating member');
                }
            });
    });

    // Increase coffees for a member
    window.increaseCoffees = function (name) {
        fetch(`/add-coffee/${name}/1`, {
            method: 'PUT'
        })
            .then(response => {
                if (response.ok) {
                    loadMembers(); // Reload members after increasing coffees
                }
            })
            .catch(error => console.error('Error increasing coffees:', error));
    };

    // Decrease coffees for a member
    window.decreaseCoffees = function (name) {
        fetch(`/add-coffee/${name}/-1`, {
            method: 'PUT'
        })
            .then(response => {
                if (response.ok) {
                    loadMembers(); // Reload members after decreasing coffees
                }
            })
            .catch(error => console.error('Error decreasing coffees:', error));
    };

    // Delete a member
    window.deleteMember = function (name) {
        fetch(`/delete/${name}`, {
            method: 'DELETE'
        })
            .then(response => {
                if (response.ok) {
                    loadMembers(); // Reload members after deletion
                }
            })
            .catch(error => console.error('Error deleting member:', error));
    };

    // Load the members when the page is ready
    loadMembers();
});
