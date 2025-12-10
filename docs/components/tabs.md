# Tab Component Documentation

## Overview

The Tab Component provides enhanced tab functionality with state persistence, URL hash navigation, and event-driven architecture. It automatically remembers which tab was active when the page is refreshed and supports multiple tab containers on the same page.

## Features

- ✅ **State Persistence**: Remembers active tab on page refresh using localStorage
- ✅ **URL Hash Navigation**: Supports deep linking with URL fragments
- ✅ **Multiple Containers**: Handle multiple tab groups on the same page
- ✅ **Cross-tab Sync**: Active tab syncs across browser tabs
- ✅ **Bootstrap 5 Compatible**: Works seamlessly with Bootstrap tabs
- ✅ **Event-driven**: Custom callbacks and events for tab changes
- ✅ **Auto-initialization**: Works out of the box with minimal setup

## Quick Start

### 1. Include the JavaScript

Add the tab component script to your template:

```html
<script src="{{ url_for('static', filename='js/components/tabs.js') }}"></script>
```

### 2. Basic HTML Structure

```html
<!-- Tab Container with data-tab-container attribute -->
<div data-tab-container="user-profile">
    <!-- Tab Navigation -->
    <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item" role="presentation">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#profile" 
                    data-tab-id="profile" type="button" role="tab">
                Profile
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#settings" 
                    data-tab-id="settings" type="button" role="tab">
                Settings
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#security" 
                    data-tab-id="security" type="button" role="tab">
                Security
            </button>
        </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
        <div class="tab-pane fade show active" id="profile" role="tabpanel">
            <h4>Profile Information</h4>
            <p>Your profile content here...</p>
        </div>
        <div class="tab-pane fade" id="settings" role="tabpanel">
            <h4>Settings</h4>
            <p>Your settings content here...</p>
        </div>
        <div class="tab-pane fade" id="security" role="tabpanel">
            <h4>Security</h4>
            <p>Your security content here...</p>
        </div>
    </div>
</div>
```

### 3. Auto-initialization

The component auto-initializes on page load. No additional JavaScript required!

## Advanced Usage

### Multiple Tab Containers

You can have multiple independent tab groups on the same page:

```html
<!-- First tab container -->
<div data-tab-container="main-tabs">
    <ul class="nav nav-pills">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab1" 
                    data-tab-id="tab1">Tab 1</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab2" 
                    data-tab-id="tab2">Tab 2</button>
        </li>
    </ul>
    <div class="tab-content">
        <div class="tab-pane fade show active" id="tab1">Content 1</div>
        <div class="tab-pane fade" id="tab2">Content 2</div>
    </div>
</div>

<!-- Second tab container -->
<div data-tab-container="secondary-tabs">
    <ul class="nav nav-tabs">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tabA" 
                    data-tab-id="tabA">Tab A</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tabB" 
                    data-tab-id="tabB">Tab B</button>
        </li>
    </ul>
    <div class="tab-content">
        <div class="tab-pane fade show active" id="tabA">Content A</div>
        <div class="tab-pane fade" id="tabB">Content B</div>
    </div>
</div>
```

### Custom Initialization

For advanced control, you can create your own TabManager instance:

```javascript
// Custom tab manager with callbacks
const customTabManager = new TabManager({
    storageKey: 'myApp_tabs',
    useUrlHash: true,
    autoInit: false,
    onTabChange: function(tabId, button, containerId) {
        console.log(`Tab changed to ${tabId} in container ${containerId}`);
        
        // Custom logic when tab changes
        if (tabId === 'analytics') {
            loadAnalyticsData();
        }
    },
    onTabShow: function(tabId, button, containerId) {
        // Before tab is shown
        console.log(`About to show tab ${tabId}`);
    },
    onTabHide: function(tabId, button, containerId) {
        // When tab is hidden
        console.log(`Hiding tab ${tabId}`);
    }
});

// Initialize manually
customTabManager.init();
```

### Programmatic Tab Control

```javascript
// Show a specific tab
window.tabManager.showTab('settings');

// Get currently active tab
const activeTab = window.tabManager.getActiveTab('user-profile');

// Clear all saved tab states
window.tabManager.clearSavedStates();
```

## HTML Attributes

### Required Attributes

| Attribute | Element | Description |
|-----------|---------|-------------|
| `data-tab-container` | Container | Identifies a tab container group |
| `data-bs-toggle` | Button | Bootstrap tab toggle (use "tab" or "pill") |
| `data-bs-target` | Button | Target tab pane selector |

### Optional Attributes

| Attribute | Element | Description |
|-----------|---------|-------------|
| `data-tab-id` | Button | Custom tab identifier (fallback: target or href) |
| `id` | Container | Alternative container identifier |

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `storageKey` | String | 'activeTab' | localStorage key prefix |
| `useUrlHash` | Boolean | true | Enable URL hash navigation |
| `autoInit` | Boolean | true | Auto-initialize on instantiation |
| `onTabChange` | Function | null | Callback when tab changes |
| `onTabShow` | Function | null | Callback before tab shows |
| `onTabHide` | Function | null | Callback when tab hides |

