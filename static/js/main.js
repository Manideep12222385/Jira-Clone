// Manager dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop
    initializeDragDrop();
    
    // Initialize modals
    initializeModals();
    
    // Filter functionality
    initializeFilters();
    
    // Initialize project popup
    initializeProjectPopup();

    // Initialize team management
    initializeTeamManagement();
});

function initializeTeamManagement() {
    // Add event listener for new team leader select
    const newTeamLeader = document.getElementById('newTeamLeader');
    if (newTeamLeader) {
        newTeamLeader.addEventListener('change', updateNewSelectedMembers);
    }

    // Add event listener for team leader select
    const teamLeader = document.getElementById('teamLeader');
    if (teamLeader) {
        teamLeader.addEventListener('change', updateSelectedMembers);
    }
}

function showNewTeamModal() {
    const modal = document.getElementById('newTeamModal');
    if (modal) {
        modal.style.display = 'block';
        // Reset form and scroll to top
        const form = modal.querySelector('#newTeamForm');
        if (form) {
            form.reset();
            modal.querySelector('.modal-content').scrollTop = 0;
        }
        updateNewSelectedMembers();
    }
}

function updateNewSelectedMembers() {
    const selectedMembersDiv = document.getElementById('newSelectedMembers');
    const checkboxes = document.querySelectorAll('#newTeamMembers input[type="checkbox"]:checked');
    const teamLeader = document.getElementById('newTeamLeader');
    const teamLeaderName = teamLeader.options[teamLeader.selectedIndex]?.text || 'No leader selected';
    
    let html = `
        <div class="selected-member">
            <i class="fas fa-user-tie"></i>
            <span>${teamLeaderName} ${teamLeader.value ? '(Team Leader)' : ''}</span>
        </div>
    `;
    
    checkboxes.forEach(checkbox => {
        const label = document.querySelector(`label[for="${checkbox.id}"]`).textContent;
        html += `
            <div class="selected-member">
                <i class="fas fa-user"></i>
                <span>${label}</span>
            </div>
        `;
    });
    
    if (!teamLeader.value && checkboxes.length === 0) {
        html = `
            <div style="color: #666; font-style: italic; padding: 10px;">
                No team members selected
            </div>
        `;
    }
    
    selectedMembersDiv.innerHTML = html;
}

async function createTeam(event) {
    event.preventDefault();
    const formData = {
        name: document.getElementById('newTeamName').value,
        description: document.getElementById('newTeamDescription').value,
        leader_id: document.getElementById('newTeamLeader').value,
        members: Array.from(document.querySelectorAll('#newTeamMembers input:checked')).map(cb => cb.value)
    };
    
    try {
        const response = await fetch('/admin/create_team', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Error creating team');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating team');
    }
}

