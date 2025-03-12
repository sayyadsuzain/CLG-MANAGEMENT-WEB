// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const LOGIN_ENDPOINT = `${API_BASE_URL}/users/login/`;
const REGISTER_ENDPOINT = `${API_BASE_URL}/users/register/`;

// Store registered users in localStorage
function getRegisteredUsers() {
    const users = localStorage.getItem('registeredUsers');
    return users ? JSON.parse(users) : [];
}

function addRegisteredUser(userData) {
    const users = getRegisteredUsers();
    users.push(userData);
    localStorage.setItem('registeredUsers', JSON.stringify(users));
}

// Function to register a student email
function registerStudent(email) {
    const registeredStudents = JSON.parse(localStorage.getItem('registeredStudents') || '[]');
    if (!registeredStudents.includes(email)) {
        registeredStudents.push(email);
        localStorage.setItem('registeredStudents', JSON.stringify(registeredStudents));
    }
}

// Handle login form submission
async function handleLogin(userType) {
    event.preventDefault();
    console.log('Login handler called for:', userType);
    
    try {
        // Get email and password based on user type
        const email = document.getElementById(`${userType}Email`).value;
        const password = document.getElementById(`${userType}Password`).value;

        console.log('Login attempt with:', { email, userType });

        if (!email || !password || !userType) {
            showAlert('Error', 'Please fill in all required fields');
            console.error('Missing required fields:', { email: !!email, password: !!password, userType: !!userType });
            return false;
        }

        // Check if user exists in registered users
        const registeredUsers = getRegisteredUsers();
        console.log('Checking registered users:', registeredUsers);
        
        const user = registeredUsers.find(u => 
            u.email === email && 
            u.password === password && 
            u.userType === userType
        );

        if (!user) {
            showAlert('Error', 'Invalid credentials or user not found');
            console.error('User not found or invalid credentials');
            return false;
        }

        console.log('User found:', user);

        // Create user data for storage
        const userData = {
            id: user.id || Date.now().toString(),
            email: user.email,
            full_name: user.full_name,
            userType: user.userType
        };

        // Store authentication data consistently
        localStorage.setItem('userData', JSON.stringify(userData));
        localStorage.setItem('accessToken', 'mock_token_' + Date.now());
        localStorage.setItem('authToken', 'mock_token_' + Date.now()); // For backward compatibility
        localStorage.setItem('userType', userType);

        // Show success message
        showAlert('Success', 'Login successful! Redirecting...');
        console.log('Login successful, preparing to redirect');

        // Redirect after a short delay
        setTimeout(() => {
            const redirectPath = userType === 'student' ? './student/dashboard.html' : './faculty/dashboard.html';
            console.log('Redirecting to:', redirectPath);
            window.location.href = redirectPath;
        }, 1500);

        // Register student email if not already registered
        if (userType === 'student') {
            registerStudent(email);
        }

    } catch (error) {
        console.error('Login error:', error);
        showAlert('Error', 'Failed to log in. Please try again.');
    }
    
    return false; // Prevent form submission
}

// Handle registration form submission
async function handleRegistration(userType) {
    try {
        console.log('Starting registration process for:', userType);

        // Show loading state
        const submitButton = document.querySelector(`#${userType}RegisterForm button[type="submit"]`);
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = 'Registering...';

        const name = document.getElementById(`${userType}RegName`).value;
        const email = document.getElementById(`${userType}RegEmail`).value;
        const password = document.getElementById(`${userType}RegPassword`).value;
        const confirmPassword = document.getElementById(`${userType}RegConfirmPassword`).value;

        // Validate passwords match
        if (password !== confirmPassword) {
            throw new Error('Passwords do not match');
        }

        // Check if email already exists
        const registeredUsers = getRegisteredUsers();
        if (registeredUsers.some(user => user.email === email)) {
            throw new Error('This email is already registered. Please use a different email.');
        }

        // Create new user data
        const userData = {
            full_name: name,
            email: email,
            password: password, // In a real app, this should be hashed
            userType: userType
        };

        // Add type-specific fields
        if (userType === 'student') {
            userData.roll_number = document.getElementById('studentRegRollNo').value;
        } else {
            userData.department = document.getElementById('facultyRegDepartment').value;
        }

        // Store the new user
        addRegisteredUser(userData);

        // Store the registered email for login
        sessionStorage.setItem('lastRegisteredEmail', email);
        sessionStorage.setItem('lastRegisteredType', userType);

        // Show success message
        showAlert('Success', 'Registration successful! You can now login with your credentials.');
        
        // Switch to login tab
        setTimeout(() => {
            try {
                // Switch to main login tab
                const loginTab = document.getElementById('login-tab');
                if (loginTab) {
                    loginTab.click();
                }

                // Short delay before switching to specific login tab
                setTimeout(() => {
                    // Switch to specific user type login tab
                    const userLoginTab = document.getElementById(`${userType}-login-tab`);
                    if (userLoginTab) {
                        userLoginTab.click();
                    }

                    // Fill in email
                    const emailField = document.getElementById(`${userType}Email`);
                    if (emailField) {
                        emailField.value = email;
                    }

                    // Clear registration form
                    const form = document.getElementById(`${userType}RegisterForm`);
                    if (form) {
                        form.reset();
                    }
                }, 300);
            } catch (tabError) {
                console.error('Error switching tabs:', tabError);
            }
        }, 1500);

    } catch (error) {
        console.error('Registration error:', error);
        showAlert('Error', error.message);
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }

    return false; // Prevent form submission
}

