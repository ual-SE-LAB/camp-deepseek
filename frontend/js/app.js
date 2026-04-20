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
    if (!container) return;
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
                <button class="auth-tab active" onclick="showLoginForm(event)">Login</button>
                <button class="auth-tab" onclick="showRegisterForm(event)">Register</button>
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

function showLoginForm(event) {
    if(event) {
        document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
    }
    document.getElementById('authFormContainer').innerHTML = getLoginForm();
}

function showRegisterForm(event) {
    if(event) {
        document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
    }
    document.getElementById('authFormContainer').innerHTML = getRegisterForm();
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const success = await login(email, password);
        if (success) {
            if (isAdmin()) {
                renderAdminDashboard();
            } else {
                renderParentDashboard();
            }
        }
    } catch (error) {
        showToast(error.message, 'error');
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
    
    try {
        const success = await register(userData);
        if (success) {
            showLoginForm();
        }
    } catch (error) {
        showToast(error.message, 'error');
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
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2>My Campers</h2>
                <button class="btn btn-primary" onclick="renderAddCamperForm()">Add New Camper</button>
            </div>
        </div>
        <div class="campers-grid">
            ${campers.map(camper => `
                <div class="camper-card">
                    <h3>${camper.first_name} ${camper.last_name}</h3>
                    <p><strong>Date of Birth:</strong> ${new Date(camper.date_of_birth).toLocaleDateString()}</p>
                    <p><strong>Gender:</strong> ${camper.gender || 'Not specified'}</p>
                    ${camper.allergies ? `<p><strong>Allergies:</strong> ${camper.allergies}</p>` : ''}
                    <div style="margin-top: 1rem;">
                        <button class="btn btn-secondary btn-small" onclick="showToast('Edit coming soon', 'info')">Edit</button>
                        <button class="btn btn-danger btn-small" onclick="deleteCamper(${camper.id})">Delete</button>
                        <button class="btn btn-primary btn-small" onclick="viewEmergencyContacts(${camper.id})">Contacts</button>
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
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
                
                <h3>Medical Information</h3>
                <div class="form-group">
                    <label for="allergies">Allergies</label>
                    <textarea id="allergies" rows="2" placeholder="List any allergies..."></textarea>
                </div>
                
                <div class="form-group">
                    <label for="medicalConditions">Medical Conditions</label>
                    <textarea id="medicalConditions" rows="2"></textarea>
                </div>
                
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
                
                <h3>Emergency Contacts</h3>
                <div id="emergencyContacts">
                    </div>
                <button type="button" class="btn btn-secondary" style="margin-bottom: 1rem;" onclick="addEmergencyContactField()">+ Add Contact</button>
                
                <div class="form-group">
                    <label for="specialNeeds">Special Needs / Notes</label>
                    <textarea id="specialNeeds" rows="2"></textarea>
                </div>
                
                <div style="margin-top: 2rem; border-top: 1px solid #eee; padding-top: 1rem;">
                    <button type="submit" class="btn btn-primary">Save Camper</button>
                    <button type="button" class="btn btn-secondary" onclick="renderParentDashboard()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    emergencyContactCount = 0;
    addEmergencyContactField(true); // El primero es primario por defecto
}

let emergencyContactCount = 0;

function addEmergencyContactField(isFirst = false) {
    const container = document.getElementById('emergencyContacts');
    const contactId = emergencyContactCount++;
    
    const div = document.createElement('div');
    div.className = 'emergency-contact-box';
    div.id = `contact-group-${contactId}`;
    div.style = "background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #ddd;";
    
    div.innerHTML = `
        <div style="display: flex; justify-content: space-between;">
            <h4 style="margin:0 0 10px 0;">Contact #${contactId + 1}</h4>
            ${!isFirst ? `<button type="button" onclick="removeEmergencyContact(${contactId})" style="color:red; cursor:pointer; border:none; background:none;">Remove</button>` : ''}
        </div>
        <div class="form-row">
            <div class="form-group">
                <input type="text" class="contact-name" placeholder="Full Name *" required>
            </div>
            <div class="form-group">
                <input type="text" class="contact-relationship" placeholder="Relationship (e.g. Mother) *" required>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <input type="tel" class="contact-phone" placeholder="Phone Number *" required>
            </div>
            <div class="form-group">
                <label style="font-size: 0.8rem;">
                    <input type="checkbox" class="contact-primary" ${isFirst ? 'checked' : ''} onchange="updatePrimaryContact(this)"> 
                    Primary Contact
                </label>
            </div>
        </div>
    `;
    
    container.appendChild(div);
}

function updatePrimaryContact(checkbox) {
    if (checkbox.checked) {
        document.querySelectorAll('.contact-primary').forEach(cb => {
            if (cb !== checkbox) cb.checked = false;
        });
    }
}

function removeEmergencyContact(id) {
    const el = document.getElementById(`contact-group-${id}`);
    if(el) el.remove();
}

async function handleAddCamper(event) {
    event.preventDefault();
    
    const camperData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        date_of_birth: document.getElementById('dob').value,
        gender: document.getElementById('gender').value || "other",
        allergies: document.getElementById('allergies').value || "",
        medical_conditions: document.getElementById('medicalConditions').value || "",
        medications: "",
        doctor_name: document.getElementById('doctorName').value || "",
        doctor_phone: document.getElementById('doctorPhone').value || "",
        insurance_provider: "",
        insurance_policy_number: "",
        special_needs: document.getElementById('specialNeeds').value || "",
        notes: "",
        emergency_contacts: []
    };
    
    const contactElements = document.querySelectorAll('.emergency-contact-box');
    contactElements.forEach(el => {
        camperData.emergency_contacts.push({
            full_name: el.querySelector('.contact-name').value,
            relationship: el.querySelector('.contact-relationship').value,
            phone_number: el.querySelector('.contact-phone').value,
            is_primary: el.querySelector('.contact-primary').checked
        });
    });

    if (camperData.emergency_contacts.length === 0) {
        showToast('At least one emergency contact is required', 'error');
        return;
    }

    if (!camperData.emergency_contacts.some(c => c.is_primary)) {
        showToast('Please select one primary contact', 'error');
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
    if (!confirm('Are you sure you want to delete this camper?')) return;
    try {
        await parentsAPI.deleteCamper(camperId);
        showToast('Camper deleted', 'success');
        renderParentDashboard();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function viewEmergencyContacts(camperId) {
    showToast('Loading contacts...', 'info');
    // Implementación futura: abrir un modal con la lista de contactos
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
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div class="stat-card" style="background: #eef2ff; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="font-size: 2rem; color: #4f46e5; margin:0;">${parents.length}</h3>
                        <p style="margin:0; color: #666;">Parents</p>
                    </div>
                    <div class="stat-card" style="background: #f0fdf4; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="font-size: 2rem; color: #16a34a; margin:0;">${campers.length}</h3>
                        <p style="margin:0; color: #666;">Campers</p>
                    </div>
                </div>
                <div style="margin-top: 2rem; display: flex; gap: 10px;">
                    <button class="btn btn-primary" onclick="renderParentsList()">Manage Parents</button>
                    <button class="btn btn-primary" onclick="renderCampersList()">Manage Campers</button>
                </div>
            </div>
        `;
    } catch (error) {
        showToast('Error loading dashboard', 'error');
    }
}

async function renderParentsList() {
    showLoading();
    try {
        const parents = await adminAPI.getParents();
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
                <h2>Parents</h2>
                <button class="btn btn-secondary" onclick="renderAdminDashboard()">Back</button>
            </div>
            <div class="table-container card">
                <table>
                    <thead>
                        <tr><th>Name</th><th>Email</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                        ${parents.map(p => `
                            <tr>
                                <td>${p.full_name}</td>
                                <td>${p.email}</td>
                                <td>
                                    <button class="btn btn-danger btn-small" onclick="showToast('Admin delete disabled', 'info')">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (e) { showToast('Error'); }
}

async function renderCampersList() {
    showLoading();
    try {
        const campers = await adminAPI.getCampers();
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
                <h2>All Campers</h2>
                <button class="btn btn-secondary" onclick="renderAdminDashboard()">Back</button>
            </div>
            <div class="table-container card">
                <table>
                    <thead>
                        <tr><th>Name</th><th>Parent</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        ${campers.map(c => `
                            <tr>
                                <td>${c.first_name} ${c.last_name}</td>
                                <td>${c.parent_ids ? 'Linked' : 'No Parent'}</td>
                                <td>${c.is_active ? '✅' : '❌'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (e) { showToast('Error'); }
}

// Global Exports
window.showLoginForm = showLoginForm;
window.showRegisterForm = showRegisterForm;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.renderParentDashboard = renderParentDashboard;
window.renderAddCamperForm = renderAddCamperForm;
window.addEmergencyContactField = addEmergencyContactField;
window.handleAddCamper = handleAddCamper;
window.deleteCamper = deleteCamper;
window.updatePrimaryContact = updatePrimaryContact;
window.removeEmergencyContact = removeEmergencyContact;
window.renderAdminDashboard = renderAdminDashboard;
window.renderParentsList = renderParentsList;
window.renderCampersList = renderCampersList;