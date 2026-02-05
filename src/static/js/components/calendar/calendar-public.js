/**
 * Public/Student Calendar Module
 * Extends core calendar with enrollment features:
 * - Click event to view details and enroll
 * - Highlight enrolled courses
 */

class PublicCalendar extends Calendar {
    constructor(options = {}) {
        super(options);
        this.guestStudents = options.guestStudents || [];
    }
    
    handleEventClick(event) {
        super.handleEventClick(event);
        this.showEnrollmentModal(event);
    }
    
    showEnrollmentModal(event) {
        const spotsLeft = event.maxStudents - event.enrollmentCount;
        const isFull = spotsLeft === 0;
        const isEnrolled = this.isUserEnrolled(event);
        
        const eventDate = this.parseLocalDate(event.start);
        const dateStr = eventDate.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const content = `
            <div class="mb-3">
                <h5>${event.title}</h5>
                ${event.shortBlurb ? `<p class="lead">${event.shortBlurb}</p>` : ''}
                ${event.description ? `<p class="text-muted">${event.description}</p>` : ''}
                
                <hr>
                
                <div class="row mb-2">
                    <div class="col-4 fw-bold">Date:</div>
                    <div class="col-8">${dateStr}</div>
                </div>
                ${event.startTime ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Time:</div>
                        <div class="col-8">${event.startTime}</div>
                    </div>
                ` : ''}
                <div class="row mb-2">
                    <div class="col-4 fw-bold">Duration:</div>
                    <div class="col-8">${event.duration} day${event.duration > 1 ? 's' : ''}</div>
                </div>
                ${event.location ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Location:</div>
                        <div class="col-8">${event.location}</div>
                    </div>
                ` : ''}
                ${event.instructorText ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Instructors:</div>
                        <div class="col-8">${event.instructorText}</div>
                    </div>
                ` : ''}
                ${event.experienceLevel ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Level:</div>
                        <div class="col-8">
                            <span class="badge bg-secondary">${event.experienceLevel}</span>
                        </div>
                    </div>
                ` : ''}
                <div class="row mb-3">
                    <div class="col-4 fw-bold">Availability:</div>
                    <div class="col-8">
                        <span class="badge ${isFull ? 'bg-danger' : spotsLeft <= 3 ? 'bg-warning' : 'bg-success'}">
                            ${isFull ? 'FULL' : `${spotsLeft} spot${spotsLeft !== 1 ? 's' : ''} left`}
                        </span>
                        <small class="text-muted ms-2">(${event.enrollmentCount}/${event.maxStudents} enrolled)</small>
                    </div>
                </div>
                
                ${isEnrolled ? `
                    <div class="alert alert-success">
                        <i class="bi bi-check-circle me-2"></i>
                        <strong>You are enrolled in this course!</strong>
                    </div>
                ` : isFull ? `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <strong>This course is currently full.</strong> Check back later for availability.
                    </div>
                ` : ''}
            </div>
        `;
        
        let footer = '';
        
        if (isEnrolled) {
            footer = `
                <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Close</button>
            `;
        } else if (isFull) {
            footer = `
                <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Close</button>
            `;
        } else {
            // For student dashboard, always show enrollment option
            footer = `
                <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Not Now</button>
                <button type="button" class="btn btn-primary" onclick="window.publicCalendar.proceedToEnrollment(${event.id})">
                    <i class="bi bi-person-plus me-2"></i>Enroll Now
                </button>
            `;
        }
        
        const modal = new Modal({
            size: 'md',
            title: 'Course Details',
            content: content,
            footer: footer
        });
        
        window.currentModal = modal;
        modal.open();
    }
    
    proceedToEnrollment(courseId) {
        // Close the current modal
        if (window.currentModal) {
            window.currentModal.close();
        }
        
        // Check if user is logged in
        if (!window.currentUser) {
            // User not logged in - show signup modal
            if (typeof showSignupModal === 'function') {
                // Get course name from the event
                const event = this.events.find(e => e.id === courseId);
                const courseName = event ? event.title : 'Course';
                showSignupModal(courseId, courseName);
            } else {
                // Fallback - redirect to auth with return URL
                window.location.href = `/auth/login?next=/student/checkout/${courseId}`;
            }
            return;
        }
        
        // Check if there are guest students
        if (this.guestStudents && this.guestStudents.length > 0) {
            // Show selection modal
            this.showEnrollmentSelectionModal(courseId);
        } else {
            // Enroll directly for the current student
            window.location.href = `/student/checkout/${courseId}`;
        }
    }
    
    showEnrollmentSelectionModal(courseId) {
        let content = `
            <div class="mb-3">
                <p class="lead">Who would you like to enroll in this course?</p>
                <div class="list-group">
                    <button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" 
                            onclick="window.location.href='/student/checkout/${courseId}'">
                        <div>
                            <i class="bi bi-person-fill me-2"></i>
                            <strong>Myself</strong>
                        </div>
                        <i class="bi bi-chevron-right"></i>
                    </button>
        `;
        
        // Add guest students
        this.guestStudents.forEach(guest => {
            content += `
                    <button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" 
                            onclick="window.location.href='/student/checkout/${courseId}?guest_student_id=${guest.id}'">
                        <div>
                            <i class="bi bi-person me-2"></i>
                            <strong>${guest.first_name} ${guest.last_name}</strong>
                            <small class="text-muted ms-2">(${guest.relationship || 'Family/Friend'})</small>
                        </div>
                        <i class="bi bi-chevron-right"></i>
                    </button>
            `;
        });
        
        content += `
                </div>
                <div class="mt-3 text-center">
                    <a href="/student/family-friends" class="btn btn-link">
                        <i class="bi bi-plus-circle me-1"></i>Add Family Member or Friend
                    </a>
                </div>
            </div>
        `;
        
        const modal = new Modal({
            size: 'md',
            title: 'Select Student',
            content: content,
            footer: `
                <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Cancel</button>
            `
        });
        
        window.currentModal = modal;
        modal.open();
    }
}

// Export for use in templates
window.PublicCalendar = PublicCalendar;
