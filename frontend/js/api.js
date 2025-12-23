/**
 * API Configuration and HTTP Client
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Get authentication token from localStorage
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Get current user from localStorage
 */
function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

/**
 * Save authentication data to localStorage
 */
function saveAuth(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

/**
 * Clear authentication data
 */
function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!getToken();
}

/**
 * Make authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        ...options.headers
    };

    // Add auth header if token exists
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Add content type for JSON requests
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    // Handle 401 - redirect to login
    if (response.status === 401) {
        clearAuth();
        window.location.href = '/login.html';
        throw new Error('Session expired');
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'An error occurred');
    }

    return data;
}

// ============================================
// AUTH API
// ============================================

async function register(email, password, fullName, role) {
    const data = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
            email,
            password,
            full_name: fullName,
            role
        })
    });
    saveAuth(data.access_token, data.user);
    return data;
}

async function login(email, password) {
    const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
    saveAuth(data.access_token, data.user);
    return data;
}

function logout() {
    clearAuth();
    window.location.href = '/index.html';
}

async function getMe() {
    return apiRequest('/auth/me');
}

// ============================================
// JOBS API
// ============================================

async function getJobs() {
    return apiRequest('/jobs');
}

async function getJob(jobId) {
    return apiRequest(`/jobs/${jobId}`);
}

async function getMyPostings() {
    return apiRequest('/jobs/my-postings');
}

async function createJob(jobData) {
    return apiRequest('/jobs', {
        method: 'POST',
        body: JSON.stringify(jobData)
    });
}

async function updateJob(jobId, jobData) {
    return apiRequest(`/jobs/${jobId}`, {
        method: 'PUT',
        body: JSON.stringify(jobData)
    });
}

async function deleteJob(jobId) {
    return apiRequest(`/jobs/${jobId}`, {
        method: 'DELETE'
    });
}

// ============================================
// APPLICATIONS API
// ============================================

async function applyToJob(jobId, resumeFile) {
    const formData = new FormData();
    formData.append('job_id', jobId);
    formData.append('resume', resumeFile);

    return apiRequest('/applications', {
        method: 'POST',
        body: formData
    });
}

async function getMyApplications() {
    return apiRequest('/applications/my-applications');
}

async function getApplicationsForJob(jobId) {
    return apiRequest(`/applications/job/${jobId}`);
}

async function getApplication(applicationId) {
    return apiRequest(`/applications/${applicationId}`);
}

async function updateApplicationStatus(applicationId, status) {
    return apiRequest(`/applications/${applicationId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status })
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Get status badge class
 */
function getStatusBadgeClass(status) {
    const classes = {
        'pending': 'badge-warning',
        'reviewed': 'badge-info',
        'shortlisted': 'badge-success',
        'rejected': 'badge-danger',
        'hired': 'badge-success',
        'active': 'badge-success',
        'closed': 'badge-danger',
        'draft': 'badge-warning'
    };
    return classes[status] || 'badge-primary';
}

/**
 * Get score color based on value
 */
function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#6366f1';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
}

/**
 * Create score ring SVG
 */
function createScoreRing(score, size = 80) {
    const radius = (size - 8) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    const color = getScoreColor(score);

    return `
        <div class="score-ring" style="width: ${size}px; height: ${size}px;">
            <svg width="${size}" height="${size}">
                <circle cx="${size / 2}" cy="${size / 2}" r="${radius}" class="bg"/>
                <circle cx="${size / 2}" cy="${size / 2}" r="${radius}" class="progress" 
                    style="stroke: ${color}; stroke-dasharray: ${circumference}; stroke-dashoffset: ${offset}"/>
            </svg>
            <span class="score-value" style="color: ${color}">${score}</span>
        </div>
    `;
}

/**
 * Show loading spinner
 */
function showLoading(container) {
    container.innerHTML = '<div class="flex justify-center mt-xl"><div class="spinner"></div></div>';
}

/**
 * Show error message
 */
function showError(container, message) {
    container.innerHTML = `<div class="alert alert-error">${message}</div>`;
}

/**
 * Show empty state
 */
function showEmptyState(container, title, message, actionHtml = '') {
    container.innerHTML = `
        <div class="empty-state">
            <svg class="empty-state-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
            <h3 class="empty-state-title">${title}</h3>
            <p class="empty-state-text">${message}</p>
            ${actionHtml}
        </div>
    `;
}
