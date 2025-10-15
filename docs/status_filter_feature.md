# Status Filter Feature - Active/Inactive Users

## Overview
Added a status filter to the User Management page that allows filtering users by their active/inactive status. By default, only active users are shown.

## Implementation Details

### Controller Changes (`super_user_controller.py`)

#### New Query Parameter
- **`status`**: Filter parameter for user status
  - `'active'` - Shows only active users (default)
  - `'inactive'` - Shows only inactive users
  - `'all'` - Shows both active and inactive users

#### Filtering Logic
```python
# Get status filter from query parameters (default: 'active')
status_filter = request.args.get('status', 'active')

# Apply status filter after role filter
if status_filter == 'active':
    all_users = [u for u in all_users if u.is_active]
    users_not_in_role = [u for u in users_not_in_role if u.is_active]
elif status_filter == 'inactive':
    all_users = [u for u in all_users if not u.is_active]
    users_not_in_role = [u for u in users_not_in_role if not u.is_active]
# 'all' status shows both active and inactive
```

### Template Changes (`index.html`)

#### Status Filter Buttons
Added a new filter section below the role filter:

```html
<div class="filter-container">
    <h3>Filter by Status:</h3>
    <div class="filter-buttons">
        <a href="...?status=active">Active Users</a>
        <a href="...?status=inactive">Inactive Users</a>
        <a href="...?status=all">All</a>
    </div>
</div>
```

#### Status Column in Table
Added a "Status" column showing active/inactive badges:

```html
<th>Status</th>
...
<td>
    {% if user.is_active %}
    <span class="badge badge--success">Active</span>
    {% else %}
    <span class="badge badge--secondary">Inactive</span>
    {% endif %}
</td>
```

#### Updated Filter URLs
All filter buttons now preserve both role and status filters:

```html
<!-- Role filters preserve status -->
<a href="{{ url_for('super_user.user_management', role=role.name, status=current_status_filter) }}">

<!-- Status filters preserve role -->
<a href="{{ url_for('super_user.user_management', role=current_role_filter, status='active') }}">
```

## User Experience

### Default Behavior
- Page loads showing **only active users**
- "Active Users" filter button is highlighted
- Inactive users are hidden by default

### Filter Combinations
Users can combine role and status filters:

| Role Filter | Status Filter | Result |
|-------------|---------------|--------|
| All Users | Active | All active users across all roles |
| All Users | Inactive | All inactive users across all roles |
| All Users | All | All users (active + inactive) |
| Student | Active | Active students only |
| Student | Inactive | Inactive students only |
| Student | All | All students (active + inactive) |
| Instructor | Active | Active instructors only |

### Visual Indicators

**Status Badges:**
- **Active**: Green badge with "Active" text
- **Inactive**: Gray badge with "Inactive" text

**Filter Buttons:**
- Active filter button has blue background
- Inactive buttons have white background with border

## URL Examples

```
# Default: Active users only
/super/user-management

# Explicit active users
/super/user-management?status=active

# Inactive users
/super/user-management?status=inactive

# All users (active + inactive)
/super/user-management?status=all

# Active students
/super/user-management?role=student&status=active

# Inactive instructors
/super/user-management?role=instructor&status=inactive

# All super-users (active + inactive)
/super/user-management?role=super-user&status=all
```

## Database Schema

Uses existing `is_active` field from User model:

```python
class User(BaseModel):
    is_active = db.Column(db.Boolean, default=True, nullable=False)
```

## Benefits

### User Management
✅ **Cleaner Default View**: Only shows active users by default
✅ **Easy Access to Inactive**: One click to see inactive users
✅ **Complete View Available**: Can view all users when needed
✅ **Visual Status**: Clear badges show user status at a glance

### Performance
✅ **Client-Side Filtering**: Fast filtering using list comprehensions
✅ **No Additional Queries**: Uses existing user data
✅ **Efficient**: Filters applied after role filtering

### Security
✅ **Prevents Accidents**: Inactive users hidden by default reduces mistakes
✅ **Clear Status**: Visual indicators prevent confusion
✅ **Audit Trail**: Can review inactive users when needed

## Testing Scenarios

### Basic Filtering
- [ ] Default view shows only active users
- [ ] Click "Inactive Users" shows only inactive users
- [ ] Click "All" shows both active and inactive users
- [ ] Status badges display correctly

### Combined Filters
- [ ] Role + Status filters work together
- [ ] Switching role filter preserves status filter
- [ ] Switching status filter preserves role filter
- [ ] URLs update correctly with both parameters

### Edge Cases
- [ ] No active users in a role (empty table)
- [ ] No inactive users in a role (empty table)
- [ ] All users are active (inactive filter shows nothing)
- [ ] All users are inactive (active filter shows nothing)

### Add User Feature
- [ ] Menu icon still appears when filtering
- [ ] Dropdown only shows users matching status filter
- [ ] Adding user works with status filters active
- [ ] Page refreshes preserving both filters

## Future Enhancements

Potential improvements:

1. **Toggle Active/Inactive**: Quick action buttons in table to toggle status
2. **Bulk Operations**: Select multiple users to activate/deactivate
3. **Filter Counts**: Show count of users in each filter
4. **Last Active Date**: Show when user was last active
5. **Reason for Deactivation**: Track why users were deactivated
6. **Reactivation Workflow**: Special process to reactivate users

## Migration Notes

### No Breaking Changes
- Existing functionality unchanged
- New parameter is optional (defaults to 'active')
- All existing routes work without modification

### Backward Compatibility
- Old URLs without `status` parameter default to active users
- Existing bookmarks continue to work
- No database changes required

### Frontend Only
- No backend logic changes beyond filtering
- No new database queries
- Uses existing `is_active` field

## Code Changes Summary

**Controller:**
- Added `status_filter` parameter handling
- Added status filtering logic after role filtering
- Added `current_status_filter` to context

**Template:**
- Added status filter button section
- Added status column to table
- Added status badges (Active/Inactive)
- Updated all filter URLs to preserve both filters

**Lines Changed:**
- Controller: ~10 lines added
- Template: ~25 lines added
- Total: ~35 lines

## Related Documentation

- `table_component.md` - Badge components used for status
- `user_role_management_feature.md` - Main feature documentation
- User Model documentation - `is_active` field details
