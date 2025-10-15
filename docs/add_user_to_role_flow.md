# Add User to Role - Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Management Page                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Role Filter Buttons: [All Users] [Student] [Instructor] etc.   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    User clicks "Student"
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Page Reloads with ?role=student                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Controller    │
                    │                 │
                    │  1. Get role    │
                    │  2. Get users   │
                    │     in role     │
                    │  3. Calculate   │
                    │     users NOT   │
                    │     in role     │
                    └─────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
         Has users                      All users
         not in role?                   in role?
              │                               │
              ▼                               ▼
┌──────────────────────────────┐  ┌─────────────────────────────┐
│  Show Add User Section       │  │  Show Info Message          │
│                              │  │  "All users already in      │
│  ┌────────────────────────┐ │  │   this role"                │
│  │ Select User Dropdown   │ │  └─────────────────────────────┘
│  │ ▼ John Doe (john@...)  │ │
│  │   Jane Smith (jane@...)│ │
│  └────────────────────────┘ │
│  [Add to Role] (disabled)   │
└──────────────────────────────┘
              │
     User selects from dropdown
              │
              ▼
┌──────────────────────────────┐
│  [Add to Role] (enabled)     │
└──────────────────────────────┘
              │
     User clicks "Add to Role"
              │
              ▼
┌──────────────────────────────┐
│  JavaScript Event Handler    │
│                              │
│  1. Disable button           │
│  2. Show "Adding..."         │
│  3. Send AJAX POST           │
└──────────────────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  POST /add-to-role           │
│                              │
│  Body: {                     │
│    user_id: 5,               │
│    role_name: "student"      │
│  }                           │
└──────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Controller                            │
│                                                                  │
│  1. Validate user_id and role_name ──────┐                      │
│  2. Get Role by name ─────────────────┐  │                      │
│  3. Get User by ID ────────────────┐  │  │                      │
│  4. Check if already has role ──┐  │  │  │                      │
│  5. Call UserHasRoles.assign_role() │  │  │                     │
│     (user_id, role_id)           │  │  │  │                     │
│                                  │  │  │  │                     │
│     ┌────────────────────────────┘  │  │  │                     │
│     │ Already has role? Return 400  │  │  │                     │
│     │                               │  │  │                     │
│     └───┐                           │  │  │                     │
│         │ User not found? Return 404 │  │  │                    │
│         │                           │  │  │                     │
│         └───┐                       │  │  │                     │
│             │ Role not found? 404   │  │  │                     │
│             │                       │  │  │                     │
│             └───┐                   │  │  │                     │
│                 │ Missing params? 400│  │                       │
│                 │                   │  │                        │
│                 └───┐               │  │                        │
│                     │ Success!      │  │                        │
└─────────────────────┼───────────────┴──┴────────────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │   Database      │
            │                 │
            │ INSERT INTO     │
            │ user_has_roles  │
            │ (user_id,       │
            │  role_id)       │
            └─────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │  JSON Response  │
            │                 │
            │ {"success": true,│
            │  "message": "..." │
            │ }               │
            └─────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │  JavaScript     │
            │                 │
            │  1. Show success│
            │     message     │
            │  2. Wait 1 sec  │
            │  3. Reload page │
            └─────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │  User now       │
            │  appears in     │
            │  filtered table │
            │  for that role  │
            └─────────────────┘
```

## Error Flow

```
┌─────────────────────────────────────┐
│  Any error occurs                   │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  JSON Response                      │
│  {"success": false,                 │
│   "error": "Error message"}         │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  JavaScript                         │
│  1. Show error message (red)        │
│  2. Re-enable button                │
│  3. Change text back to             │
│     "Add to Role"                   │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  User can try again or              │
│  select different user              │
└─────────────────────────────────────┘
```
