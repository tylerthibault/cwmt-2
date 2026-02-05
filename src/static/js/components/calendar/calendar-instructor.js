/**
 * Instructor Calendar Module
 * Extends core calendar with instructor-specific features:
 * - Click event to sign up as C1 or C2 instructor
 * - Highlight courses they're already teaching
 */

class InstructorCalendar extends Calendar {
    constructor(options = {}) {
        // Store instructor ID before super() is called
        const instructorId = options.currentInstructorId || window.currentInstructorId;
        
        super(options);
        
        // Set it as instance property (super() already called init())
        this.currentInstructorId = instructorId;
        
        // Re-render now that currentInstructorId is set
        console.log('Re-rendering with instructor ID:', this.currentInstructorId);
        this.render();
    }
    
    handleEventClick(event) {
        super.handleEventClick(event);
        this.showCourseDetailsModal(event);
    }
    
    isTeachingCourse(event) {
        return event.instructorC1Id === this.currentInstructorId || 
               event.instructorC2Id === this.currentInstructorId;
    }
    
    createEventElement(event, cellDate) {
        const eventElement = super.createEventElement(event, cellDate);
        
        console.log('Creating event element for:', event.title);
        console.log('  Current Instructor ID:', this.currentInstructorId);
        console.log('  Event C1 ID:', event.instructorC1Id);
        console.log('  Event C2 ID:', event.instructorC2Id);
        console.log('  isTeachingCourse result:', this.isTeachingCourse(event));
        
        // Add highlight class if instructor is teaching this course
        if (this.isTeachingCourse(event)) {
            console.log('  -> Adding teaching class!');
            eventElement.classList.add('teaching');
        }
        
        return eventElement;
    }
    
    createMobileEventCard(event) {
        const card = super.createMobileEventCard(event);
        
        // Add highlight class if instructor is teaching this course
        if (this.isTeachingCourse(event)) {
            card.classList.add('teaching');
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
        
        const isTeaching = this.isTeachingCourse(event);
        const hasC1 = event.instructorC1Id !== null && event.instructorC1Id !== undefined && event.instructorC1Id !== 0;
        const hasC2 = event.instructorC2Id !== null && event.instructorC2Id !== undefined && event.instructorC2Id !== 0;
        const canSignUpC1 = !hasC1 && !isTeaching;
        const canSignUpC2 = !hasC2 && !isTeaching;
        
        console.log('Event:', event);
        console.log('Current Instructor ID:', this.currentInstructorId);
        console.log('instructorC1Id:', event.instructorC1Id, 'instructorC2Id:', event.instructorC2Id);
        console.log('isTeaching:', isTeaching);
        console.log('hasC1:', hasC1, 'hasC2:', hasC2);
        console.log('canSignUpC1:', canSignUpC1, 'canSignUpC2:', canSignUpC2);
        
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
                ${event.experienceLevel ? `
                    <div class="row mb-2">
                        <div class="col-4 fw-bold">Level:</div>
                        <div class="col-8">
                            <span class="badge bg-secondary">${event.experienceLevel}</span>
                        </div>
                    </div>
                ` : ''}
                <div class="row mb-3">
                    <div class="col-4 fw-bold">Instructors:</div>
                    <div class="col-8">
                        <div class="mb-2">
                            <strong>C1:</strong> 
                            ${hasC1 && event.instructorText ? event.instructorText.split(' & ')[0] : '<span class="text-muted">Available</span>'}
                            ${event.instructorC1Id === this.currentInstructorId ? '<span class="badge bg-success ms-2">You</span>' : ''}
                        </div>
                        <div>
                            <strong>C2:</strong> 
                            ${hasC2 && event.instructorText ? (event.instructorText.includes(' & ') ? event.instructorText.split(' & ')[1] : '<span class="text-muted">Available</span>') : '<span class="text-muted">Available</span>'}
                            ${event.instructorC2Id === this.currentInstructorId ? '<span class="badge bg-success ms-2">You</span>' : ''}
                        </div>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-4 fw-bold">Enrollment:</div>
                    <div class="col-8">
                        <span class="badge bg-info">
                            ${event.enrollmentCount}/${event.maxStudents} students
                        </span>
                    </div>
                </div>
                
                ${isTeaching ? `
                    <div class="alert alert-success">
                        <i class="bi bi-check-circle me-2"></i>
                        <strong>You are teaching this course!</strong>
                    </div>
                ` : ''}
            </div>
        `;
        
        let footer = '';
        
        if (isTeaching) {
            footer = `
                <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Close</button>
            `;
        } else if (!canSignUpC1 && !canSignUpC2) {
            footer = `
                <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Close</button>
            `;
        } else {
            footer = `
                <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Close</button>
                <div class="d-flex gap-2">
                    ${canSignUpC1 ? `
                        <button type="button" class="btn btn-primary" onclick="window.instructorCalendar.signUpForCourse(${event.id}, 'c1')">
                            <i class="bi bi-person-plus me-2"></i>Sign Up as C1
                        </button>
                    ` : ''}
                    ${canSignUpC2 ? `
                        <button type="button" class="btn btn-outline-primary" onclick="window.instructorCalendar.signUpForCourse(${event.id}, 'c2')">
                            <i class="bi bi-person-plus me-2"></i>Sign Up as C2
                        </button>
                    ` : ''}
                </div>
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
    
    signUpForCourse(courseId, position) {
        // Close the modal
        if (window.currentModal) {
            window.currentModal.close();
        }
        
        console.log('Signing up for course:', courseId, 'as', position);
        
        // Send request to sign up
        fetch('/courses/instructor/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                course_instance_id: courseId,
                role: position
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                // Return the HTML as text to see what the error is
                return response.text().then(text => {
                    console.error('Received HTML instead of JSON:', text);
                    throw new Error('Server returned an error page. Check console for details.');
                });
            }
        })
        .then(data => {
            if (data.success) {
                alert(`Successfully signed up as ${position.toUpperCase()}!`);
                location.reload(); // Reload to show updated calendar
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while signing up for the course. Check console for details.');
        });
    }
}

// Export for use in templates
window.InstructorCalendar = InstructorCalendar;
