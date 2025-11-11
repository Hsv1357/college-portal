// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Modal functionality
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close-modal');
    const addUserBtn = document.getElementById('add-user-btn');
    const applyPermissionBtn = document.getElementById('apply-permission-btn');
    const uploadStudentsBtn = document.getElementById('upload-students-btn');
    const uploadFacultyBtn = document.getElementById('upload-faculty-btn');
    const addFacultyBtn = document.getElementById('add-faculty-btn');
    const addClubEventBtn = document.getElementById('add-club-event-btn');
    const changePasswordBtn = document.getElementById('change-password-btn');
    
    // Open modals
    if (addUserBtn) {
        addUserBtn.addEventListener('click', function() {
            document.getElementById('add-user-modal').style.display = 'flex';
        });
    }
    
    if (applyPermissionBtn) {
        applyPermissionBtn.addEventListener('click', function() {
            document.getElementById('apply-permission-modal').style.display = 'flex';
            // Set today's date as default
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('date').value = today;
        });
    }

    if (uploadStudentsBtn) {
        uploadStudentsBtn.addEventListener('click', function() {
            document.getElementById('upload-students-modal').style.display = 'flex';
        });
    }

    if (uploadFacultyBtn) {
        uploadFacultyBtn.addEventListener('click', function() {
            document.getElementById('upload-faculty-modal').style.display = 'flex';
        });
    }

    if (addFacultyBtn) {
        addFacultyBtn.addEventListener('click', function() {
            document.getElementById('add-faculty-modal').style.display = 'flex';
        });
    }

    if (addClubEventBtn) {
        addClubEventBtn.addEventListener('click', function() {
            document.getElementById('add-club-event-modal').style.display = 'flex';
        });
    }

    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', function() {
            document.getElementById('change-password-modal').style.display = 'flex';
        });
    }
    
    // Close modals
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
    
    // Handle permission status updates
    const approveButtons = document.querySelectorAll('.btn-approve');
    const rejectButtons = document.querySelectorAll('.btn-reject');
    
    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const permissionId = this.getAttribute('data-id');
            updatePermissionStatus(permissionId, 'approved');
        });
    });
    
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const permissionId = this.getAttribute('data-id');
            updatePermissionStatus(permissionId, 'rejected');
        });
    });
    
    // Add user form submission
    const addUserForm = document.getElementById('add-user-form');
    if (addUserForm) {
        addUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addUser();
        });
    }
    
    // Apply permission form submission
    const applyPermissionForm = document.getElementById('apply-permission-form');
    if (applyPermissionForm) {
        applyPermissionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyPermission();
        });
    }

    // Upload students form submission
    const uploadStudentsForm = document.getElementById('upload-students-form');
    if (uploadStudentsForm) {
        uploadStudentsForm.addEventListener('submit', uploadStudents);
    }

    // Upload faculty form submission
    const uploadFacultyForm = document.getElementById('upload-faculty-form');
    if (uploadFacultyForm) {
        uploadFacultyForm.addEventListener('submit', uploadFaculty);
    }

    // Add faculty form submission
    const addFacultyForm = document.getElementById('add-faculty-form');
    if (addFacultyForm) {
        addFacultyForm.addEventListener('submit', addFaculty);
    }

    // Add club/event form submission
    const addClubEventForm = document.getElementById('add-club-event-form');
    if (addClubEventForm) {
        addClubEventForm.addEventListener('submit', addClubEvent);
    }

    // Change password form submission
    const changePasswordForm = document.getElementById('change-password-form');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', changePassword);
    }
    
    // Initialize charts if any
    initializeCharts();
    
    // Add real-time updates simulation
    simulateRealTimeUpdates();
}

// Update permission status
function updatePermissionStatus(permissionId, status) {
    showLoading(true);
    
    fetch('/api/update_permission_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            permission_id: permissionId,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            showNotification(`Permission ${status} successfully!`, 'success');
            // Reload after 1 second to show updated status
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        showNotification('An error occurred while updating permission status.', 'error');
    });
}

// Add new user
function addUser() {
    showLoading(true);
    
    const form = document.getElementById('add-user-form');
    const formData = new FormData(form);
    const data = {
        username: formData.get('username'),
        password: formData.get('password'),
        name: formData.get('name'),
        email: formData.get('email'),
        class: formData.get('class')
    };
    
    fetch('/api/add_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            document.getElementById('add-user-modal').style.display = 'none';
            form.reset();
            showNotification('Student added successfully!', 'success');
            // Reload after 1 second to show new user
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        showNotification('An error occurred while adding student.', 'error');
    });
}

// Apply for permission
function applyPermission() {
    showLoading(true);
    
    const form = document.getElementById('apply-permission-form');
    const formData = new FormData(form);
    const data = {
        date: formData.get('date'),
        reason: formData.get('reason'),
        proof: formData.get('proof')
    };
    
    fetch('/api/add_permission', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            document.getElementById('apply-permission-modal').style.display = 'none';
            form.reset();
            showNotification('Permission request submitted successfully!', 'success');
            // Reload after 1 second to show new permission
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        showNotification('An error occurred while submitting permission request.', 'error');
    });
}

