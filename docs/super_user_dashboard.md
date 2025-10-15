# Super User Dashboard

## Overview

The Super User Dashboard provides comprehensive system administration capabilities for users with the `super-user` role. This dashboard serves as the central control panel for managing the entire CWMT application.

## Features

### 1. System Overview Statistics

The dashboard displays real-time system metrics:

- **Total Users**: Count of all registered users in the system
- **Active Users**: Number of currently active users
- **Total Roles**: Count of all defined system roles
- **System Health**: Current health status of the application
- **Pending Actions**: Number of items requiring administrator attention

### 2. User Management

Comprehensive user administration capabilities:

- **View All Users**: Browse and search all registered users
- **Create New User**: Add new users to the system
- **Manage Permissions**: Configure user-specific permissions and access levels

### 3. Role Management

Complete role-based access control (RBAC) management:

- **View All Roles**: See all system roles and their configurations
- **Create New Role**: Define new roles with specific permissions
- **Edit Role Permissions**: Modify existing role permissions and access levels

### 4. System Settings

Global application configuration:

- **Global Settings**: Configure system-wide preferences
- **Database Management**: Database maintenance and optimization tools
- **Email Configuration**: Set up and manage email service settings

### 5. System Monitoring

Real-time activity tracking and monitoring:

- **System Activity Chart**: Visual representation of system activity over time
- **Recent System Logs**: Latest log entries with severity levels
- **Recent User Activity**: Detailed log of user actions and events

### 6. Advanced System Tools

Critical system administration tools (use with caution):

- **Clear Cache**: Remove all cached data
- **Backup Database**: Create database backups
- **System Migration**: Run database migrations
- **Generate Reports**: Create system reports

## File Structure

```
src/
├── templates/
│   └── private/
│       └── dashboard/
│           └── super_user/
│               └── index.html              # Super-user dashboard template
├── static/
│   ├── css/
│   │   └── private/
│   │       └── super_user_dashboard.css   # Dashboard-specific styles
│   └── js/
│       └── private/
│           └── super_user_dashboard.js    # Dashboard interactivity
└── logic/
    └── user_logic.py                      # Context building logic
```

## Technical Implementation

### Backend (Python)

The super-user dashboard context is built in `src/logic/user_logic.py`:

```python
@staticmethod
def _build_superuser_context(user, current_role):
    """Build context for super-user dashboard"""
    # Gathers statistics from database
    # Retrieves recent activity logs
    # Formats data for template rendering
    # Returns comprehensive context dictionary
```

**Data Provided:**
- User and role statistics
- Recent user activity from logbook
- System logs
- Last update timestamps

### Frontend (HTML/CSS/JS)

**Template**: `src/templates/private/dashboard/super_user/index.html`
- Extends `bases/private.html`
- Uses Bootstrap 5 components
- Implements responsive grid layout
- Includes modal dialogs for confirmations

**Styling**: `src/static/css/private/super_user_dashboard.css`
- Component-based CSS architecture
- Follows BEM methodology
- Responsive design patterns
- Dark mode support

**Interactivity**: `src/static/js/private/super_user_dashboard.js`
- Dashboard refresh functionality
- Chart rendering (Chart.js)
- Modal interactions
- Cache clearing operations

## Access Control

The super-user dashboard is protected by:

1. **Authentication**: User must be logged in (`@login_required` decorator)
2. **Authorization**: User must have `super-user` role assigned
3. **Session Validation**: Active session token required

## Dashboard Components

### Stat Cards

Four primary metric cards displaying:
- Color-coded visual indicators
- Large numeric values
- Contextual icons
- Hover animations

### Management Cards

Three main management sections:
- User Management (blue theme)
- Role Management (green theme)
- System Settings (cyan theme)

Each card includes:
- Quick action buttons
- Last update timestamp
- Contextual footer information

### Activity Chart

Line chart showing:
- User login trends
- System event frequency
- Configurable time range (default: 7 days)

### System Logs

Scrollable log viewer with:
- Severity level badges (INFO, WARNING, ERROR)
- Timestamp display
- Message content
- Export functionality

### User Activity Table

Comprehensive activity log showing:
- Timestamp
- User information (username, email)
- Action performed
- Action details
- IP address
- Status indicator

### Advanced Tools Section

Red-themed warning section with:
- Cache clearing
- Database backup
- Migration tools
- Report generation

## Dependencies

### Required Libraries

- **Bootstrap 5**: UI framework
- **Font Awesome 6**: Icon library
- **Chart.js** (optional): For activity charts

### Backend Dependencies

- Flask
- SQLAlchemy
- User and Role models
- Logbook model for activity tracking

## Usage

### Accessing the Dashboard

1. Log in with a user account that has the `super-user` role
2. Navigate to `/user/dashboard`
3. The system automatically routes super-users to the super-user dashboard

### Refreshing Statistics

Click the "Refresh" button in the top-right corner to reload current statistics without refreshing the entire page.

### Clearing Cache

1. Click "Clear Cache" in the Advanced Tools section
2. Confirm the action in the modal dialog
3. Wait for the operation to complete

## Customization

### Adding New Statistics

1. Modify `_build_superuser_context()` in `src/logic/user_logic.py`
2. Add new data queries and transformations
3. Update the template to display new statistics

### Adding New Features

1. Add new card sections to the template
2. Create corresponding routes and logic
3. Update CSS for new component styling
4. Add JavaScript for interactivity if needed

### Modifying Chart Display

Edit `initActivityChart()` in `super_user_dashboard.js`:
- Change chart type
- Modify data sources
- Adjust styling and colors
- Add new datasets

## Security Considerations

### Protected Actions

All destructive actions (cache clearing, database operations) should:
- Require confirmation dialogs
- Log the action and user
- Implement CSRF protection
- Validate user permissions server-side

### Data Privacy

- User activity logs should respect privacy policies
- Sensitive information should be masked or excluded
- IP addresses should be stored securely
- Access to logs should be audited

## Future Enhancements

Potential features for future development:

1. **Real-time Updates**: WebSocket integration for live statistics
2. **Advanced Filtering**: Filter users and activity by various criteria
3. **Bulk Operations**: Batch user management operations
4. **Export Functionality**: Export data to CSV/PDF
5. **System Alerts**: Configurable alerts for system events
6. **Audit Trail**: Comprehensive audit logging for all admin actions
7. **Custom Dashboards**: Configurable dashboard layouts
8. **API Documentation**: Built-in API documentation viewer

## Troubleshooting

### Dashboard Not Loading

- Verify user has `super-user` role assigned
- Check browser console for JavaScript errors
- Ensure all CSS/JS files are loading correctly
- Verify database connection

### Statistics Not Updating

- Check database connectivity
- Verify query permissions
- Review application logs for errors
- Ensure models are properly imported

### Charts Not Displaying

- Verify Chart.js library is loaded
- Check browser console for errors
- Ensure canvas element exists
- Validate data format

## Support

For issues or questions related to the super-user dashboard:

1. Check application logs in `logs/` directory
2. Review recent commits for breaking changes
3. Consult the main project documentation
4. Contact the development team

## Version History

- **v1.0.0** - Initial super-user dashboard implementation
  - Basic statistics display
  - User and role management sections
  - Activity monitoring
  - Advanced tools section
