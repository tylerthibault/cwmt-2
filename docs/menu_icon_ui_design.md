# User Management UI - Menu Icon Design

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  User Management                                   ┌───────┐         │
│  Manage user-related settings here                 │  👤+  │         │
│                                                     └───────┘         │
│                                                     Menu Icon         │
│                                                                       │
├─────────────────────────────────────────────────────────────────────┤
│  Filter by Role:                                                     │
│  ┌──────────┐ ┌─────────┐ ┌────────────┐ ┌────────────┐            │
│  │All Users │ │ Student │ │ Instructor │ │ Super User │            │
│  └──────────┘ └─────────┘ └────────────┘ └────────────┘            │
│     (active)                                                         │
└─────────────────────────────────────────────────────────────────────┘
```

## Menu Icon (Closed State)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  User Management                                   ╭───────╮         │
│  Viewing: Student Role                             │  👤+  │ ← Click │
│                                                     ╰───────╯         │
│                                                                       │
│  Circular button with:                                               │
│  - Blue background (#1976d2)                                         │
│  - White icon (fa-user-plus)                                         │
│  - 48px diameter                                                     │
│  - Hover: Slight scale + shadow                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Dropdown Menu (Open State)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  User Management                                   ╭───────╮         │
│  Viewing: Student Role                             │  👤+  │         │
│                                                     ╰───────╯         │
│                                                         │             │
│                                          ┌──────────────▼─────────┐  │
│                                          │ Add User to Student  ✕ │  │
│                                          ├────────────────────────┤  │
│                                          │                        │  │
│                                          │ ┌────────────────────┐ │  │
│                                          │ │ Select a user...  ▼│ │  │
│                                          │ └────────────────────┘ │  │
│                                          │                        │  │
│                                          │ ┌────────────────────┐ │  │
│                                          │ │   Add to Role      │ │  │
│                                          │ └────────────────────┘ │  │
│                                          │                        │  │
│                                          └────────────────────────┘  │
│                                                                       │
│  - White card with shadow                                            │
│  - Absolutely positioned below icon                                  │
│  - Right-aligned                                                     │
│  - Min-width: 350px                                                  │
│  - Rounded corners                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Dropdown Menu with Selection

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  User Management                                    ╭───────╮         │
│  Viewing: Student Role                              │  👤+  │         │
│                                                      ╰───────╯         │
│                                                          │             │
│                                           ┌──────────────▼─────────┐  │
│                                           │ Add User to Student  ✕ │  │
│                                           ├────────────────────────┤  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │ john_doe (john@...) │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │   Add to Role      │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │        (enabled)       │  │
│                                           └────────────────────────┘  │
│                                                                        │
│  Button becomes enabled when user is selected                         │
└──────────────────────────────────────────────────────────────────────┘
```

## Success State

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  User Management                                    ╭───────╮         │
│  Viewing: Student Role                              │  👤+  │         │
│                                                      ╰───────╯         │
│                                                          │             │
│                                           ┌──────────────▼─────────┐  │
│                                           │ Add User to Student  ✕ │  │
│                                           ├────────────────────────┤  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │ john_doe (john@...) │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │     Adding...      │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │      (disabled)        │  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │ ✓ User john_doe    │ │  │
│                                           │ │   added to role    │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │    (green message)     │  │
│                                           └────────────────────────┘  │
│                                                                        │
│  Page reloads in 1 second...                                          │
└──────────────────────────────────────────────────────────────────────┘
```

## Error State

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  User Management                                    ╭───────╮         │
│  Viewing: Student Role                              │  👤+  │         │
│                                                      ╰───────╯         │
│                                                          │             │
│                                           ┌──────────────▼─────────┐  │
│                                           │ Add User to Student  ✕ │  │
│                                           ├────────────────────────┤  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │ john_doe (john@...) │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │   Add to Role      │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │      (enabled)         │  │
│                                           │                        │  │
│                                           │ ┌────────────────────┐ │  │
│                                           │ │ ✕ Error: User      │ │  │
│                                           │ │   already has role │ │  │
│                                           │ └────────────────────┘ │  │
│                                           │    (red message)       │  │
│                                           └────────────────────────┘  │
│                                                                        │
│  User can try again or select different user                          │
└──────────────────────────────────────────────────────────────────────┘
```

## Mobile View (< 768px)

```
┌─────────────────────────────┐
│                             │
│  User Management            │
│  Manage user-related        │
│  settings here              │
│                             │
│                  ╭───────╮  │
│                  │  👤+  │  │
│                  ╰───────╯  │
│                      │       │
│      ┌───────────────▼────┐ │
│      │ Add User...      ✕ │ │
│      ├────────────────────┤ │
│      │                    │ │
│      │ ┌────────────────┐ │ │
│      │ │ Select user.. ▼│ │ │
│      │ └────────────────┘ │ │
│      │                    │ │
│      │ ┌────────────────┐ │ │
│      │ │  Add to Role   │ │ │
│      │ └────────────────┘ │ │
│      │                    │ │
│      └────────────────────┘ │
│                             │
│  - Narrower dropdown        │
│  - Adjusted positioning     │
│  - Full-width button        │
└─────────────────────────────┘
```

## Interaction States

### Menu Icon Button States
- **Default**: Blue circle, white icon
- **Hover**: Darker blue, slight scale (1.05), shadow
- **Active**: Scale down (0.95)
- **Focus**: Blue outline for accessibility

### Close Button States
- **Default**: Transparent background, gray icon
- **Hover**: Light gray background, darker icon
- **Active**: Slight scale

### Dropdown Menu States
- **Hidden**: `display: none`
- **Visible**: `display: block`, slide-in animation
- **Z-index**: 1000 (above other content)

### Click Outside Behavior
- Click anywhere outside the dropdown → Menu closes
- Click the menu icon when open → Menu closes
- Click X button → Menu closes
- Click inside dropdown → Menu stays open

## Color Scheme

```css
Menu Icon:
  Background: #1976d2 (primary blue)
  Hover: #1565c0 (darker blue)
  Icon: white

Dropdown:
  Background: white
  Border: #dee2e6 (light gray)
  Shadow: rgba(0, 0, 0, 0.15)

Header:
  Background: #f8f9fa (light gray)
  Text: #212529 (dark gray)

Close Button:
  Default: #6c757d (gray)
  Hover background: #e9ecef
  Hover text: #212529

Success Message:
  Background: #e8f5e9 (light green)
  Text: #2e7d32 (dark green)
  Border: #2e7d32

Error Message:
  Background: #ffebee (light red)
  Text: #c62828 (dark red)
  Border: #c62828
```

## Accessibility Features

- ✅ Proper ARIA labels on buttons
- ✅ Keyboard navigation support
- ✅ Focus indicators visible
- ✅ Close on Escape key (can be added)
- ✅ Screen reader friendly
- ✅ Semantic HTML structure
- ✅ Color contrast meets WCAG AA
