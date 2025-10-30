document.addEventListener('DOMContentLoaded', () => {
    const registrationForm = document.getElementById('registration-form');
    
    // Initial load of the dashboard data from the Python server
    loadRegistrations();

    // Event listener for form submission
    registrationForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Package form data as a JavaScript object
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            event: document.getElementById('event').value
        };

        // Send data to the Python backend
        handleRegistrationSubmission(formData);
    });
});


/**
 * Sends registration data to the Python backend via a POST request.
 */
async function handleRegistrationSubmission(formData) {
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const data = await response.json();

        if (response.ok) {
            // Success response (HTTP 201)
            document.getElementById('registration-form').reset(); 
            displayMessage(`✅ ${data.message} ID: ${data.record.id}`, 'success');
            loadRegistrations(); // Refresh dashboard
        } else {
            // Error response (HTTP 400, 409, etc.)
            displayMessage(`🔴 ERROR! ${data.message}`, 'error');
        }

    } catch (error) {
        console.error('Network or server error:', error);
        displayMessage('❌ Could not connect to the server.', 'error');
    }
}


/**
 * Fetches all registration data from the Python backend (API GET).
 */
async function loadRegistrations() {
    const tbody = document.getElementById('registrations-tbody');
    const totalElement = document.getElementById('total-registrations');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Loading...</td></tr>';

    try {
        const response = await fetch('/api/registrations');
        const registrations = await response.json();
        
        tbody.innerHTML = ''; 
        totalElement.textContent = registrations.length;

        if (registrations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No participants registered yet.</td></tr>';
            return;
        }

        // Populate table rows
        registrations.forEach(reg => {
            const row = tbody.insertRow();
            row.insertCell().textContent = reg.id;
            row.insertCell().textContent = reg.name;
            row.insertCell().textContent = reg.email;
            row.insertCell().textContent = reg.event;
            row.insertCell().textContent = reg.registration_date.split(' ')[0]; // Show just the date
        });

    } catch (error) {
        console.error('Failed to fetch registrations:', error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Failed to load data. Is the server running?</td></tr>';
        totalElement.textContent = 'ERROR';
    }
}


/**
 * Displays feedback messages (success/error) to the user.
 */
function displayMessage(text, type) {
    const messageArea = document.getElementById('message-area');
    messageArea.textContent = text;
    messageArea.className = `message ${type}`; 
    messageArea.style.display = 'block';
    
    // Hide message after a few seconds
    setTimeout(() => {
        messageArea.style.display = 'none';
    }, 5000);
}