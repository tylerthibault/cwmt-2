/**
 * Calendar Instructor Module
 * Handles instructor-specific features: signup, withdrawal, slot display
 */

class CalendarInstructorModule {
    constructor(instructors, currentInstructorId) {
        this.instructors = instructors || [];
        this.currentInstructorId = currentInstructorId;
    }

    /**
     * Show event details for instructor view
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
            <div class="mt-3">
                <h6>Instructor Slots:</h6>
                ${this.renderInstructorSlots(event)}
            </div>
        `;

        const footer = `
            <button type="button" class="btn btn-secondary modal-close-btn">Close</button>
            ${this.getInstructorActionButton(event)}
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

        this.setupInstructorActions(modal, event);
    }

    /**
     * Render instructor slot availability
     */
    renderInstructorSlots(event) {
        const c1Available = !event.c1_instructor || event.c1_instructor === 'Unassigned';
        const c2Available = !event.c2_instructor || event.c2_instructor === 'Unassigned';

        return `
            <div class="instructor-slot ${c1Available ? 'available' : 'taken'}">
                <strong>C1 Instructor:</strong> ${event.c1_instructor || 'Available'}
                ${c1Available ? '<span class="badge bg-success ms-2">Available</span>' : ''}
            </div>
            <div class="instructor-slot ${c2Available ? 'available' : 'taken'}">
                <strong>C2 Instructor:</strong> ${event.c2_instructor || 'Available'}
                ${c2Available ? '<span class="badge bg-success ms-2">Available</span>' : ''}
            </div>
        `;
    }

    /**
     * Get appropriate action button for instructor
     */
    getInstructorActionButton(event) {
        // Check if course is in the past
        const courseStart = new Date(event.start);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        courseStart.setHours(0, 0, 0, 0);
        const isPast = courseStart < today;

        if (isPast) {
            return '<button type="button" class="btn btn-secondary" disabled>Past Course</button>';
        }

        // Check if user is already signed up for this course
        const isC1 = event.c1_instructor_id === this.currentInstructorId;
        const isC2 = event.c2_instructor_id === this.currentInstructorId;

        if (isC1 || isC2) {
            const role = isC1 ? 'C1' : 'C2';
            return `<button type="button" class="btn btn-danger" id="instructor-withdraw-btn" data-role="${role}">Drop ${role} Position</button>`;
        } else {
            const c1Available = !event.c1_instructor_id;
            const c2Available = !event.c2_instructor_id;

            if (!c1Available && !c2Available) {
                return '<button type="button" class="btn btn-secondary" disabled>Fully Staffed</button>';
            } else {
                return `<button type="button" class="btn btn-primary" id="instructor-signup-btn">Sign Up</button>`;
            }
        }
    }

    /**
     * Set up instructor action buttons
     */
    setupInstructorActions(modal, event) {
        const signupBtn = modal.container.querySelector('#instructor-signup-btn');
        const withdrawBtn = modal.container.querySelector('#instructor-withdraw-btn');

        if (signupBtn) {
            signupBtn.addEventListener('click', () => {
                this.showInstructorSignupOptions(event, modal);
            });
        }

        if (withdrawBtn) {
            withdrawBtn.addEventListener('click', () => {
                this.withdrawFromCourse(event.id, modal);
            });
        }
    }

