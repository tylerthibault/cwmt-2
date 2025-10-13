---
applyTo: '**/*.js'
---

# JavaScript Development Instructions for CWMT Flask Application

These instructions enforce JavaScript best practices and organizational standards defined in the project constitution.

## Core JavaScript Principles

### External Files Only (Constitutional)
JavaScript MUST be in external files under `static/js/` - NO inline JavaScript except minimal configuration:

```html
<!-- ❌ NEVER -->
<button onclick="alert('Hello')">Click</button>

<!-- ✅ ALWAYS -->
<button class="alert-button">Click</button>
```

```javascript
// static/js/main.js
document.querySelector('.alert-button').addEventListener('click', function() {
    alert('Hello');
});
```

### File Organization
```
static/js/
├── main.js              # Global application logic
├── components/          # Reusable component scripts
│   ├── forms.js
│   ├── navigation.js
│   └── modals.js
└── pages/              # Page-specific scripts
    ├── dashboard.js
    └── settings.js
```

## Code Structure Standards

### Function Organization
```javascript
// ✅ CORRECT - Clean function structure
function createUser(userData) {
    // Validation
    if (!userData.email) {
        throw new Error('Email is required');
    }
    
    // API call
    return fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .catch(error => console.error('Error:', error));
}

// ❌ INCORRECT - Mixed concerns
function createUserAndUpdateUI(userData) {
    // Don't mix API calls with DOM manipulation
    if (!userData.email) {
        document.getElementById('error').innerText = 'Email required';
        return;
    }
    // ... API call and DOM updates mixed together
}
```

### Event Handling
```javascript
// ✅ CORRECT - Clean event delegation
document.addEventListener('DOMContentLoaded', function() {
    // Form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Button clicks
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', handleButtonClick);
    });
});

function handleFormSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    // Handle form submission
}

function handleButtonClick(event) {
    const action = event.target.dataset.action;
    // Handle button action based on data attribute
}
```

## API Communication

### Fetch API Standards
```javascript
// ✅ CORRECT - Consistent API wrapper
class ApiClient {
    static async request(url, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    static async get(url) {
        return this.request(url);
    }
    
    static async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// Usage
ApiClient.post('/api/users', { name: 'John', email: 'john@example.com' })
    .then(user => console.log('User created:', user))
    .catch(error => showError(error.message));
```

### Error Handling
```javascript
// ✅ CORRECT - Centralized error handling
function showError(message) {
    const errorDiv = document.getElementById('error-messages');
    errorDiv.innerHTML = `<div class="alert alert--danger">${message}</div>`;
    errorDiv.style.display = 'block';
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-messages');
    successDiv.innerHTML = `<div class="alert alert--success">${message}</div>`;
    successDiv.style.display = 'block';
}

function clearMessages() {
    document.getElementById('error-messages').style.display = 'none';
    document.getElementById('success-messages').style.display = 'none';
}
```

## Modern JavaScript Features

### ES6+ Standards
```javascript
// ✅ Use modern JavaScript features
const users = await ApiClient.get('/api/users');
const activeUsers = users.filter(user => user.active);
const userNames = activeUsers.map(user => user.name);

// Destructuring
const { name, email, ...otherData } = userData;

// Template literals
const message = `Welcome ${name}! Your email ${email} has been verified.`;

// Arrow functions for simple operations
const isActive = user => user.active;
const getName = user => user.name;
```

### Module Pattern (Optional)
```javascript
// ✅ CORRECT - Simple module pattern for larger files
const UserModule = (function() {
    let users = [];
    
    function loadUsers() {
        return ApiClient.get('/api/users')
            .then(data => {
                users = data;
                renderUsers();
            });
    }
    
    function renderUsers() {
        const container = document.getElementById('users-list');
        container.innerHTML = users.map(user => 
            `<div class="user-card">${user.name}</div>`
        ).join('');
    }
    
    // Public API
    return {
        load: loadUsers,
        render: renderUsers
    };
})();
```

## Performance Guidelines

### Efficient DOM Manipulation
```javascript
// ✅ CORRECT - Batch DOM updates
function updateUserList(users) {
    const fragment = document.createDocumentFragment();
    
    users.forEach(user => {
        const div = document.createElement('div');
        div.className = 'user-item';
        div.textContent = user.name;
        fragment.appendChild(div);
    });
    
    document.getElementById('user-list').appendChild(fragment);
}

// ✅ CORRECT - Debounce user input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const searchUsers = debounce(function(query) {
    ApiClient.get(`/api/users/search?q=${query}`)
        .then(results => updateUserList(results));
}, 300);
```

## Code Style Rules

### Formatting Standards
- Use 2 spaces for indentation
- Use semicolons
- Use single quotes for strings
- Use camelCase for variables and functions
- Use PascalCase for constructors/classes
- Use UPPER_CASE for constants

### Variable Declarations
```javascript
// ✅ CORRECT
const API_BASE_URL = '/api';
let currentUser = null;
const userData = { name: 'John', email: 'john@example.com' };

// ❌ INCORRECT
var api_url = '/api';  // Use const, not var
let CurrentUser = null;  // Use camelCase
```

These instructions ensure all JavaScript follows constitutional principles of external files, clean organization, and maintainable code that supports the Flask MVC architecture.