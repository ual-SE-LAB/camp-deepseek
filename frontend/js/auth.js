// Auth state management
let currentUser = null;
let authListeners = [];

function addAuthListener(listener) {
    authListeners.push(listener);
    if (currentUser) {
        listener(currentUser);
    }
}

function removeAuthListener(listener) {
    authListeners = authListeners.filter(l => l !== listener);
}

function notifyAuthListeners() {
    authListeners.forEach(listener => listener(currentUser));
}

// Check if user is logged in
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        setCurrentUser(null);
        return false;
    }
    
    try {
        const user = await authAPI.getMe();
        setCurrentUser(user);
        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        logout();
        return false;
    }
}

function setCurrentUser(user) {
    currentUser = user;
    notifyAuthListeners();
    updateNavigation();
}

// Login
async function login(email, password) {
    try {
        const data = await authAPI.login(email, password);
        localStorage.setItem('token', data.access_token);
        const user = await authAPI.getMe();
        setCurrentUser(user);
        showToast('Login successful!', 'success');
        return true;
    } catch (error) {
        showToast(error.message, 'error');
        return false;
    }
}

// Register
async function register(userData) {
    try {
        await authAPI.register(userData);
        showToast('Registration successful! Please login.', 'success');
        return true;
    } catch (error) {
        showToast(error.message, 'error');
        return false;
    }
}

// Logout
function logout() {
    localStorage.removeItem('token');
    setCurrentUser(null);
    showToast('Logged out successfully', 'info');
    renderAuthPage();
}

// Check if user is admin
function isAdmin() {
    return currentUser && currentUser.role === 'admin';
}

// Update navigation based on auth state
function updateNavigation() {
    const navMenu = document.getElementById('navMenu');
    if (!navMenu) return;
    
    if (currentUser) {
        navMenu.innerHTML = `
            <span>Welcome, ${currentUser.full_name}</span>
            ${isAdmin() ? `
                <a href="#" onclick="renderAdminDashboard()">Dashboard</a>
                <a href="#" onclick="renderParentsList()">Parents</a>
                <a href="#" onclick="renderCampersList()">Campers</a>
            ` : `
                <a href="#" onclick="renderParentDashboard()">My Campers</a>
                <a href="#" onclick="renderAddCamperForm()">Add Camper</a>
            `}
            <button class="btn-logout" onclick="logout()">Logout</button>
        `;
    } else {
        navMenu.innerHTML = `
            <button class="btn-primary" onclick="renderAuthPage()">Login / Register</button>
        `;
    }
}