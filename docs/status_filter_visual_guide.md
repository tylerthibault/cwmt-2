# Status Filter Visual Guide

## Default View (Active Users Only)

```
┌─────────────────────────────────────────────────────────────────┐
│ User Management                                      [👤+]       │
│ Manage user-related settings and configurations here            │
├─────────────────────────────────────────────────────────────────┤
│ Filter by Role:                                                 │
│ ┌────────────┐ ┌─────────┐ ┌────────────┐ ┌────────────┐      │
│ │ All Users  │ │ Student │ │ Instructor │ │ Super User │      │
│ └────────────┘ └─────────┘ └────────────┘ └────────────┘      │
│    (active)                                                     │
│                                                                 │
│ Filter by Status:                                               │
│ ┌──────────────┐ ┌────────────────┐ ┌─────┐                   │
│ │ Active Users │ │ Inactive Users │ │ All │                   │
│ └──────────────┘ └────────────────┘ └─────┘                   │
│    (active)                                                     │
├─────────────────────────────────────────────────────────────────┤
│ ID │ Username  │ Email           │ Status  │ Actions           │
├────┼───────────┼─────────────────┼─────────┼───────────────────┤
│ 1  │ john_doe  │ john@email.com  │ Active  │ [Remove][Deact]  │
│ 2  │ jane_smith│ jane@email.com  │ Active  │ [Remove][Deact]  │
│ 3  │ bob_jones │ bob@email.com   │ Active  │ [Remove][Deact]  │
└─────────────────────────────────────────────────────────────────┘

Note: Only active users shown (is_active = True)
```

## Inactive Users View

```
┌─────────────────────────────────────────────────────────────────┐
│ User Management                                      [👤+]       │
│ Manage user-related settings and configurations here            │
├─────────────────────────────────────────────────────────────────┤
│ Filter by Role:                                                 │
│ ┌────────────┐ ┌─────────┐ ┌────────────┐ ┌────────────┐      │
│ │ All Users  │ │ Student │ │ Instructor │ │ Super User │      │
│ └────────────┘ └─────────┘ └────────────┘ └────────────┘      │
│    (active)                                                     │
│                                                                 │
│ Filter by Status:                                               │
│ ┌──────────────┐ ┌────────────────┐ ┌─────┐                   │
│ │ Active Users │ │ Inactive Users │ │ All │                   │
│ └──────────────┘ └────────────────┘ └─────┘                   │
│                      (active)                                   │
├─────────────────────────────────────────────────────────────────┤
│ ID │ Username   │ Email            │ Status    │ Actions        │
├────┼────────────┼──────────────────┼───────────┼────────────────┤
│ 7  │ old_user   │ old@email.com    │ Inactive  │ [Reactivate]  │
│ 12 │ deleted_usr│ deleted@mail.com │ Inactive  │ [Reactivate]  │
└─────────────────────────────────────────────────────────────────┘

Note: Only inactive users shown (is_active = False)
```

## All Users View

```
┌─────────────────────────────────────────────────────────────────┐
│ User Management                                      [👤+]       │
│ Manage user-related settings and configurations here            │
├─────────────────────────────────────────────────────────────────┤
│ Filter by Role:                                                 │
│ ┌────────────┐ ┌─────────┐ ┌────────────┐ ┌────────────┐      │
│ │ All Users  │ │ Student │ │ Instructor │ │ Super User │      │
│ └────────────┘ └─────────┘ └────────────┘ └────────────┘      │
│    (active)                                                     │
│                                                                 │
│ Filter by Status:                                               │
│ ┌──────────────┐ ┌────────────────┐ ┌─────┐                   │
│ │ Active Users │ │ Inactive Users │ │ All │                   │
│ └──────────────┘ └────────────────┘ └─────┘                   │
│                                        (active)                 │
├─────────────────────────────────────────────────────────────────┤
│ ID │ Username  │ Email           │ Status    │ Actions          │
├────┼───────────┼─────────────────┼───────────┼──────────────────┤
│ 1  │ john_doe  │ john@email.com  │ Active    │ [Remove][Deact] │
│ 2  │ jane_smith│ jane@email.com  │ Active    │ [Remove][Deact] │
│ 7  │ old_user  │ old@email.com   │ Inactive  │ [Reactivate]    │
│ 3  │ bob_jones │ bob@email.com   │ Active    │ [Remove][Deact] │
│ 12 │ deleted_u │ deleted@m.com   │ Inactive  │ [Reactivate]    │
└─────────────────────────────────────────────────────────────────┘

Note: Both active and inactive users shown
```

## Combined Filters (Role + Status)

### Active Students Only

```
┌─────────────────────────────────────────────────────────────────┐
│ User Management                                      [👤+]       │
├─────────────────────────────────────────────────────────────────┤
│ Filter by Role:                                                 │
│ ┌────────────┐ ┌─────────┐ ┌────────────┐ ┌────────────┐      │
│ │ All Users  │ │ Student │ │ Instructor │ │ Super User │      │
│ └────────────┘ └─────────┘ └────────────┘ └────────────┘      │
│                  (active)                                       │
│                                                                 │
│ Filter by Status:                                               │
│ ┌──────────────┐ ┌────────────────┐ ┌─────┐                   │
│ │ Active Users │ │ Inactive Users │ │ All │                   │
│ └──────────────┘ └────────────────┘ └─────┘                   │
│    (active)                                                     │
├─────────────────────────────────────────────────────────────────┤
│ ID │ Username  │ Email           │ Status  │ Actions           │
├────┼───────────┼─────────────────┼─────────┼───────────────────┤
│ 5  │ alice_w   │ alice@email.com │ Active  │ [Remove][Deact]  │
│ 8  │ charlie_b │ charl@email.com │ Active  │ [Remove][Deact]  │
│ 15 │ emma_s    │ emma@email.com  │ Active  │ [Remove][Deact]  │
└─────────────────────────────────────────────────────────────────┘

Showing: Active users with Student role
URL: /super/user-management?role=student&status=active
```