## Events

The component dispatches custom events you can listen for:

```javascript
// Listen for tab changes
document.addEventListener('tabChanged', function(event) {
    const { tabId, containerId, button } = event.detail;
    console.log(`Tab ${tabId} activated in ${containerId}`);
});
```

## API Methods

### TabManager Instance Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `init()` | - | Initialize the tab manager |
| `showTab(tabId)` | tabId: String | Show specific tab |
| `getActiveTab(containerId)` | containerId?: String | Get active tab ID |
| `clearSavedStates()` | - | Clear all localStorage states |
| `destroy()` | - | Cleanup and remove listeners |

## Integration Examples

### User Management Example

Based on the superuser management page:

```html
<div data-tab-container="user-management">
    <div class="card-header">
        <ul class="nav nav-pills" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#all-users" 
                        data-tab-id="all" type="button" role="tab">
                    All Users <span class="badge bg-light text-dark ms-1">{{ users|length }}</span>
                </button>
            </li>
            {% for role in roles %}
            <li class="nav-item" role="presentation">
                <button class="nav-link" data-bs-toggle="pill" data-bs-target="#{{ role.name }}-users" 
                        data-tab-id="{{ role.name }}" type="button" role="tab">
                    {{ role.name|title }} <span class="badge bg-light text-dark ms-1">0</span>
                </button>
            </li>
            {% endfor %}
        </ul>
    </div>
</div>

<script>
// Custom logic for user management tabs
document.addEventListener('tabChanged', function(event) {
    const { tabId } = event.detail;
    
    if (event.detail.containerId === 'user-management') {
        // Update user list based on role filter
        filterUsersByRole(tabId);
        
        // Update add button text
        updateAddButtonText(tabId);
    }
});
</script>
```

### Dashboard Example

```html
<div data-tab-container="dashboard">
    <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#overview" 
                    data-tab-id="overview">Overview</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#analytics" 
                    data-tab-id="analytics">Analytics</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#reports" 
                    data-tab-id="reports">Reports</button>
        </li>
    </ul>

    <div class="tab-content">
        <div class="tab-pane fade show active" id="overview">
            <!-- Overview content -->
        </div>
        <div class="tab-pane fade" id="analytics">
            <!-- Analytics content -->
        </div>
        <div class="tab-pane fade" id="reports">
            <!-- Reports content -->
        </div>
    </div>
</div>
```

## Best Practices

### 1. Use Descriptive Tab IDs

```html
<!-- Good -->
<button data-tab-id="user-profile">Profile</button>
<button data-tab-id="account-settings">Settings</button>

<!-- Avoid -->
<button data-tab-id="tab1">Profile</button>
<button data-tab-id="tab2">Settings</button>
```

### 2. Container Naming

```html
<!-- Good: Descriptive container names -->
<div data-tab-container="user-management">
<div data-tab-container="dashboard-tabs">
<div data-tab-container="settings-panel">

<!-- Avoid: Generic names -->
<div data-tab-container="tabs1">
<div data-tab-container="container">
```

### 3. Lazy Loading Content

```javascript
document.addEventListener('tabChanged', function(event) {
    const { tabId } = event.detail;
    
    // Load content only when tab is activated
    if (tabId === 'analytics' && !analyticsLoaded) {
        loadAnalyticsData();
        analyticsLoaded = true;
    }
});
```

### 4. URL-Friendly Tab IDs

Use URL-safe characters in tab IDs for hash navigation:

```html
<!-- Good -->
<button data-tab-id="user-settings">Settings</button>
<button data-tab-id="billing-info">Billing</button>

<!-- Avoid spaces and special characters -->
<button data-tab-id="user settings">Settings</button>
<button data-tab-id="billing & payment">Billing</button>
```

## Troubleshooting

### Tab State Not Persisting

1. Check if `data-tab-container` attribute is present
2. Verify `data-tab-id` attributes are unique within the container
3. Ensure localStorage is enabled in the browser

### URL Hash Not Working

1. Confirm `useUrlHash: true` in configuration
2. Check that tab IDs are URL-safe (no spaces or special characters)
3. Verify the hash matches an existing tab ID

### Multiple Containers Conflicting

1. Ensure each container has a unique `data-tab-container` value
2. Check that tab IDs within each container are unique
3. Verify the container identification logic

### Events Not Firing

1. Make sure the component is loaded before adding event listeners
2. Check that Bootstrap 5 is properly loaded
3. Verify tab elements have correct Bootstrap attributes

## Browser Support

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

## Dependencies

- Bootstrap 5.x (required for tab functionality)
- Modern browser with localStorage support