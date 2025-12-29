/**
 * Calendar Student Module
 * Handles student-specific features: course signup
 */

class CalendarStudentModule {
    /**
     * Show event details for student view
     */
    showEventDetails(event) {
        const content = `
            <p><strong>Date:</strong> ${new Date(event.start).toLocaleDateString('en-US', { 
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
            })}</p>
            <p><strong>Location:</strong> ${event.location}</p>
            <p><strong>Instructor:</strong> ${event.instructor}</p>
            <p><strong>Status:</strong> <span class="badge bg-secondary">${event.status}</span></p>
            <p><strong>Enrollment:</strong> ${event.enrollment}</p>
        `;

        const footer = `
            <button type="button" class="btn btn-secondary modal-close-btn">Close</button>
            <button type="button" class="btn btn-outline-primary" id="guest-signup-btn">
                <i class="bi bi-person-plus"></i> Enroll Someone Else
            </button>
            <button type="button" class="btn btn-primary" id="signup-btn">
                <i class="bi bi-person-check"></i> Enroll Myself
            </button>
        `;

        const modal = Modal.show({
            title: event.title,
            content: content,
            footer: footer,
            size: 'md'
        });

        modal.container.querySelector('.modal-close-btn').addEventListener('click', () => {
            modal.close();
        });

        const signupBtn = modal.container.querySelector('#signup-btn');
        if (signupBtn) {
            signupBtn.addEventListener('click', () => {
                this.signupForCourse(event.id, modal);
            });
        }

        const guestSignupBtn = modal.container.querySelector('#guest-signup-btn');
        if (guestSignupBtn) {
            guestSignupBtn.addEventListener('click', () => {
                modal.close();
                this.showGuestSignupModal(event);
            });
        }
    }

    /**
     * Show guest account creation modal
     */
    showGuestSignupModal(event) {
        // Fetch existing guest students first
        fetch('/student/guest-students')
        .then(response => response.json())
        .then(data => {
            this.renderGuestSelectionModal(event, data.guest_students || []);
        })
        .catch(error => {
            console.error('Error fetching guest students:', error);
            this.renderGuestSelectionModal(event, []);
        });
    }