    /**
     * Show instructor role selection modal
     */
    showInstructorSignupOptions(event, parentModal) {
        const c1Available = !event.c1_instructor_id;
        const c2Available = !event.c2_instructor_id;

        let options = '';
        if (c1Available) {
            options += '<div class="form-check mb-2"><input class="form-check-input" type="radio" name="instructor_role" id="c1_role" value="c1" checked><label class="form-check-label" for="c1_role">C1 Instructor (Primary)</label></div>';
        }
        if (c2Available) {
            options += '<div class="form-check mb-2"><input class="form-check-input" type="radio" name="instructor_role" id="c2_role" value="c2" ' + (c1Available ? '' : 'checked') + '><label class="form-check-label" for="c2_role">C2 Instructor (Assistant)</label></div>';
        }

        const content = `
            <p>Select your instructor role for this course:</p>
            ${options}
        `;

        const footer = `
            <button type="button" class="btn btn-secondary" id="cancel-signup-btn">Cancel</button>
            <button type="button" class="btn btn-primary" id="confirm-signup-btn">Confirm Sign Up</button>
        `;

        const signupModal = Modal.show({
            title: 'Choose Instructor Role',
            content: content,
            footer: footer,
            size: 'md'
        });

        signupModal.container.querySelector('#cancel-signup-btn').addEventListener('click', () => {
            signupModal.close();
        });

        signupModal.container.querySelector('#confirm-signup-btn').addEventListener('click', () => {
            const selectedRole = signupModal.container.querySelector('input[name="instructor_role"]:checked').value;
            this.signupForInstructorRole(event.id, selectedRole, signupModal, parentModal);
        });
    }

    /**
     * Sign up for instructor role
     */
    signupForInstructorRole(courseId, role, signupModal, parentModal) {
        signupModal.showLoading();

        fetch('/courses/instructor/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_instance_id: courseId, role: role })
        })
        .then(response => response.json())
        .then(data => {
            signupModal.close();
            parentModal.close();
            if (data.success) {
                Modal.alert({ 
                    title: 'Success', 
                    message: 'Successfully signed up as ' + role.toUpperCase() + ' instructor!' 
                }).then(() => {
                    location.reload();
                });
            } else {
                Modal.alert({ 
                    title: 'Error', 
                    message: data.message || 'Failed to sign up for course.' 
                });
            }
        })
        .catch(error => {
            signupModal.close();
            Modal.alert({ 
                title: 'Error', 
                message: 'An error occurred while signing up.' 
            });
        });
    }

    /**
     * Withdraw from course
     */
    withdrawFromCourse(courseId, modal) {
        const confirmModal = Modal.show({
            title: 'Drop Course Position',
            content: '<p>Are you sure you want to drop your instructor position for this course?</p>',
            footer: `
                <button type="button" class="btn btn-secondary" id="cancel-drop-btn">Cancel</button>
                <button type="button" class="btn btn-danger" id="confirm-drop-btn">Drop Position</button>
            `,
            size: 'md'
        });

        confirmModal.container.querySelector('#cancel-drop-btn').addEventListener('click', () => {
            confirmModal.close();
        });

        confirmModal.container.querySelector('#confirm-drop-btn').addEventListener('click', () => {
            confirmModal.close();
            modal.showLoading();

            fetch('/courses/instructor/withdraw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ course_instance_id: courseId })
            })
            .then(response => response.json())
            .then(data => {
                modal.close();
                if (data.success) {
                    Modal.show({
                        title: 'Success',
                        content: '<p>Successfully dropped your position from the course.</p>',
                        footer: '<button type="button" class="btn btn-primary modal-ok-btn">OK</button>',
                        size: 'md'
                    }).container.querySelector('.modal-ok-btn').addEventListener('click', () => {
                        location.reload();
                    });
                } else {
                    Modal.show({
                        title: 'Error',
                        content: `<p>${data.message || 'Failed to drop course position.'}</p>`,
                        footer: '<button type="button" class="btn btn-primary modal-ok-btn">OK</button>',
                        size: 'md'
                    });
                }
            })
            .catch(error => {
                modal.close();
                Modal.show({
                    title: 'Error',
                    content: '<p>An error occurred while dropping your position.</p>',
                    footer: '<button type="button" class="btn btn-primary modal-ok-btn">OK</button>',
                    size: 'md'
                });
                console.error(error);
            });
        });
    }
}

// Export to window
window.CalendarInstructor = null; // Will be initialized with data
window.CalendarInstructorModule = CalendarInstructorModule;
