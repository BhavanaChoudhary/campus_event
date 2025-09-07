// Campus Event Management Platform JavaScript

const API_BASE = 'http://localhost:5000/api';

// Utility Functions
function showMessage(message, type = 'success') {
    const msgDiv = document.createElement('div');
    msgDiv.textContent = message;
    msgDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 5px;
        color: white;
        background-color: ${type === 'success' ? '#28a745' : '#dc3545'};
        z-index: 1000;
        transition: opacity 0.3s;
    `;
    document.body.appendChild(msgDiv);
    setTimeout(() => {
        msgDiv.style.opacity = '0';
        setTimeout(() => document.body.removeChild(msgDiv), 300);
    }, 3000);
}

// Event Management Functions
async function createEvent(event) {
    event.preventDefault();

    const eventData = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        event_type: document.getElementById('eventType').value,
        event_date: document.getElementById('eventDate').value,
        college_id: parseInt(document.getElementById('collegeId').value),
        capacity: parseInt(document.getElementById('capacity').value) || 100
    };

    try {
        const response = await fetch(`${API_BASE}/events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventData)
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('Event created successfully!');
            document.getElementById('eventForm').reset();
            loadEvents();
        } else {
            showMessage(result.error || 'Failed to create event', 'error');
        }
    } catch (error) {
        showMessage('Network error occurred', 'error');
        console.error('Error:', error);
    }
}

async function loadEvents() {
    const collegeId = document.getElementById('collegeIdFilter')?.value;
    const eventType = document.getElementById('eventTypeFilter')?.value;

    let url = `${API_BASE}/events`;
    const params = new URLSearchParams();
    if (collegeId) params.append('college_id', collegeId);
    if (eventType) params.append('event_type', eventType);
    if (params.toString()) url += '?' + params.toString();

    try {
        const response = await fetch(url);
        const events = await response.json();

        const container = document.getElementById('eventsList') || document.getElementById('eventsContainer');
        if (container) {
            container.innerHTML = events.map(event => `
                <div class="event-card">
                    <h3>${event.title}</h3>
                    <p><strong>Type:</strong> ${event.event_type}</p>
                    <p><strong>Date:</strong> ${event.event_date}</p>
                    <p><strong>College:</strong> ${event.college_name}</p>
                    <p><strong>Registrations:</strong> ${event.registrations_count}/${event.capacity}</p>
                    <div class="event-actions">
                        ${document.getElementById('studentIdInput') ?
                            `<button onclick="registerForEvent(${event.id})">Register</button>` :
                            `<button onclick="viewEventDetails(${event.id})">View Details</button>`
                        }
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

async function registerForEvent(eventId) {
    const studentId = document.getElementById('studentIdInput')?.value;
    if (!studentId) {
        showMessage('Please enter your Student ID', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/events/${eventId}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: parseInt(studentId) })
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('Successfully registered for event!');
            loadEvents();
        } else {
            showMessage(result.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Network error occurred', 'error');
        console.error('Error:', error);
    }
}

async function loadRegistrations() {
    const studentId = document.getElementById('studentIdInput')?.value;
    if (!studentId) {
        showMessage('Please enter your Student ID', 'error');
        return;
    }

    // This would require additional API endpoints for student-specific data
    // For now, we'll show a placeholder
    document.getElementById('registrationsList').innerHTML = `
        <p>Loading registrations for Student ID: ${studentId}</p>
        <p>Note: Full registration history would require additional API endpoints</p>
    `;
}

// Report Functions
async function viewEventReport() {
    try {
        const response = await fetch(`${API_BASE}/reports/events`);
        const events = await response.json();

        const container = document.getElementById('reportContainer');
        container.innerHTML = `
            <h3>Event Popularity Report</h3>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Event</th>
                        <th>Type</th>
                        <th>Date</th>
                        <th>College</th>
                        <th>Registrations</th>
                        <th>Attendance</th>
                        <th>Avg Rating</th>
                    </tr>
                </thead>
                <tbody>
                    ${events.map(event => `
                        <tr>
                            <td>${event.title}</td>
                            <td>${event.event_type}</td>
                            <td>${event.event_date}</td>
                            <td>${event.college_name}</td>
                            <td>${event.total_registrations}</td>
                            <td>${event.total_attendance}</td>
                            <td>${event.avg_rating || 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading event report:', error);
    }
}

async function viewStudentReport() {
    try {
        const response = await fetch(`${API_BASE}/reports/students`);
        const students = await response.json();

        const container = document.getElementById('reportContainer');
        container.innerHTML = `
            <h3>Student Participation Report</h3>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Email</th>
                        <th>College</th>
                        <th>Registrations</th>
                        <th>Attendance</th>
                        <th>Avg Rating</th>
                    </tr>
                </thead>
                <tbody>
                    ${students.map(student => `
                        <tr>
                            <td>${student.name}</td>
                            <td>${student.email}</td>
                            <td>${student.college_name}</td>
                            <td>${student.total_registrations}</td>
                            <td>${student.total_attendance}</td>
                            <td>${student.avg_rating || 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading student report:', error);
    }
}

async function viewTopStudents() {
    try {
        const response = await fetch(`${API_BASE}/reports/top-students`);
        const students = await response.json();

        const container = document.getElementById('reportContainer');
        container.innerHTML = `
            <h3>Top 3 Most Active Students</h3>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Student</th>
                        <th>Email</th>
                        <th>College</th>
                        <th>Registrations</th>
                        <th>Attendance</th>
                        <th>Avg Rating</th>
                    </tr>
                </thead>
                <tbody>
                    ${students.map((student, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${student.name}</td>
                            <td>${student.email}</td>
                            <td>${student.college_name}</td>
                            <td>${student.total_registrations}</td>
                            <td>${student.total_attendance}</td>
                            <td>${student.avg_rating || 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading top students report:', error);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add form event listeners
    const eventForm = document.getElementById('eventForm');
    if (eventForm) {
        eventForm.addEventListener('submit', createEvent);
    }

    // Load initial data
    if (document.getElementById('eventsList') || document.getElementById('eventsContainer')) {
        loadEvents();
    }
});