// Show alert modal
function showAlert(title, message) {
    try {
        const modalElement = document.getElementById('alertModal');
        const modal = new bootstrap.Modal(modalElement);
        document.getElementById('alertModalTitle').textContent = title;
        document.getElementById('alertModalBody').textContent = message;
        modal.show();
    } catch (error) {
        console.error('Error showing alert:', error);
        // Fallback to basic alert
        alert(`${title}: ${message}`);
    }
}

// Handle forgot password
function showForgotPassword() {
    showAlert('Forgot Password', 'Please contact the administrator to reset your password.');
}

// Check if user is already logged in
function checkAuth() {
    const userData = JSON.parse(localStorage.getItem('userData'));
    const authToken = localStorage.getItem('accessToken');
    
    if (userData && authToken) {
        // Check if token is still valid
        fetch('http://localhost:8000/api/users/verify-token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            }
        })
        .then(response => {
            if (response.ok) {
                // Token is valid, redirect to appropriate dashboard
                if (userData.userType === 'student') {
                    window.location.href = '/student/dashboard.html';
                } else if (userData.userType === 'faculty') {
                    window.location.href = '/faculty/dashboard.html';
                }
            } else {
                // Token is invalid, clear storage
                localStorage.removeItem('userData');
                localStorage.removeItem('accessToken');
            }
        })
        .catch(error => {
            console.error('Token verification error:', error);
        });
    }
}

// Logout function
function logout() {
    console.log('Logging out...');
    
    // Clear all authentication data
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userType');
    localStorage.removeItem('userData');
    
    console.log('Redirecting to login page...');
    window.location.href = '/login.html';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded, initializing...');

    // Check if user is already logged in
    checkAuth();

    // Add login form submit handlers
    const studentLoginForm = document.getElementById('studentLoginForm');
    const facultyLoginForm = document.getElementById('facultyLoginForm');
    
    if (studentLoginForm) {
        studentLoginForm.addEventListener('submit', () => handleLogin('student'));
    }
    
    if (facultyLoginForm) {
        facultyLoginForm.addEventListener('submit', () => handleLogin('faculty'));
    }

    // Add password validation listeners
    ['student', 'faculty'].forEach(type => {
        const password = document.getElementById(`${type}RegPassword`);
        const confirmPassword = document.getElementById(`${type}RegConfirmPassword`);
        
        if (password && confirmPassword) {
            confirmPassword.addEventListener('input', () => {
                if (password.value !== confirmPassword.value) {
                    confirmPassword.setCustomValidity('Passwords do not match');
                } else {
                    confirmPassword.setCustomValidity('');
                }
            });
        }
    });

    // Auto-fill email if coming from registration
    const lastRegisteredEmail = sessionStorage.getItem('lastRegisteredEmail');
    const lastRegisteredType = sessionStorage.getItem('lastRegisteredType');
    
    if (lastRegisteredEmail && lastRegisteredType) {
        console.log('Found previously registered email, auto-filling...');
        
        const emailField = document.getElementById(`${lastRegisteredType}Email`);
        if (emailField) {
            emailField.value = lastRegisteredEmail;
        }
        
        // Clear stored data
        sessionStorage.removeItem('lastRegisteredEmail');
        sessionStorage.removeItem('lastRegisteredType');
    }
}); 