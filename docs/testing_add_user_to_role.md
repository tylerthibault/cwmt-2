# Testing Guide: Add User to Role Feature

## Prerequisites
1. Database with users and roles seeded
2. At least one super-user account
3. Multiple users with varying role assignments
4. Multiple roles created (student, instructor, super-user, etc.)

## Test Scenarios

### 1. Successful User Addition
**Steps:**
1. Log in as super-user
2. Navigate to User Management
3. Click on a role filter (e.g., "Student")
4. Verify "Add User to Student Role" section appears
5. Open dropdown - verify it shows users NOT in student role
6. Select a user from dropdown
7. Verify "Add to Role" button becomes enabled
8. Click "Add to Role" button
9. Verify button shows "Adding..."
10. Verify success message appears (green)
11. Verify page reloads after ~1 second
12. Verify user now appears in the filtered table

**Expected Result:** ✅ User successfully added to role

---

### 2. All Users Already in Role
**Steps:**
1. Navigate to a role where all users are already members
2. Verify info message appears: "All users are already in the [Role] role"
3. Verify no dropdown appears

**Expected Result:** ✅ Appropriate message shown, no dropdown

---

### 3. Attempt to Add User Already in Role
**Setup:** Manually call the endpoint with a user already in the role

**Expected Result:** ✅ Error response: "User already has this role" (400)

---

### 4. Invalid User ID
**Setup:** Manually call endpoint with non-existent user_id

**Expected Result:** ✅ Error response: "User not found" (404)

---

### 5. Invalid Role Name
**Setup:** Manually call endpoint with non-existent role_name

**Expected Result:** ✅ Error response: "Role not found" (404)

---

### 6. Missing Parameters
**Setup:** Call endpoint without user_id or role_name

**Expected Result:** ✅ Error response: "Missing user_id or role_name" (400)

---

### 7. View All Users (No Filter)
**Steps:**
1. Click "All Users" filter
2. Verify no "Add User" section appears
3. Verify all users shown in table

**Expected Result:** ✅ No add user section when viewing all users

---

### 8. Dropdown Selection and Deselection
**Steps:**
1. Filter by a role
2. Open dropdown, select a user
3. Verify button becomes enabled
4. Select the first option ("Select a user to add...")
5. Verify button becomes disabled again

**Expected Result:** ✅ Button state responds to selection

---

### 9. Network Error Handling
**Setup:** Disconnect network or modify endpoint URL

**Expected Result:** ✅ Error message shown, button re-enabled

---

### 10. Mobile Responsive Layout
**Steps:**
1. Open page on mobile device or resize browser to <768px
2. Filter by a role
3. Verify dropdown and button stack vertically
4. Verify dropdown is full width
5. Test full flow on mobile

**Expected Result:** ✅ Layout adapts properly, functionality works

---

## Manual API Testing

### Using curl or Postman

**Successful Request:**
```bash
curl -X POST http://localhost:5000/super/user-management/add-to-role \
  -H "Content-Type: application/json" \
  -d '{"user_id": 5, "role_name": "student"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "User username added to role student"
}
```

**Error Request (User Already Has Role):**
```bash
curl -X POST http://localhost:5000/super/user-management/add-to-role \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "role_name": "super-user"}'
```

**Expected Response:**
```json
{
  "success": false,
  "error": "User already has this role"
}
```

---

## Database Verification

After adding a user to a role, verify in database:

```sql
-- Check user_has_roles table
SELECT * FROM user_has_roles 
WHERE user_id = [user_id] AND role_id = [role_id];

-- Should show new record with assigned_at timestamp
```

---

## Browser Console Testing

Open browser console and check for:
- ✅ No JavaScript errors
- ✅ Successful fetch request (200 status)
- ✅ Correct request payload
- ✅ Proper response handling

---

## Accessibility Testing

1. Tab through interface - verify logical order
2. Use only keyboard to:
   - Navigate to dropdown
   - Select user
   - Activate button
3. Verify focus indicators visible
4. Test with screen reader

---

## Performance Testing

1. Add user with large dropdown (100+ users)
2. Verify page loads quickly
3. Verify dropdown renders smoothly
4. Verify AJAX request completes quickly (<500ms)

---

## Cross-Browser Testing

Test in:
- ✅ Chrome
- ✅ Firefox  
- ✅ Safari
- ✅ Edge

---

## Common Issues to Watch For

1. **CSRF Token**: Ensure AJAX requests don't require CSRF token or it's properly included
2. **Session**: Verify super-user session maintained during AJAX call
3. **Race Conditions**: Rapid clicking shouldn't cause duplicate assignments
4. **Reload Timing**: 1 second delay should be enough to see success message
5. **Dropdown Population**: Verify correct users excluded (those already in role)

---

## Checklist for QA Sign-off

- [ ] Can add user to role successfully
- [ ] Success message displays correctly
- [ ] Page reloads and shows updated table
- [ ] Error messages display for all error cases
- [ ] Dropdown only shows users not in role
- [ ] "All users in role" message works
- [ ] Button enable/disable works correctly
- [ ] Mobile layout works properly
- [ ] No JavaScript console errors
- [ ] Database records created correctly
- [ ] Works across all major browsers
- [ ] Accessible via keyboard navigation
- [ ] Error recovery works (can retry after error)