// Upload students from Excel
function uploadStudents(e) {
    e.preventDefault();
    showLoading(true);
    
    const formData = new FormData(document.getElementById('upload-students-form'));
    
    fetch('/api/upload_students', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            document.getElementById('upload-students-modal').style.display = 'none';
            document.getElementById('upload-students-form').reset();
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 2000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showNotification('An error occurred while uploading students.', 'error');
    });
}

// Upload faculty from Excel
function uploadFaculty(e) {
    e.preventDefault();
    showLoading(true);
    
    const formData = new FormData(document.getElementById('upload-faculty-form'));
    
    fetch('/api/upload_faculty', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            document.getElementById('upload-faculty-modal').style.display = 'none';
            document.getElementById('upload-faculty-form').reset();
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 2000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showNotification('An error occurred while uploading faculty.', 'error');
    });
}

// Add faculty
function addFaculty(e) {
    e.preventDefault();
    showLoading(true);
    
    const form = document.getElementById('add-faculty-form');
    const formData = new FormData(form);
    const data = {
        username: formData.get('username'),
        password: formData.get('password'),
        name: formData.get('name'),
        email: formData.get('email'),
        department: formData.get('department')
    };
    
    fetch('/api/add_faculty', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            document.getElementById('add-faculty-modal').style.display = 'none';
            form.reset();
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 2000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showNotification('An error occurred while adding faculty.', 'error');
    });
}

// Add club/event
function addClubEvent(e) {
    e.preventDefault();
    showLoading(true);
    
    const form = document.getElementById('add-club-event-form');
    const formData = new FormData(form);
    const data = {
        name: formData.get('name'),
        type: formData.get('type')
    };
    
    fetch('/api/add_club_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            document.getElementById('add-club-event-modal').style.display = 'none';
            form.reset();
            showNotification(data.message, 'success');
            loadClubsEvents();
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showNotification('An error occurred while adding club/event.', 'error');
    });
}

// Change password
function changePassword(e) {
    e.preventDefault();
    showLoading(true);
    
    const form = document.getElementById('change-password-form');
    const formData = new FormData(form);
    const data = {
        current_password: formData.get('current_password'),
        new_password: formData.get('new_password'),
        confirm_password: formData.get('confirm_password')
    };
    
    if (data.new_password !== data.confirm_password) {
        showLoading(false);
        showNotification('New passwords do not match', 'error');
        return;
    }
    
    fetch('/api/change_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            document.getElementById('change-password-modal').style.display = 'none';
            form.reset();
            showNotification(data.message, 'success');
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showNotification('An error occurred while changing password.', 'error');
    });
}

// Load clubs and events
function loadClubsEvents() {
    fetch('/api/get_clubs_events')
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('clubs-events-table');
        if (table) {
            table.innerHTML = '';
            data.clubs.forEach(club => {
                table.innerHTML += `
                    <tr>
                        <td>${club.name}</td>
                        <td>Club</td>
                        <td>Active</td>
                        <td>
                            <button class="action-btn btn-edit">Edit</button>
                            <button class="action-btn btn-delete">Delete</button>
                        </td>
                    </tr>
                `;
            });
            data.events.forEach(event => {
                table.innerHTML += `
                    <tr>
                        <td>${event.name}</td>
                        <td>Event</td>
                        <td>Active</td>
                        <td>
                            <button class="action-btn btn-edit">Edit</button>
                            <button class="action-btn btn-delete">Delete</button>
                        </td>
                    </tr>
                `;
            });
        }
    });
}

// Show loading state
function showLoading(show) {
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        if (show) {
            button.disabled = true;
            button.innerHTML = 'Processing...';
            button.classList.add('loading');
        } else {
            button.disabled = false;
            button.innerHTML = button.getAttribute('data-original-text') || 'Submit';
            button.classList.remove('loading');
        }
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message ${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '80px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';
    notification.style.maxWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// Initialize charts (placeholder for future chart implementations)
function initializeCharts() {
    // This would integrate with Chart.js or similar library
    console.log('Charts initialized');
}

// Simulate real-time updates
function simulateRealTimeUpdates() {
    // Update time every minute
    setInterval(updateDashboardTime, 60000);
    updateDashboardTime();
}

function updateDashboardTime() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
    
    timeElements.forEach(element => {
        element.textContent = timeString;
    });
}

// Export functionality (placeholder)
function exportToExcel(tableId, filename) {
    // This would integrate with a library like SheetJS
    console.log(`Exporting table ${tableId} to ${filename}.xlsx`);
    showNotification('Export functionality would be implemented here', 'info');
}

// Print functionality
function printSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print ${sectionId}</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                    </style>
                </head>
                <body>
                    ${section.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}