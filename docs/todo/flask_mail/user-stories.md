# Flask-Mail User Stories

## Admin User Stories

### Template Management

**Story 1: Create Email Template**
- **As an** admin
- **I want to** create a new email template for a specific purpose
- **So that** I can customize how emails appear for different situations

**Acceptance Criteria:**
- Admin can select from predefined purposes (password_reset, new_user, course_signup, etc.)
- Admin can enter a template name (e.g., "Holiday Welcome Email")
- Admin can write subject line with variable placeholders
- Admin can write HTML body with variable placeholders
- Admin can write plain text body with variable placeholders
- System shows available variables for selected purpose
- System validates template syntax before saving
- Admin receives clear error messages for invalid templates

---

**Story 2: Preview Email Template**
- **As an** admin
- **I want to** preview an email template with sample data
- **So that** I can see how it will look before making it active

**Acceptance Criteria:**
- Admin can click "Preview" on any template
- System renders template with realistic example data
- Preview shows both HTML and plain text versions
- Preview displays in a modal or separate view
- Variables are properly replaced with sample values

---

**Story 3: Send Test Email**
- **As an** admin
- **I want to** send a test email to myself or a test address
- **So that** I can verify the template works in a real email client

**Acceptance Criteria:**
- Admin can enter a test email address
- System uses the example student data to populate variables
- Email is sent to specified address
- System confirms successful send
- Test emails are logged separately from production emails

---

**Story 4: Activate Email Template**
- **As an** admin
- **I want to** activate an email template for a specific purpose
- **So that** the system uses it when sending emails of that type

**Acceptance Criteria:**
- Admin can mark a template as "active"
- Only one template per purpose can be active at a time
- Activating a template automatically deactivates the previous active template
- System confirms which template is currently active for each purpose
- Change is immediate (no approval needed)

---

**Story 5: Edit Email Template**
- **As an** admin
- **I want to** edit an existing email template
- **So that** I can improve or update the content

**Acceptance Criteria:**
- Admin can edit any template (active or inactive)
- All template fields are editable
- System re-validates syntax on save
- Changes to active templates take effect immediately
- System tracks who made changes and when

---

**Story 6: Deactivate Email Template**
- **As an** admin
- **I want to** deactivate a template without deleting it
- **So that** I can switch back to it later (seasonal templates)

**Acceptance Criteria:**
- Admin can deactivate an active template
- Deactivated templates remain in the system
- System falls back to default template if no active template exists
- Admin can reactivate a deactivated template

---

**Story 7: View Template List**
- **As an** admin
- **I want to** see all email templates organized by purpose
- **So that** I can manage them easily

**Acceptance Criteria:**
- Admin sees list of all templates
- List shows: purpose, name, active status, creator, last modified
- Admin can filter by purpose
- Admin can filter by active/inactive status
- Active templates are clearly marked/highlighted

---

**Story 8: Delete Email Template**
- **As an** admin
- **I want to** delete unused email templates
- **So that** I can keep the template library clean

**Acceptance Criteria:**
- Admin can delete inactive templates
- System prevents deletion of active templates (must deactivate first)
- Deletion requires confirmation
- System shows warning if template cannot be deleted

---

### Email History & Monitoring

**Story 9: View Email History**
- **As an** admin
- **I want to** view a log of all emails sent by the system
- **So that** I can track communications and troubleshoot issues

**Acceptance Criteria:**
- Admin sees list of all sent emails
- Log shows: recipient, purpose, subject, sent date/time, status (sent/failed)
- Admin can filter by date range
- Admin can filter by purpose
- Admin can filter by recipient
- Admin can search by email address

---

**Story 10: View Email Details**
- **As an** admin
- **I want to** view the full details of a sent email
- **So that** I can see exactly what was sent to a user

**Acceptance Criteria:**
- Admin can click on any email log entry
- System shows: recipient, sender, subject, sent time
- System shows rendered HTML body (as sent)
- System shows plain text body (as sent)
- System shows which template was used
- System shows any error messages if email failed

---

**Story 11: Resend Email**
- **As an** admin
- **I want to** resend a previously sent email
- **So that** I can help users who didn't receive it

**Acceptance Criteria:**
- Admin can click "Resend" on any email log entry
- System sends email with same content
- New log entry is created for the resend
- Admin receives confirmation of successful resend

---

## System/Developer Stories

**Story 12: Send Email from Code**
- **As a** developer
- **I want to** send an email by specifying purpose and variables
- **So that** I don't need to manage email formatting in business logic

**Acceptance Criteria:**
- Developer calls `send_email(purpose, to, context)`
- System retrieves active template for purpose
- System validates all required variables are provided
- System renders template with provided variables
- System sends both HTML and plain text versions
- System logs the email send
- System raises clear errors for missing templates or variables

---

**Story 13: Default Templates**
- **As a** system
- **I want to** have default templates for all purposes
- **So that** emails can be sent even if admin hasn't created custom templates

**Acceptance Criteria:**
- System ships with default templates for each purpose
- Defaults are used when no active custom template exists
- Defaults are functional but basic
- Admins can view but not edit default templates
- Admins can create custom templates to override defaults

---

## User Stories (End Users)

**Story 14: Receive Password Reset Email**
- **As a** user
- **I want to** receive a clear password reset email
- **So that** I can regain access to my account

**Acceptance Criteria:**
- Email arrives promptly (within minutes)
- Subject line clearly indicates password reset
- Reset link is prominent and clickable
- Email explains expiry time
- Email works in HTML and plain text clients

---

**Story 15: Receive Welcome Email**
- **As a** new user
- **I want to** receive a welcome email with my credentials
- **So that** I know how to access the system

**Acceptance Criteria:**
- Email arrives after account creation
- Email contains temporary password
- Email contains login link
- Email has welcoming, professional tone
- Credentials are clearly visible

---

**Story 16: Receive Course Enrollment Confirmation**
- **As a** student
- **I want to** receive confirmation when I enroll in a course
- **So that** I have details about the course

**Acceptance Criteria:**
- Email arrives after enrollment
- Email contains course name, dates, location
- Email contains instructor information
- Email is visually appealing
- Important information is easy to find
