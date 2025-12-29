/**
 * Calendar Admin Module
 * Handles admin-specific features: course creation wizard, event details
 */

class CalendarAdminModule {
    constructor(courseTemplates, instructors) {
        this.courseTemplates = courseTemplates || [];
        this.instructors = instructors || [];
        this.currentWizardStep = 1;
    }

    /**
     * Open the schedule course wizard
     */
    openScheduleWizard(selectedDate) {        console.log('Opening wizard with templates:', this.courseTemplates);
        console.log('Opening wizard with instructors:', this.instructors);
                this.currentWizardStep = 1;
        const dateStr = selectedDate.toLocaleDateString('en-US', { 
            weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' 
        });

        const wizardContent = `
            <div class="wizard-steps">
                <div class="wizard-step active" data-step="1">
                    <div class="wizard-step-number">1</div>
                    <div>Course</div>
                </div>
                <div class="wizard-step" data-step="2">
                    <div class="wizard-step-number">2</div>
                    <div>Details</div>
                </div>
                <div class="wizard-step" data-step="3">
                    <div class="wizard-step-number">3</div>
                    <div>Review</div>
                </div>
            </div>
            
            <div class="wizard-content">
                <!-- Step 1: Select Course Template -->
                <div class="wizard-form-section active" data-step="1">
                    <h5>Select Course Template</h5>
                    <p class="text-muted">Scheduled for: ${dateStr}</p>
                    <div class="mb-3">
                        <label class="form-label">Course Template <span class="text-danger">*</span></label>
                        <select class="form-select" id="course_template_id" required>
                            <option value="">Select a course...</option>
                            ${this.courseTemplates.map(t => 
                                `<option value="${t.id}" data-max="${t.max_students}" data-duration="${t.duration_days}">${t.name}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
                
                <!-- Step 2: Course Details -->
                <div class="wizard-form-section" data-step="2">
                    <h5>Course Details</h5>
                    <div class="mb-3">
                        <label class="form-label">Start Time <span class="text-danger">*</span></label>
                        <input type="time" class="form-control" id="start_time" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Location <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="location" placeholder="e.g., Building A, Room 101" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Duration (Days) <span class="text-danger">*</span></label>
                        <input type="number" class="form-control" id="duration_days" min="1" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Maximum Students <span class="text-danger">*</span></label>
                        <input type="number" class="form-control" id="max_students" min="1" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">C1 Instructor</label>
                        <select class="form-select" id="c1_instructor_id">
                            <option value="">Unassigned</option>
                            ${this.instructors.map(i => `<option value="${i.id}">${i.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">C2 Instructor</label>
                        <select class="form-select" id="c2_instructor_id">
                            <option value="">Unassigned</option>
                            ${this.instructors.map(i => `<option value="${i.id}">${i.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Notes</label>
                        <textarea class="form-control" id="notes" rows="3" placeholder="Optional notes about this course instance"></textarea>
                    </div>
                </div>
                
                <!-- Step 3: Review -->
                <div class="wizard-form-section" data-step="3">
                    <h5>Review & Confirm</h5>
                    <div id="review-content" class="alert alert-info">
                        <p><strong>Date:</strong> ${dateStr}</p>
                        <p id="review-details"></p>
                    </div>
                </div>
            </div>
        `;

        const footer = `
            <button type="button" class="btn btn-secondary" id="wizard-prev" style="display: none;">Previous</button>
            <button type="button" class="btn btn-primary" id="wizard-next">Next</button>
            <button type="button" class="btn btn-success" id="wizard-submit" style="display: none;">Schedule Course</button>
        `;

        const modal = Modal.show({
            title: 'Schedule New Course',
            content: wizardContent,
            footer: footer,
            size: 'lg',
            closeOnOverlay: false
        });

        modal.selectedDate = selectedDate;
        this.setupWizardNavigation(modal);

        const templateSelect = modal.container.querySelector('#course_template_id');
        templateSelect.addEventListener('change', (e) => {
            const selectedOption = e.target.options[e.target.selectedIndex];
            if (selectedOption.value) {
                modal.templateData = {
                    maxStudents: selectedOption.dataset.max,
                    duration: selectedOption.dataset.duration
                };
            }
        });
    }

    /**
     * Set up wizard navigation
     */
    setupWizardNavigation(modal) {
        const nextBtn = modal.container.querySelector('#wizard-next');
        const prevBtn = modal.container.querySelector('#wizard-prev');
        const submitBtn = modal.container.querySelector('#wizard-submit');

        nextBtn.addEventListener('click', () => {
            if (this.validateStep(this.currentWizardStep, modal)) {
                this.currentWizardStep++;
                this.updateWizardStep(modal);
            }
        });

        prevBtn.addEventListener('click', () => {
            this.currentWizardStep--;
            this.updateWizardStep(modal);
        });

        submitBtn.addEventListener('click', () => {
            this.submitCourse(modal);
        });
    }

    /**
     * Update wizard step UI
     */
    updateWizardStep(modal) {
        const container = modal.container;

        container.querySelectorAll('.wizard-step').forEach(step => {
            const stepNum = parseInt(step.dataset.step);
            step.classList.remove('active', 'completed');
            if (stepNum === this.currentWizardStep) {
                step.classList.add('active');
            } else if (stepNum < this.currentWizardStep) {
                step.classList.add('completed');
            }
        });

        container.querySelectorAll('.wizard-form-section').forEach(section => {
            section.classList.remove('active');
            if (parseInt(section.dataset.step) === this.currentWizardStep) {
                section.classList.add('active');
            }
        });

        const nextBtn = container.querySelector('#wizard-next');
        const prevBtn = container.querySelector('#wizard-prev');
        const submitBtn = container.querySelector('#wizard-submit');

        prevBtn.style.display = this.currentWizardStep > 1 ? 'inline-block' : 'none';

        if (this.currentWizardStep === 3) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
            this.updateReview(modal);
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';

            if (this.currentWizardStep === 2 && modal.templateData) {
                const maxStudentsInput = container.querySelector('#max_students');
                const durationInput = container.querySelector('#duration_days');
                if (!maxStudentsInput.value) {
                    maxStudentsInput.value = modal.templateData.maxStudents;
                }
                if (!durationInput.value) {
                    durationInput.value = modal.templateData.duration;
                }
            }
        }
    }

    /**
     * Validate current wizard step
     */
    validateStep(step, modal) {
        const container = modal.container;
        const currentSection = container.querySelector(`.wizard-form-section[data-step="${step}"]`);

        if (step === 1) {
            const templateField = currentSection.querySelector('#course_template_id');
            const template = templateField ? templateField.value : '';
            console.log('Validating step 1, template value:', template, 'field:', templateField);
            if (!template) {
                Modal.alert({ title: 'Required Field', message: 'Please select a course template.' });
                return false;
            }
        } else if (step === 2) {
            const time = currentSection.querySelector('#start_time').value;
            const location = currentSection.querySelector('#location').value;
            const durationDays = currentSection.querySelector('#duration_days').value;
            const maxStudents = currentSection.querySelector('#max_students').value;
            if (!time || !location || !durationDays || !maxStudents) {
                Modal.alert({ title: 'Required Fields', message: 'Please fill in all required fields.' });
                return false;
            }
        }

        return true;
    }

    /**
     * Update review step content
     */
    updateReview(modal) {
        const container = modal.container;
        const reviewDetails = container.querySelector('#review-details');

        const templateSelect = container.querySelector('#course_template_id');
        const templateText = templateSelect.options[templateSelect.selectedIndex].text;
        const time = container.querySelector('#start_time').value;
        const location = container.querySelector('#location').value;
        const durationDays = container.querySelector('#duration_days').value;
        const maxStudents = container.querySelector('#max_students').value;
        const notes = container.querySelector('#notes').value;

        const c1InstructorSelect = container.querySelector('#c1_instructor_id');
        const c1InstructorText = c1InstructorSelect.value ? 
            c1InstructorSelect.options[c1InstructorSelect.selectedIndex].text : 'Unassigned';

        const c2InstructorSelect = container.querySelector('#c2_instructor_id');
        const c2InstructorText = c2InstructorSelect.value ? 
            c2InstructorSelect.options[c2InstructorSelect.selectedIndex].text : 'Unassigned';

        reviewDetails.innerHTML = `
            <p><strong>Course:</strong> ${templateText}</p>
            <p><strong>Time:</strong> ${time}</p>
            <p><strong>Location:</strong> ${location}</p>
            <p><strong>Duration:</strong> ${durationDays} day(s)</p>
            <p><strong>Maximum Students:</strong> ${maxStudents}</p>
            <p><strong>C1 Instructor:</strong> ${c1InstructorText}</p>
            <p><strong>C2 Instructor:</strong> ${c2InstructorText}</p>
            ${notes ? `<p><strong>Notes:</strong> ${notes}</p>` : ''}
        `;
    }

    /**
     * Submit course creation
     */
    submitCourse(modal) {
        const container = modal.container;

        const year = modal.selectedDate.getFullYear();
        const month = String(modal.selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(modal.selectedDate.getDate()).padStart(2, '0');
        const localDateString = `${year}-${month}-${day}`;

        const formData = {
            course_template_id: container.querySelector('#course_template_id').value,
            start_date: localDateString,
            start_time: container.querySelector('#start_time').value,
            location: container.querySelector('#location').value,
            duration_days: container.querySelector('#duration_days').value,
            max_students: container.querySelector('#max_students').value,
            c1_instructor_id: container.querySelector('#c1_instructor_id').value || null,
            c2_instructor_id: container.querySelector('#c2_instructor_id').value || null,
            notes: container.querySelector('#notes').value || null
        };

        modal.showLoading();

        fetch('/courses/admin/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            modal.close();
            if (data.success) {
                Modal.alert({ 
                    title: 'Success', 
                    message: 'Course scheduled successfully!' 
                }).then(() => {
                    location.reload();
                });
            } else {
                Modal.alert({ 
                    title: 'Error', 
                    message: data.message || 'Failed to schedule course.' 
                });
            }
        })
        .catch(error => {
            modal.close();
            Modal.alert({ 
                title: 'Error', 
                message: 'An error occurred while scheduling the course.' 
            });
        });
    }

    /**
     * Show event details for admin view
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
            <a href="/courses/admin/view/${event.id}" class="btn btn-primary">View Full Details</a>
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
    }
}

// Export to window
window.CalendarAdmin = null; // Will be initialized with data
window.CalendarAdminModule = CalendarAdminModule;
