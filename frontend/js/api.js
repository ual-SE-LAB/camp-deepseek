// API Configuration
const API_BASE_URL = '/api';

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'API call failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth API
const authAPI = {
    login: (email, password) => apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    }),
    
    register: (userData) => apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
    }),
    
    getMe: () => apiCall('/auth/me')
};

// Parents API
const parentsAPI = {
    getMyCampers: () => apiCall('/parents/me/campers'),
    
    addCamper: (camperData) => apiCall('/parents/me/campers', {
        method: 'POST',
        body: JSON.stringify(camperData)
    }),
    
    updateCamper: (camperId, camperData) => apiCall(`/parents/me/campers/${camperId}`, {
        method: 'PUT',
        body: JSON.stringify(camperData)
    }),
    
    deleteCamper: (camperId) => apiCall(`/parents/me/campers/${camperId}`, {
        method: 'DELETE'
    })
};

// Admin API
const adminAPI = {
    // Parent management
    getParents: () => apiCall('/admin/parents'),
    
    createParent: (parentData) => apiCall('/admin/parents', {
        method: 'POST',
        body: JSON.stringify(parentData)
    }),
    
    updateParent: (parentId, parentData) => apiCall(`/admin/parents/${parentId}`, {
        method: 'PUT',
        body: JSON.stringify(parentData)
    }),
    
    deleteParent: (parentId) => apiCall(`/admin/parents/${parentId}`, {
        method: 'DELETE'
    }),
    
    // Camper management
    getCampers: () => apiCall('/admin/campers'),
    
    createCamper: (camperData) => apiCall('/admin/campers', {
        method: 'POST',
        body: JSON.stringify(camperData)
    }),
    
    updateCamper: (camperId, camperData) => apiCall(`/admin/campers/${camperId}`, {
        method: 'PUT',
        body: JSON.stringify(camperData)
    }),
    
    deleteCamper: (camperId) => apiCall(`/admin/campers/${camperId}`, {
        method: 'DELETE'
    }),
    
    linkCamperToParent: (camperId, parentId, relationship = 'parent') => 
        apiCall(`/admin/campers/${camperId}/link-parent/${parentId}?relationship=${relationship}`, {
            method: 'POST'
        })
};
