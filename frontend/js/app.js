// Main application logic
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication status
    checkAuth().then(authenticated => {
        if (authenticated) {
            if (isAdmin()) {
                renderAdminDashboard();
            } else {
                renderParentDashboard();
            }
        } else {
            renderAuthPage();
        }
    });
});

// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Loading spinner
function showLoading() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = '<div class="spinner"></div>';
}

// Render authentication page
function renderAuthPage() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="auth-container">
            <div class="auth-tabs">
                <button class="auth-tab active" onclick="showLoginForm()">Login</button>
                <button class="auth-tab" onclick="showRegisterForm()">Register</button>
            </div>
            <div id="authFormContainer" class="auth-form">
                ${getLoginForm()}
            </div>
        </div>
    `;
}

function getLoginForm() {
    return `
        <h2>Login to CampManager</h2>
        <form onsubmit="handleLogin(event)">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
    `;
}

function getRegisterForm() {
    return `
        <h2>Create an Account</h2>
        <form onsubmit="handleRegister(event)">
            <div class="form-group">
                <label for="fullName">Full Name</label>
                <input type="text" id="fullName" required>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" required>
            </div>
            <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" required minlength="6">
            </div>
            <div class="form-group">
                <label for="confirmPassword">Confirm Password</label>
                <input type="password" id="confirmPassword" required>
            </div>
            <button type="submit" class="btn btn-primary">Register</button>
        </form>
    `;
}

function showLoginForm() {
    document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('authFormContainer').innerHTML = getLoginForm();
}

function showRegisterForm() {
    document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('authFormContainer').innerHTML = getRegisterForm();
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const success = await login(email, password);
    if (success) {
        if (isAdmin()) {
            renderAdminDashboard();
        } else {
            renderParentDashboard();
        }
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    const userData = {
        full_name: document.getElementById('fullName').value,
        email: document.getElementById('email').value,
        phone_number: document.getElementById('phone').value,
        password: password,
        role: 'parent'
    };
    
    const success = await register(userData);
    if (success) {
        showLoginForm();
    }
}

// Parent Dashboard
async function renderParentDashboard() {
    showLoading();
    try {
        const campers = await parentsAPI.getMyCampers();
        renderParentCampers(campers);
    } catch (error) {
        showToast('Failed to load campers', 'error');
    }
}

function renderParentCampers(campers) {
    const mainContent = document.getElementById('mainContent');
    
    if (campers.length === 0) {
        mainContent.innerHTML = `
            <div class="card">
                <h2>My Campers</h2>
                <p>You haven't added any campers yet.</p>
                <button class="btn btn-primary" onclick="renderAddCamperForm()">Add Your First Camper</button>
            </div>
        `;
        return;
    }
    
    mainContent.innerHTML = `
        <div class="card">
            <h2>My Campers</h2>
            <button class="btn btn-primary" onclick="renderAddCamperForm()">Add New Camper</button>
        </div>
        <div class="campers-grid">
            ${campers.map(camper => `
                <div class="camper-card">
                    <h3>${camper.first_name} ${camper.last_name}</h3>
                    <p><strong>Date of Birth:</strong> ${new Date(camper.date_of_birth).toLocaleDateString()}</p>
                    <p><strong>Gender:</strong> ${camper.gender || 'Not specified'}</p>
                    ${camper.allergies ? `<p><strong>Allergies:</strong> ${camper.allergies}</p>` : ''}
                    ${camper.medical_conditions ? `<p><strong>Medical Conditions:</strong> ${camper.medical_conditions}</p>` : ''}
                    <div style="margin-top: 1rem;">
                        <button class="btn btn-secondary" onclick="renderEditCamperForm(${camper.id})">Edit</button>
                        <button class="btn btn-danger" onclick="deleteCamper(${camper.id})">Delete</button>
                        <button class="btn btn-primary" onclick="viewEmergencyContacts(${camper.id})">Emergency Contacts</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderAddCamperForm() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="card">
            <h2>Add New Camper</h2>
            <form onsubmit="handleAddCamper(event)">
                <h3>Camper Information</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="firstName">First Name *</label>
                        <input type="text" id="firstName" required>
                    </div>
                    <div class="form-group">
                        <label for="lastName">Last Name *</label>
                        <input type="text" id="lastName" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="dob">Date of Birth *</label>
                        <input type="date" id="dob" required>
                    </div>
                    <div class="form-group">
                        <label for="gender">Gender</label>
                        <select id="gender">
                            <option value="">Select...</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                </div>
                
                <h3>Medical Information</h3>
                <div class="form-group">
                    <label for="allergies">Allergies</label>
                    <textarea id="allergies" rows="2"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="medicalConditions">Medical Conditions</label>
                    <textarea id="medicalConditions" rows="2"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="medications">Medications</label>
                    <textarea id="medications" rows="2"></textarea>
                </div>
                
                <h3>Doctor Information</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="doctorName">Doctor's Name</label>
                        <input type="text" id="doctorName">
                    </div>
                    <div class="form-group">
                        <label for="doctorPhone">Doctor's Phone</label>
                        <input type="tel" id="doctorPhone">
                    </div>
                </div>
                
                <h3>Insurance Information</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="insuranceProvider">Insurance Provider</label>
                        <input type="text" id="insuranceProvider">
                    </div>
                    <div class="form-group">
                        <label for="policyNumber">Policy Number</label>
                        <input type="text" id="policyNumber">
                    </div>
                </div>
                
                <h3>Emergency Contacts</h3>
                <div id="emergencyContacts">
                    <!-- Emergency contact fields will be added here -->
                </div>
                <button type="button" class="btn btn-secondary" onclick="addEmergencyContactField()">Add Another Emergency Contact</button>
                
                <div class="form-group">
                    <label for="specialNeeds">Special Needs / Notes</label>
                    <textarea id="specialNeeds" rows="3"></textarea>
                </div>
                
                <div style="margin-top: 1rem;">
                    <button type="submit" class="btn btn-primary">Add Camper</button>
                    <button type="button" class="btn" onclick="renderParentDashboard()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    // Initialize with one emergency contact
    addEmergencyContactField();
}

let emergencyContactCount = 0;

function addEmergencyContactField() {
    const container = document.getElementById('emergencyContacts');
    const contactId = emergencyContactCount++;
    
    const contactHtml = `
        <div class="emergency-contact" id="contact-${contactId}" style="margin-bottom: 1rem; padding: 1rem; border: 1px solid #e0e0e0; border-radius: 6px;">
            <h4>Emergency Contact ${emergencyContactCount}</h4>
            <div class="form-row">
                <div class="form-group">
                    <label>Full Name *</label>
                    <input type="text" class="contact-name" required>
                </div>
                <div class="form-group">
                    <label>Relationship *</label>
                    <input type="text" class="contact-relationship" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Phone Number *</label>
                    <input type="tel" class="contact-phone" required>
                </div>
                <div class="form-group">
                    <label>Alternate Phone</label>
                    <input type="tel" class="contact-alt-phone">
                </div>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" class="contact-email">
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" class="contact-primary" onchange="updatePrimaryContact(this, ${contactId})">
                    Primary Emergency Contact
                </label>
            </div>
            ${emergencyContactCount > 1 ? `
                <button type="button" class="btn btn-danger" onclick="removeEmergencyContact(${contactId})">Remove</button>
            ` : ''}
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', contactHtml);
}

function updatePrimaryContact(checkbox, contactId) {
    if (checkbox.checked) {
        // Uncheck all other primary contacts
        document.querySelectorAll('.contact-primary').forEach(cb => {
            if (cb !== checkbox) {
                cb.checked = false;
            }
        });
    }
}

function removeEmergencyContact(contactId) {
    document.getElementById(`contact-${contactId}`).remove();
    emergencyContactCount--;
}

async function handleAddCamper(event) {
    event.preventDefault();
    
    // Collect camper data
    const camperData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        date_of_birth: document.getElementById('dob').value,
        gender: document.getElementById('gender').value || null,
        allergies: document.getElementById('allergies').value || null,
        medical_conditions: document.getElementById('medicalConditions').value || null,
        medications: document.getElementById('medications').value || null,
        doctor_name: document.getElementById('doctorName').value || null,
        doctor_phone: document.getElementById('doctorPhone').value || null,
        insurance_provider: document.getElementById('insuranceProvider').value || null,
        insurance_policy_number: document.getElementById('policyNumber').value || null,
        special_needs: document.getElementById('specialNeeds').value || null,
        emergency_contacts: []
    };
    
    // Collect emergency contacts
    const contacts = document.querySelectorAll('.emergency-contact');
    contacts.forEach(contact => {
        const contactData = {
            full_name: contact.querySelector('.contact-name').value,
            relationship: contact.querySelector('.contact-relationship').value,
            phone_number: contact.querySelector('.contact-phone').value,
            alternate_phone: contact.querySelector('.contact-alt-phone').value || null,
            email: contact.querySelector('.contact-email').value || null,
            is_primary: contact.querySelector('.contact-primary').checked
        };
        
        // Validate required fields
        if (!contactData.full_name || !contactData.relationship || !contactData.phone_number) {
            throw new Error('All emergency contacts require name, relationship, and phone number');
        }
        
        camperData.emergency_contacts.push(contactData);
    });
    
    // Validate at least one primary contact
    if (!camperData.emergency_contacts.some(c => c.is_primary)) {
        showToast('Please select a primary emergency contact', 'error');
        return;
    }
    
    try {
        await parentsAPI.addCamper(camperData);
        showToast('Camper added successfully!', 'success');
        renderParentDashboard();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteCamper(camperId) {
    if (!confirm('Are you sure you want to delete this camper?')) {
        return;
    }
    
    try {
        await parentsAPI.deleteCamper(camperId);
        showToast('Camper deleted successfully', 'success');
        renderParentDashboard();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function viewEmergencyContacts(camperId) {
    // This would fetch and display emergency contacts
    // For Sprint 1, we'll implement a simple view
    showToast('Emergency contacts feature coming soon!', 'info');
}

// Admin Dashboard
async function renderAdminDashboard() {
    showLoading();
    try {
        const [parents, campers] = await Promise.all([
            adminAPI.getParents(),
            adminAPI.getCampers()
        ]);
        
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="card">
                <h2>Admin Dashboard</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    <div class="stat-card" style="text-align: center; padding: 1rem; background: #f0f0f0; border-radius: 8px;">
                        <h3 style="font-size: 2rem; color: #667eea;">${parents.length}</h3>
                        <p>Total Parents</p>
                    </div>
                    <div class="stat-card" style="text-align: center; padding: 1rem; background: #f0f0f0; border-radius: 8px;">
                        <h3 style="font-size: 2rem; color: #48bb78;">${campers.length}</h3>
                        <p>Total Campers</p>
                    </div>
                </div>
                <div style="margin-top: 2rem;">
                    <button class="btn btn-primary" onclick="renderParentsList()">Manage Parents</button>
                    <button class="btn btn-primary" onclick="renderCampersList()" style="margin-left: 1rem;">Manage Campers</button>
                </div>
            </div>
        `;
    } catch (error) {
        showToast('Failed to load dashboard', 'error');
    }
}

async function renderParentsList() {
    showLoading();
    try {
        const parents = await adminAPI.getParents();
        
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="card">
                <h2>Manage Parents</h2>
                <button class="btn btn-primary" onclick="renderAddParentForm()">Add New Parent</button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Registered</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${parents.map(parent => `
                            <tr>
                                <td>${parent.full_name}</td>
                                <td>${parent.email}</td>
                                <td>${parent.phone_number || 'N/A'}</td>
                                <td>${new Date(parent.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-secondary btn-small" onclick="renderEditParentForm(${parent.id})">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="deleteParent(${parent.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        showToast('Failed to load parents', 'error');
    }
}

async function renderCampersList() {
    showLoading();
    try {
        const campers = await adminAPI.getCampers();
        
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="card">
                <h2>Manage Campers</h2>
                <button class="btn btn-primary" onclick="renderAddCamperFormAdmin()">Add New Camper</button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Date of Birth</th>
                            <th>Gender</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${campers.map(camper => `
                            <tr>
                                <td>${camper.first_name} ${camper.last_name}</td>
                                <td>${new Date(camper.date_of_birth).toLocaleDateString()}</td>
                                <td>${camper.gender || 'N/A'}</td>
                                <td>${camper.is_active ? 'Active' : 'Inactive'}</td>
                                <td>
                                    <button class="btn btn-secondary btn-small" onclick="renderEditCamperFormAdmin(${camper.id})">Edit</button>
                                    <button class="btn btn-primary btn-small" onclick="renderLinkParentForm(${camper.id})">Link Parent</button>
                                    <button class="btn btn-danger btn-small" onclick="deleteCamperAdmin(${camper.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        showToast('Failed to load campers', 'error');
    }
}

// Make functions globally available
window.showLoginForm = showLoginForm;
window.showRegisterForm = showRegisterForm;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.logout = logout;
window.renderAuthPage = renderAuthPage;
window.renderParentDashboard = renderParentDashboard;
window.renderAddCamperForm = renderAddCamperForm;
window.addEmergencyContactField = addEmergencyContactField;
window.handleAddCamper = handleAddCamper;
window.deleteCamper = deleteCamper;
window.viewEmergencyContacts = viewEmergencyContacts;
window.renderAdminDashboard = renderAdminDashboard;
window.renderParentsList = renderParentsList;
window.renderCampersList = renderCampersList;