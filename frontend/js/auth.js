/**
 * Authentication UI Handler
 */

/**
 * Initialize navbar with auth state
 */
function initNavbar() {
    const user = getCurrentUser();
    const navbarUser = document.getElementById('navbar-user');
    const navbarNav = document.getElementById('navbar-nav');

    if (!navbarUser || !navbarNav) return;

    if (user) {
        // Show user info and dashboard link
        const dashboardLink = user.role === 'hr' ? 'hr-dashboard.html' : 'applicant-dashboard.html';

        navbarNav.innerHTML = `
            <li><a href="jobs.html">Browse Jobs</a></li>
            <li><a href="${dashboardLink}">Dashboard</a></li>
        `;

        navbarUser.innerHTML = `
            <span class="user-badge">${user.role.toUpperCase()}</span>
            <span class="text-secondary">${user.full_name}</span>
            <button class="btn btn-outline btn-sm" onclick="logout()">Logout</button>
        `;
    } else {
        // Show login/register links
        navbarNav.innerHTML = `
            <li><a href="jobs.html">Browse Jobs</a></li>
        `;

        navbarUser.innerHTML = `
            <a href="login.html" class="btn btn-outline btn-sm">Login</a>
            <a href="register.html" class="btn btn-primary btn-sm">Register</a>
        `;
    }
}

/**
 * Protect page - redirect if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

/**
 * Require specific role
 */
function requireRole(role) {
    const user = getCurrentUser();
    if (!user || user.role !== role) {
        window.location.href = '/index.html';
        return false;
    }
    return true;
}

/**
 * Redirect if already logged in
 */
function redirectIfLoggedIn() {
    if (isAuthenticated()) {
        const user = getCurrentUser();
        const redirectUrl = user.role === 'hr' ? '/hr-dashboard.html' : '/applicant-dashboard.html';
        window.location.href = redirectUrl;
    }
}

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('form-error');
    const submitBtn = event.target.querySelector('button[type="submit"]');

    try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner spinner-sm"></span> Logging in...';

        const data = await login(email, password);

        // Redirect based on role
        const redirectUrl = data.user.role === 'hr' ? '/hr-dashboard.html' : '/applicant-dashboard.html';
        window.location.href = redirectUrl;
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
}

/**
 * Handle registration form submission
 */
async function handleRegister(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const fullName = document.getElementById('fullName').value;
    const activeBtn = document.querySelector('.role-toggle-btn.active');
    const role = activeBtn ? activeBtn.dataset.role : 'applicant';
    const errorDiv = document.getElementById('form-error');
    const submitBtn = event.target.querySelector('button[type="submit"]');

    try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner spinner-sm"></span> Creating account...';

        const data = await register(email, password, fullName, role);

        // Redirect based on role
        const redirectUrl = data.user.role === 'hr' ? '/hr-dashboard.html' : '/applicant-dashboard.html';
        window.location.href = redirectUrl;
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
    }
}

/**
 * Initialize role toggle buttons
 */
function initRoleToggle() {
    const buttons = document.querySelectorAll('.role-toggle-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();

    // Initialize role toggle if present
    const roleToggle = document.querySelector('.role-toggle');
    if (roleToggle) {
        initRoleToggle();
    }
});