    /**
     * Render guest selection or creation modal
     */
    renderGuestSelectionModal(event, guestStudents) {
        let guestListHtml = '';
        
        if (guestStudents.length > 0) {
            guestListHtml = `
                <div class="mb-3">
                    <h6 class="mb-3">Select a Family Member or Friend:</h6>
                    <div class="list-group" id="guestList">
                        ${guestStudents.map(guest => `
                            <a href="#" class="list-group-item list-group-item-action guest-item" data-guest-id="${guest.id}">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="mb-1">${guest.first_name} ${guest.last_name}</h6>
                                        <small class="text-muted">
                                            <span class="badge bg-info">${guest.relationship}</span>
                                            ${guest.email}
                                        </small>
                                    </div>
                                    <i class="bi bi-chevron-right"></i>
                                </div>
                            </a>
                        `).join('')}
                    </div>
                </div>
                <div class="text-center mb-3">
                    <button type="button" class="btn btn-outline-primary" id="showAddGuestForm">
                        <i class="bi bi-plus-circle"></i> Add New Family Member or Friend
                    </button>
                </div>
            `;
        } else {
            guestListHtml = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> 
                    You don't have any guest accounts yet. Create one to enroll family members or friends.
                </div>
            `;
        }

        const content = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i> <strong>Enrolling Someone Else</strong>
                <p class="mb-0 small">Create a guest account for family member or friend. You'll pay for their enrollment.</p>
            </div>
            
            <p class="mb-3"><strong>Course:</strong> ${event.title}</p>
            
            <div id="guestSelectionView">
                ${guestListHtml}
            </div>

            <div id="guestFormView" style="display: none;">
                <form id="guestSignupForm">
                    <div class="mb-3">
                        <label for="guest_first_name" class="form-label">First Name <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="guest_first_name" name="first_name" required>
                    </div>

                    <div class="mb-3">
                        <label for="guest_last_name" class="form-label">Last Name <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="guest_last_name" name="last_name" required>
                    </div>

                    <div class="mb-3">
                        <label for="guest_email" class="form-label">Email Address <span class="text-danger">*</span></label>
                        <input type="email" class="form-control" id="guest_email" name="email" required>
                        <small class="form-text text-muted">They'll receive course notifications at this email.</small>
                    </div>

                    <div class="mb-3">
                        <label for="guest_phone" class="form-label">Phone Number</label>
                        <input type="tel" class="form-control" id="guest_phone" name="phone_number">
                    </div>

                    <div class="mb-3">
                        <label for="relationship" class="form-label">Relationship <span class="text-danger">*</span></label>
                        <select class="form-select" id="relationship" name="relationship" required>
                            <option value="">Select relationship...</option>
                            <option value="child">Child</option>
                            <option value="spouse">Spouse</option>
                            <option value="parent">Parent</option>
                            <option value="sibling">Sibling</option>
                            <option value="friend">Friend</option>
                            <option value="other">Other</option>
                        </select>
                    </div>

                    <div class="alert alert-warning small">
                        <i class="bi bi-exclamation-triangle"></i> 
                        A temporary password will be generated and sent to their email. They can change it after logging in.
                    </div>
                </form>
                
                <button type="button" class="btn btn-link" id="backToGuestList">
                    <i class="bi bi-arrow-left"></i> Back to List
                </button>
            </div>
        `;

        const footer = `
            <button type="button" class="btn btn-secondary" id="cancel-guest-btn">Cancel</button>
            <button type="button" class="btn btn-primary" id="create-guest-btn" style="display: none;">
                <i class="bi bi-check-circle"></i> Create Account & Continue to Payment
            </button>
        `;

        const guestModal = Modal.show({
            title: 'Enroll Guest Student',
            content: content,
            footer: footer,
            size: 'lg',
            closeOnOverlay: false
        });

        // Handle guest selection
        guestModal.container.querySelectorAll('.guest-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const guestId = item.dataset.guestId;
                guestModal.close();
                window.location.href = `/student/checkout/${event.id}?guest_student_id=${guestId}`;
            });
        });

        // Handle show add guest form
        const showAddBtn = guestModal.container.querySelector('#showAddGuestForm');
        if (showAddBtn) {
            showAddBtn.addEventListener('click', () => {
                guestModal.container.querySelector('#guestSelectionView').style.display = 'none';
                guestModal.container.querySelector('#guestFormView').style.display = 'block';
                guestModal.container.querySelector('#create-guest-btn').style.display = 'inline-block';
            });
        }

        // Handle back to list
        const backBtn = guestModal.container.querySelector('#backToGuestList');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                guestModal.container.querySelector('#guestFormView').style.display = 'none';
                guestModal.container.querySelector('#guestSelectionView').style.display = 'block';
                guestModal.container.querySelector('#create-guest-btn').style.display = 'none';
            });
        }

        // If no guests, show form immediately
        if (guestStudents.length === 0) {
            guestModal.container.querySelector('#guestSelectionView').style.display = 'none';
            guestModal.container.querySelector('#guestFormView').style.display = 'block';
            guestModal.container.querySelector('#create-guest-btn').style.display = 'inline-block';
        }

        guestModal.container.querySelector('#cancel-guest-btn').addEventListener('click', () => {
            guestModal.close();
        });

        guestModal.container.querySelector('#create-guest-btn').addEventListener('click', () => {
            this.submitGuestSignup(event.id, guestModal);
        });
    }

    /**
     * Submit guest account creation
     */
    submitGuestSignup(courseId, modal) {
        const form = modal.container.querySelector('#guestSignupForm');
        
        // Validate form
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = {
            first_name: modal.container.querySelector('#guest_first_name').value,
            last_name: modal.container.querySelector('#guest_last_name').value,
            email: modal.container.querySelector('#guest_email').value,
            phone_number: modal.container.querySelector('#guest_phone').value,
            relationship: modal.container.querySelector('#relationship').value,
            course_id: courseId
        };

        modal.showLoading();

        fetch('/student/create-guest-account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modal.close();
                // Redirect to checkout with guest student ID
                window.location.href = `/student/checkout/${courseId}?guest_student_id=${data.guest_student_id}`;
            } else {
                modal.hideLoading();
                Modal.alert({ 
                    title: 'Error', 
                    message: data.message || 'Failed to create guest account.' 
                });
            }
        })
        .catch(error => {
            modal.hideLoading();
            Modal.alert({ 
                title: 'Error', 
                message: 'An error occurred while creating the guest account.' 
            });
            console.error(error);
        });
    }

    /**
     * Sign up for course (redirects to checkout)
     */
    signupForCourse(courseId, modal) {
        modal.close();
        window.location.href = `/student/checkout/${courseId}`;
    }
}

// Export to window
window.CalendarStudent = new CalendarStudentModule();