### Inactive Instructors Only

```
┌─────────────────────────────────────────────────────────────────┐
│ User Management                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Filter by Role:                                                 │
│ ┌────────────┐ ┌─────────┐ ┌────────────┐ ┌────────────┐      │
│ │ All Users  │ │ Student │ │ Instructor │ │ Super User │      │
│ └────────────┘ └─────────┘ └────────────┘ └────────────┘      │
│                               (active)                          │
│                                                                 │
│ Filter by Status:                                               │
│ ┌──────────────┐ ┌────────────────┐ ┌─────┐                   │
│ │ Active Users │ │ Inactive Users │ │ All │                   │
│ └──────────────┘ └────────────────┘ └─────┘                   │
│                      (active)                                   │
├─────────────────────────────────────────────────────────────────┤
│ ID │ Username    │ Email            │ Status    │ Actions       │
├────┼─────────────┼──────────────────┼───────────┼───────────────┤
│ 23 │ former_prof │ prof@email.com   │ Inactive  │ [Reactivate] │
│ 31 │ retired_dr  │ dr@email.com     │ Inactive  │ [Reactivate] │
└─────────────────────────────────────────────────────────────────┘

Showing: Inactive users with Instructor role
URL: /super/user-management?role=instructor&status=inactive
```

## Status Badge Colors

```css
┌─────────────────────────────────────┐
│ Active Badge                        │
│ ┌─────────┐                         │
│ │ Active  │  ← Green (#e8f5e9)      │
│ └─────────┘    Text: #2e7d32        │
│                                     │
│ .badge--success                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Inactive Badge                      │
│ ┌──────────┐                        │
│ │ Inactive │  ← Gray (#f5f5f5)      │
│ └──────────┘    Text: #616161       │
│                                     │
│ .badge--secondary                   │
└─────────────────────────────────────┘
```

## Filter Button States

```css
┌─────────────────────────────────────┐
│ Active Filter Button                │
│ ┌──────────────┐                    │
│ │ Active Users │  ← Blue (#1976d2)  │
│ └──────────────┘    Text: White     │
│                                     │
│ .filter-btn--active                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Inactive Filter Button              │
│ ┌────────────────┐                  │
│ │ Inactive Users │  ← White         │
│ └────────────────┘    Border: Gray  │
│                       Text: Gray    │
│ .filter-btn                         │
└─────────────────────────────────────┘
```

## User Interaction Flow

```
┌──────────────────────┐
│ Page Loads           │
│ Default: Active Only │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐         ┌──────────────────────┐
│ Shows Active Users   │◄────────┤ Click "Active Users" │
│ (status=active)      │         └──────────────────────┘
└──────────┬───────────┘
           │
           │ Click "Inactive Users"
           ▼
┌──────────────────────┐         ┌──────────────────────┐
│ Shows Inactive Users │◄────────┤Click "Inactive Users"│
│ (status=inactive)    │         └──────────────────────┘
└──────────┬───────────┘
           │
           │ Click "All"
           ▼
┌──────────────────────┐         ┌──────────────────────┐
│ Shows All Users      │◄────────┤ Click "All"          │
│ (status=all)         │         └──────────────────────┘
└──────────────────────┘

Note: Role filter preserved through all status changes
```

## URL Parameter Combinations

```
┌────────────────┬────────────┬──────────────────────────────┐
│ Role           │ Status     │ URL                          │
├────────────────┼────────────┼──────────────────────────────┤
│ (none)         │ active     │ ?status=active (default)     │
│ (none)         │ inactive   │ ?status=inactive             │
│ (none)         │ all        │ ?status=all                  │
│ student        │ active     │ ?role=student&status=active  │
│ student        │ inactive   │ ?role=student&status=inactive│
│ student        │ all        │ ?role=student&status=all     │
│ instructor     │ active     │ ?role=instructor&status=active│
│ super-user     │ inactive   │ ?role=super-user&status=inactive│
└────────────────┴────────────┴──────────────────────────────┘
```

## Empty State Examples

### No Inactive Users

```
┌─────────────────────────────────────────────────────────────────┐
│ Filter by Status:                                               │
│ ┌──────────────┐ ┌────────────────┐ ┌─────┐                   │
│ │ Active Users │ │ Inactive Users │ │ All │                   │
│ └──────────────┘ └────────────────┘ └─────┘                   │
│                      (active)                                   │
├─────────────────────────────────────────────────────────────────┤
│ ID │ Username │ Email │ Status │ Actions                        │
├────┴──────────┴───────┴────────┴────────────────────────────────┤
│                                                                 │
│              No inactive users found                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### No Active Users in Role

```
┌─────────────────────────────────────────────────────────────────┐
│ Filter by Role: [Student - active]                             │
│ Filter by Status: [Active Users - active]                      │
├─────────────────────────────────────────────────────────────────┤
│ ID │ Username │ Email │ Status │ Actions                        │
├────┴──────────┴───────┴────────┴────────────────────────────────┤
│                                                                 │
│         No active students found                                │
│         Try "Inactive Users" or "All"                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
