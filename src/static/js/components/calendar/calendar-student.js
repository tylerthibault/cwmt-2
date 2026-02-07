/**
 * Student Calendar Module
 * Extends core calendar with student-specific features:
 * - Shows all available courses
 * - Highlights courses the student is enrolled in
 */

class StudentCalendar extends Calendar {
    constructor(options = {}) {
        // Store student ID and enrollments BEFORE calling super
        // because super() will call init() which calls render()
        options.currentStudentId = options.currentStudentId || window.currentStudentId;
        options.enrolledCourseIds = options.enrolledCourseIds || window.enrolledCourseIds || [];
        
        super(options);
        
        // Set as instance properties after super
        this.currentStudentId = options.currentStudentId;
        this.enrolledCourseIds = options.enrolledCourseIds;
        this.modal = null; // Will hold Modal instance when modal is open
        
        console.log('StudentCalendar initialized with student ID:', this.currentStudentId);
        console.log('Enrolled course IDs:', this.enrolledCourseIds);
    }
    
    handleEventClick(event) {
        super.handleEventClick(event);
        this.showCourseDetailsModal(event);
    }
    
    isEnrolledInCourse(event) {
        // Defensive check - enrolledCourseIds might not be set yet during super() call
        if (!this.enrolledCourseIds) {
            return false;
        }
        const enrolled = this.enrolledCourseIds.includes(event.id);
        console.log(`Checking enrollment for course ${event.id} (${event.title}):`, enrolled);
        return enrolled;
    }
    
    createEventElement(event, cellDate) {
        const eventElement = super.createEventElement(event, cellDate);
        
        // Add enrolled class if student is enrolled in this course
        if (this.isEnrolledInCourse(event)) {
            eventElement.classList.add('enrolled');
            console.log('Added enrolled class to:', event.title);
        }
        
        return eventElement;
    }
    
    createMobileEventCard(event) {
        const card = super.createMobileEventCard(event);
        
        // Add enrolled class if student is enrolled in this course
        if (this.isEnrolledInCourse(event)) {
            card.classList.add('enrolled');
        }
        
        return card;
    }
    
    showCourseDetailsModal(event) {
        const eventDate = this.parseLocalDate(event.start);
        const dateStr = eventDate.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const isEnrolled = this.isEnrolledInCourse(event);
        
        const content = `
            <div class="mb-3">
                <h5>${event.title}</h5>
                ${event.shortBlurb ? `<p class="lead">${event.shortBlurb}</p>` : ''}
                ${event.description ? `<p class="text-muted">${event.description}</p>` : ''}
                
                <hr>
                
                ${isEnrolled ? `
                    <div class="alert alert-success mb-3">
                        <i class="bi bi-check-circle-fill me-2"></i>
                        <strong>You are enrolled in this course!</strong>
                    </div>
                ` : ''}
                
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
                ${event.durationDays ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Duration:</div>
                        <div class="col-8">${event.durationDays} day${event.durationDays !== 1 ? 's' : ''}</div>
                    </div>
                ` : ''}
                ${event.location ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Location:</div>
                        <div class="col-8">${event.location}</div>
                    </div>
                ` : ''}
                ${event.capacity !== undefined ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Capacity:</div>
                        <div class="col-8">${event.enrolled || 0} / ${event.capacity} enrolled</div>
                    </div>
                ` : ''}
                ${event.price ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Price:</div>
                        <div class="col-8">$${event.price}</div>
                    </div>
                ` : ''}
            </div>
        `;
        
        const footer = isEnrolled ? `
            <button type="button" class="btn btn-secondary" onclick="window.studentCalendar.closeModal()">
                Close
            </button>
        ` : `
            <button type="button" class="btn btn-secondary" onclick="window.studentCalendar.closeModal()">
                Cancel
            </button>
            <a href="/student/checkout/${event.id}" class="btn btn-primary">
                <i class="bi bi-cart-plus me-2"></i>
                Enroll Now
            </a>
        `;
        
        this.modal = Modal.show({
            title: 'Course Details',
            content: content,
            footer: footer,
            size: 'lg'
        });
    }
    
    closeModal() {
        if (this.modal) {
            this.modal.close();
            this.modal = null;
        }
    }
}

// Export to window for use in other scripts
window.StudentCalendar = StudentCalendar;