function showTeamDetails(teamId) {
    const modal = document.getElementById('teamDetailsModal');
    if (!modal) return;

    // Show loading state
    modal.style.display = 'block';
    const form = modal.querySelector('#editTeamForm');
    if (form) {
        form.reset();
        modal.querySelector('.modal-content').scrollTop = 0;
    }

    // Fetch and populate data
    fetch(`/admin/get_team_details/${teamId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            // Set form values
            document.getElementById('teamId').value = teamId;
            document.getElementById('teamName').value = data.name;
            document.getElementById('teamDescription').value = data.description || '';
            
            const teamLeaderSelect = document.getElementById('teamLeader');
            if (teamLeaderSelect) {
                teamLeaderSelect.value = data.leader_id;
            }
            
            // Update team members checkboxes
            const checkboxes = document.querySelectorAll('#teamMembers input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = data.members.includes(parseInt(checkbox.value));
            });
            
            // Update the selected members display
            updateSelectedMembers();
        })
        .catch(error => {
            console.error('Error fetching team details:', error);
            alert('Error loading team details. Please try again.');
            modal.style.display = 'none';
        });
}

function updateTeam(event) {
    event.preventDefault();
    
    const formData = {
        team_id: document.getElementById('teamId').value,
        name: document.getElementById('teamName').value,
        description: document.getElementById('teamDescription').value,
        leader_id: document.getElementById('teamLeader').value,
        members: Array.from(document.querySelectorAll('#teamMembers input:checked')).map(cb => cb.value)
    };
    
    fetch('/admin/update_team', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        location.reload();
    })
    .catch(error => {
        console.error('Error updating team:', error);
        alert('Error updating team. Please try again.');
    });
}

function initializeDragDrop() {
    const taskCards = document.querySelectorAll('.task-card');
    const dropZones = document.querySelectorAll('.task-list');
    
    taskCards.forEach(card => {
        card.draggable = true;
        card.addEventListener('dragstart', handleDragStart);
    });
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', allowDrop);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
    });
}

function handleDragStart(e) {
    e.dataTransfer.setData('taskId', e.target.dataset.taskId);
}

function handleDragOver(e) {
    e.preventDefault();
}

function handleDrop(e) {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    const newStatus = e.target.closest('.kanban-column').dataset.status;
    
    updateTaskStatus(taskId, newStatus);
}

function updateTaskStatus(taskId, newStatus) {
    fetch('/admin/update_task_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.error || 'Error updating task status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating task status. Please try again.');
    });
}

function initializeFilters() {
    const epicFilter = document.getElementById('epic-filter');
    const typeFilter = document.getElementById('type-filter');
    
    if (epicFilter && typeFilter) {
        epicFilter.addEventListener('change', applyFilters);
        typeFilter.addEventListener('change', applyFilters);
    }
}

function applyFilters() {
    const epic = document.getElementById('epic-filter')?.value || '';
    const type = document.getElementById('type-filter')?.value || '';

    // Filter tasks based on epic (project name) and type (Story/Task)
    const tasks = document.querySelectorAll('.task-card');
    tasks.forEach(task => {
        const taskProject = task.querySelector('small')?.textContent.replace('Project: ', '').trim() || '';
        const taskType = task.getAttribute('data-type') || '';
        // Get the column status (TO DO, IN PROGRESS, DONE)
        const taskStatus = task.closest('.kanban-column')?.getAttribute('data-status') || '';

        // EPIC filter: project name
        const showEpic = !epic || taskProject === epic;

        // Type filter logic
        let showType = true;
        if (type === 'Story') {
            showType = (taskType === 'Story') && (taskStatus === 'TO DO' || taskStatus === 'IN PROGRESS');
        } else if (type === 'Task') {
            showType = (taskType === 'Task') && (taskStatus === 'DONE');
        }

        task.style.display = (showEpic && showType) ? 'block' : 'none';
    });
}

// Modal handling
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close');
    
    // Close modal when clicking close button
    closeButtons.forEach(button => {
        button.onclick = function() {
            button.closest('.modal').style.display = 'none';
        }
    });
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    }

    // Add event listeners for form submissions
    const newTeamForm = document.getElementById('newTeamForm');
    if (newTeamForm) {
        newTeamForm.addEventListener('submit', createTeam);
    }

    const editTeamForm = document.getElementById('editTeamForm');
    if (editTeamForm) {
        editTeamForm.addEventListener('submit', updateTeam);
    }

    // Add event listeners for member selection
    const teamLeader = document.getElementById('teamLeader');
    if (teamLeader) {
        teamLeader.addEventListener('change', updateSelectedMembers);
    }

    const newTeamLeader = document.getElementById('newTeamLeader');
    if (newTeamLeader) {
        newTeamLeader.addEventListener('change', updateNewSelectedMembers);
    }
}

// Project management
function showNewProjectModal() {
    const modal = document.getElementById('newProjectModal');
    if (modal) {
    modal.style.display = 'block';
    
    // Set default dates
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').value = today;
    document.getElementById('endDate').min = today;

    // Always update team members when modal opens
    updateTeamMembers();
    }
}

async function showProjectDetails(projectId) {
    const modal = document.getElementById('projectDetailsModal');
    if (!modal) return;

    try {
        // Show loading state
        modal.style.display = 'block';
        const form = modal.querySelector('#editProjectForm');
        if (form) {
            form.reset();
            modal.querySelector('.modal-content').scrollTop = 0;
        }

        // Fetch project details
        const response = await fetch(`/admin/get_project_details/${projectId}`);
        const project = await response.json();
        
        if (project.error) {
            throw new Error(project.error);
        }

        // Set form values
        document.getElementById('projectId').value = projectId;
        document.getElementById('editProjectName').value = project.name;
        document.getElementById('editProjectDescription').value = project.description || '';
        document.getElementById('editClientSelect').value = project.client_id;
        document.getElementById('editTeamSelect').value = project.team_id;
        document.getElementById('editEndDate').value = project.end_date;
        
        // Update team members
        await updateEditTeamMembers();
        
        // Check team members that are assigned to the project
        if (project.team_members) {
            project.team_members.forEach(memberId => {
                const checkbox = document.querySelector(`#editTeamMembersSelect input[value="${memberId}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
    } catch (error) {
        console.error('Error fetching project details:', error);
        alert('Error loading project details. Please try again.');
        modal.style.display = 'none';
    }
}

async function updateProject(event) {
    event.preventDefault();
    
    const formData = {
        project_id: document.getElementById('projectId').value,
        name: document.getElementById('editProjectName').value,
        description: document.getElementById('editProjectDescription').value,
        client_id: document.getElementById('editClientSelect').value,
        team_id: document.getElementById('editTeamSelect').value,
        end_date: document.getElementById('editEndDate').value,
        team_members: Array.from(document.querySelectorAll('#editTeamMembersSelect input:checked')).map(cb => cb.value)
    };
    
    try {
        const response = await fetch('/admin/update_project', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Error updating project');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating project. Please try again.');
    }
}

async function deleteProject() {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
        return;
    }
    
    const projectId = document.getElementById('projectId').value;
    
    try {
        const response = await fetch(`/admin/delete_project/${projectId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Error deleting project');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting project. Please try again.');
    }
}

// Team management
function updateTeamMembersList() {
    const teamLeaderSelect = document.getElementById('teamLeader');
    const selectedLeaderId = teamLeaderSelect.value;
    const teamMembersDiv = document.getElementById('teamMembers');
    
    // Show/hide team member options based on selected leader
    const memberItems = teamMembersDiv.querySelectorAll('.checkbox-item');
    memberItems.forEach(item => {
        const userId = item.dataset.userid;
        const checkbox = item.querySelector('input[type="checkbox"]');
        
        if (userId === selectedLeaderId) {
            item.style.display = 'none';
            checkbox.checked = false;
        } else {
            item.style.display = 'block';
        }
    });
    
    // Update the selected members display
    updateSelectedMembers();
}

async function showTeamDetails(teamId) {
    try {
        const response = await fetch(`/admin/get_team_details/${teamId}`);
        const team = await response.json();
        
        // Set form values
        document.getElementById('teamId').value = teamId;
        document.getElementById('teamName').value = team.name;
        document.getElementById('teamDescription').value = team.description || '';
        
        const teamLeaderSelect = document.getElementById('teamLeader');
        teamLeaderSelect.value = team.leader_id;
        
        // Update team members checkboxes
        const teamMembersDiv = document.getElementById('teamMembers');
        const checkboxes = teamMembersDiv.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => checkbox.checked = false); // Reset all checkboxes
        
        if (team.members && team.members.length > 0) {
            team.members.forEach(memberId => {
                const checkbox = teamMembersDiv.querySelector(`input[value="${memberId}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
        
        // Update team members list visibility
        updateTeamMembersList();
        
        // Show the modal
        document.getElementById('teamDetailsModal').style.display = 'block';
    } catch (error) {
        console.error('Error fetching team details:', error);
        alert('Error loading team details. Please try again.');
    }
}

async function updateTeam(event) {
    event.preventDefault();
    const formData = {
        team_id: document.getElementById('teamId').value,
        name: document.getElementById('teamName').value,
        description: document.getElementById('teamDescription').value,
        leader_id: document.getElementById('teamLeader').value,
        members: Array.from(document.querySelectorAll('#teamMembers input:checked')).map(cb => cb.value)
    };
    
    try {
        const response = await fetch('/admin/update_team', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Error updating team');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating team. Please try again.');
    }
}

async function deleteTeam() {
    if (!confirm('Are you sure you want to delete this team? This action cannot be undone.')) {
        return;
    }
    
    const teamId = document.getElementById('teamId').value;
    
    try {
        const response = await fetch(`/admin/delete_team/${teamId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Error deleting team');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting team. Please try again.');
    }
}

function updateSelectedMembers() {
    const selectedMembersDiv = document.getElementById('selectedMembers');
    const checkboxes = document.querySelectorAll('#teamMembers input[type="checkbox"]:checked');
    const teamLeader = document.getElementById('teamLeader');
    const teamLeaderName = teamLeader.options[teamLeader.selectedIndex].text;
    
    let html = `
        <div class="selected-member">
            <i class="fas fa-user-tie"></i>
            <span>${teamLeaderName} (Team Leader)</span>
        </div>
    `;
    
    checkboxes.forEach(checkbox => {
        const label = document.querySelector(`label[for="${checkbox.id}"]`).textContent;
        html += `
            <div class="selected-member">
                <i class="fas fa-user"></i>
                <span>${label}</span>
            </div>
        `;
    });
    
    if (checkboxes.length === 0) {
        html += `
            <div style="color: #666; font-style: italic; padding: 10px;">
                No team members selected
            </div>
        `;
    }
    
    selectedMembersDiv.innerHTML = html;
}

// Drag and drop functionality
function allowDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    const taskId = event.dataTransfer.getData('taskId');
    const newStatus = event.target.closest('.kanban-column').dataset.status;
    
    updateTaskStatus(taskId, newStatus);
}

function updateTaskStatus(taskId, newStatus) {
    fetch('/update_task_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

// Helper function to update team members select when team is changed
function updateTeamMembers() {
    const teamId = document.getElementById('teamSelect').value;
    const container = document.getElementById('teamMembersSelect');
    container.innerHTML = '<div style="text-align:center; color:#888;">Loading team members...</div>';
    
    fetch(`/get_team_members/${teamId}`)
        .then(response => response.json())
        .then(members => {
            container.innerHTML = members.map(member => `
                <div class="checkbox-item">
                    <input type="checkbox" id="member${member.id}" value="${member.id}">
                    <label for="member${member.id}">${member.username}</label>
                </div>
            `).join('');
        });
}

function updateEditTeamMembers() {
    const teamId = document.getElementById('editTeamSelect').value;
    fetch(`/get_team_members/${teamId}`)
        .then(response => response.json())
        .then(members => {
            const container = document.getElementById('editTeamMembersSelect');
            container.innerHTML = members.map(member => `
                <div class="checkbox-item">
                    <input type="checkbox" id="editMember${member.id}" value="${member.id}">
                    <label for="editMember${member.id}">${member.username} - ${member.skills}</label>
                </div>
            `).join('');
        });
}

function initializeProjectPopup() {
    const projectRows = document.querySelectorAll('.project-row');
    const popup = document.getElementById('projectPopup');
    const closeBtn = document.querySelector('.close-popup');

    // Close popup when clicking the close button
    if (closeBtn) {
        closeBtn.onclick = function() {
            popup.style.display = "none";
        }
    }

    // Close popup when clicking outside
    window.onclick = function(event) {
        if (event.target == popup) {
            popup.style.display = "none";
        }
    }

    // Add click event to project rows
    projectRows.forEach(row => {
        row.addEventListener('click', async function() {
            const projectId = this.dataset.projectId;
            const projectName = this.dataset.projectName;
            const projectDesc = this.dataset.projectDesc;
            const client = this.dataset.client;
            const team = this.dataset.team;
            const progress = this.dataset.progress;
            const endDate = this.dataset.endDate;

            // Update popup content
            document.getElementById('popupProjectName').textContent = projectName;
            document.getElementById('popupDescription').textContent = projectDesc;
            document.getElementById('popupClient').textContent = client;
            document.getElementById('popupTeam').textContent = team;
            document.getElementById('popupEndDate').textContent = endDate;
            document.getElementById('popupProgress').textContent = `${progress}%`;
            document.getElementById('popupProgressFill').style.width = `${progress}%`;

            // Fetch tasks for this project
            try {
                const response = await fetch(`/get_project_details/${projectId}/tasks`);
                const tasks = await response.json();
                displayTasks(tasks);
            } catch (error) {
                console.error('Error fetching tasks:', error);
            }

            // Fetch team members for this project
            try {
                const response = await fetch(`/get_team_members_by_project/${projectId}`);
                const members = await response.json();
                displayTeamMembers(members);
            } catch (error) {
                console.error('Error fetching team members:', error);
            }

            // Show popup
            popup.style.display = "block";
        });
    });
}

function displayTasks(tasks) {
    const tasksContainer = document.getElementById('popupTasks');
    tasksContainer.innerHTML = '';

    tasks.forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.className = 'task-item';
        
        const statusClass = {
            'TO DO': 'status-todo',
            'IN PROGRESS': 'status-progress',
            'DONE': 'status-done'
        }[task.status] || '';

        taskElement.innerHTML = `
            ${task.title}
            <span class="task-status ${statusClass}">${task.status}</span>
        `;
        tasksContainer.appendChild(taskElement);
    });
}

function displayTeamMembers(members) {
    const membersContainer = document.getElementById('popupTeamMembers');
    membersContainer.innerHTML = '';

    members.forEach(member => {
        const memberElement = document.createElement('div');
        memberElement.className = 'team-member-item';
        memberElement.innerHTML = `
            <strong>${member.username}</strong>
            <span>${member.role}</span>
        `;
        membersContainer.appendChild(memberElement);
    });
}
window.showProjectDetails = showProjectDetails;