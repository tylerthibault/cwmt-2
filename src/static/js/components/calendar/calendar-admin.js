/**
 * Admin Calendar Module
 * Extends core calendar with admin-specific features:
 * - Click empty day to create new course instance
 * - Click event to edit/manage course instance
 */

class AdminCalendar extends Calendar {
    constructor(options = {}) {
        super(options);
        
        this.courseTemplates = options.courseTemplates || [];
        this.instructors = options.instructors || [];
        this.locations = options.locations || [];
    }
    
    createEventElement(event, cellDate) {
        const eventElement = super.createEventElement(event, cellDate);
        
        // Add instructor indicators
        if (event.hasC1 || event.hasC2) {
            const instructorBadge = document.createElement('div');
            instructorBadge.classList.add('instructor-badges');
            
            if (event.hasC1) {
                const c1Badge = document.createElement('span');
                c1Badge.classList.add('instructor-badge', 'c1-badge');
                c1Badge.textContent = 'C1';
                c1Badge.title = 'C1 Instructor Assigned';
                instructorBadge.appendChild(c1Badge);
            }
            
            if (event.hasC2) {
                const c2Badge = document.createElement('span');
                c2Badge.classList.add('instructor-badge', 'c2-badge');
                c2Badge.textContent = 'C2';
                c2Badge.title = 'C2 Instructor Assigned';
                instructorBadge.appendChild(c2Badge);
            }
            
            eventElement.appendChild(instructorBadge);
        }
        
        return eventElement;
    }
    
    handleDayClick(date, events) {
        super.handleDayClick(date, events);
        
        console.log('Admin day clicked:', date, 'Events:', events);
        
        // Admin can click any day to create a new course
        if (events.length === 0) {
            this.showCreateCourseModal(date);
        } else {
            this.showDayEventsModal(date, events);
        }
    }
    
    handleEventClick(event) {
        super.handleEventClick(event);
        console.log('Admin event clicked:', event);
        this.showEventDetailsModal(event);
    }
    
    showCreateCourseModal(date) {
        const dateStr = date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const formattedDate = this.formatDate(date);
        
        // Initialize wizard data
        this.wizardData = {
            selectedDate: formattedDate,
            selectedTemplate: null,
            selectedTime: '09:00',
            duration: null,
            maxStudents: null,
            locationId: null,
            c1InstructorId: null,
            c2InstructorId: null,
            notes: ''
        };
        
        const content = this.buildWizardContent();
        
        const footer = `
            <div class="wizard-footer">
                <button type="button" class="btn btn-secondary wizard-btn-prev" style="display: none;">
                    <i class="bi bi-arrow-left"></i> Back
                </button>
                <div>
                    <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Cancel</button>
                    <button type="button" class="btn btn-primary wizard-btn-next">
                        Next <i class="bi bi-arrow-right"></i>
                    </button>
                    <button type="button" class="btn btn-primary wizard-btn-finish" style="display: none;">
                        <i class="bi bi-check-circle"></i> Schedule Course
                    </button>
                </div>
            </div>
        `;
        
        const modal = new Modal({
            size: 'lg',
            title: `Schedule New Course - ${dateStr}`,
            content: content,
            footer: footer
        });
        
        window.currentModal = modal;
        modal.open();
        
        this.initializeWizard();
    }
    
    buildWizardContent() {
        // Build course template cards
        const templateCards = this.courseTemplates.map(template => `
            <div class="col">
                <div class="course-template-card h-100" data-template-id="${template.id}" data-duration="${template.duration_days}" data-max="${template.max_students}">
                    <div class="template-name">${template.name}</div>
                    <div class="template-details d-flex flex-wrap">
                        <span><i class="bi bi-calendar"></i> ${template.duration_days} day${template.duration_days > 1 ? 's' : ''}</span>
                        <span><i class="bi bi-people"></i> Max ${template.max_students} students</span>
                        <span class="template-badge">${template.experience_level}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Build instructor options
        const instructorOptions = this.instructors.map(instructor => 
            `<option value="${instructor.id}">${instructor.user.first_name} ${instructor.user.last_name}</option>`
        ).join('');
        
        // Build location options (tax display will be controlled by course template taxability)
        const locationOptions = this.locations.map(location => {
            return `<option value="${location.id}" data-tax-rate="${location.tax_rate}">${location.name}</option>`;
        }).join('');
        
        return `
            <div class="wizard-container">
                <ul class="wizard-steps">
                    <li class="wizard-step active" data-step="1">
                        <div class="wizard-step-indicator">1</div>
                        <div class="wizard-step-label">Choose Course</div>
                    </li>
                    <li class="wizard-step" data-step="2">
                        <div class="wizard-step-indicator">2</div>
                        <div class="wizard-step-label">Set Time</div>
                    </li>
                    <li class="wizard-step" data-step="3">
                        <div class="wizard-step-indicator">3</div>
                        <div class="wizard-step-label">Details</div>
                    </li>
                    <li class="wizard-step" data-step="4">
                        <div class="wizard-step-indicator">4</div>
                        <div class="wizard-step-label">Instructors</div>
                    </li>
                </ul>
                
                <div class="wizard-content">
                    <!-- Step 1: Course Selection -->
                    <div class="wizard-panel active" data-panel="1">
                        <h5 class="mb-4">Select a Course Type</h5>
                        <div class="course-templates-list row row-cols-1 row-cols-md-2 g-2">
                            ${templateCards}
                        </div>
                    </div>
                    
                    <!-- Step 2: Time Selection -->
                    <div class="wizard-panel" data-panel="2">
                        <h5 class="mb-4">When should this course start?</h5>
                        <div class="row">
                            <div class="col-md-6 mb-4">
                                <label class="form-label">Start Date <span class="text-danger">*</span></label>
                                <input type="date" class="form-control" id="wizardStartDate" value="${this.wizardData.selectedDate}">
                            </div>
                            <div class="col-md-6 mb-4">
                                <label class="form-label">Start Time <span class="text-danger">*</span></label>
                                <input type="time" class="form-control" id="wizardStartTime" value="09:00">
                            </div>
                        </div>
                    </div>
                    
                    <!-- Step 3: Course Details -->
                    <div class="wizard-panel" data-panel="3">
                        <h5 class="mb-4">Course Details</h5>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Duration (days)</label>
                                <input type="number" class="form-control" id="wizardDuration" min="1" readonly>
                                <small class="form-text text-muted">Set by course template</small>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Max Students</label>
                                <input type="number" class="form-control" id="wizardMaxStudents" min="1" readonly>
                                <small class="form-text text-muted">Set by course template</small>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Location <span class="text-danger">*</span></label>
                            <select class="form-select" id="wizardLocation" required>
                                <option value="">Select location...</option>
                                ${locationOptions}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Notes</label>
                            <textarea class="form-control" id="wizardNotes" rows="4" placeholder="Add any additional notes or instructions"></textarea>
                        </div>
                    </div>
                    
                    <!-- Step 4: Instructors -->
                    <div class="wizard-panel" data-panel="4">
                        <h5 class="mb-4">Assign Instructors</h5>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">C1 Instructor</label>
                                <select class="form-select" id="wizardC1Instructor">
                                    <option value="">None</option>
                                    ${instructorOptions}
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">C2 Instructor</label>
                                <select class="form-select" id="wizardC2Instructor">
                                    <option value="">None</option>
                                    ${instructorOptions}
                                </select>
                            </div>
                        </div>
                        
                        <!-- Summary -->
                        <div class="mt-4 p-3" style="background-color: #f8f9fa; border-radius: 8px;">
                            <h6>Course Summary</h6>
                            <div id="wizardSummary"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    initializeWizard() {
        this.currentStep = 1;
        
        // Template selection
        const templateCards = document.querySelectorAll('.course-template-card');
        templateCards.forEach(card => {
            card.addEventListener('click', () => {
                templateCards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                
                this.wizardData.selectedTemplate = {
                    id: parseInt(card.dataset.templateId),
                    duration: parseInt(card.dataset.duration),
                    maxStudents: parseInt(card.dataset.max),
                    name: card.querySelector('.template-name').textContent
                };
            });
        });
        
        // Navigation buttons
        const nextBtn = document.querySelector('.wizard-btn-next');
        const prevBtn = document.querySelector('.wizard-btn-prev');
        const finishBtn = document.querySelector('.wizard-btn-finish');
        
        nextBtn.addEventListener('click', () => this.wizardNext());
        prevBtn.addEventListener('click', () => this.wizardPrev());
        finishBtn.addEventListener('click', () => this.submitCreateCourse());
    }
    
    wizardNext() {
        // Validate current step
        if (this.currentStep === 1 && !this.wizardData.selectedTemplate) {
            Modal.alert({ title: 'Required', message: 'Please select a course type' });
            return;
        }
        
        if (this.currentStep === 3) {
            const locationId = document.getElementById('wizardLocation').value;
            if (!locationId) {
                Modal.alert({ title: 'Required', message: 'Please select a location' });
                return;
            }
            this.wizardData.locationId = parseInt(locationId);
            this.wizardData.notes = document.getElementById('wizardNotes').value;
        }
        
        this.currentStep++;
        this.updateWizardUI();
        
        // Capture time and duration on step 3
        if (this.currentStep === 3) {
            this.wizardData.selectedTime = document.getElementById('wizardStartTime').value;
            this.wizardData.selectedDate = document.getElementById('wizardStartDate').value;
            document.getElementById('wizardDuration').value = this.wizardData.selectedTemplate.duration;
            document.getElementById('wizardMaxStudents').value = this.wizardData.selectedTemplate.maxStudents;
            this.wizardData.duration = this.wizardData.selectedTemplate.duration;
            this.wizardData.maxStudents = this.wizardData.selectedTemplate.maxStudents;
            
            // Update location dropdown to show/hide tax rates based on template taxability
            this.updateLocationDropdown();
        }
        
        // Show summary on step 4
        if (this.currentStep === 4) {
            this.wizardData.c1InstructorId = document.getElementById('wizardC1Instructor').value || null;
            this.wizardData.c2InstructorId = document.getElementById('wizardC2Instructor').value || null;
            this.updateSummary();
        }
    }
    
    wizardPrev() {
        this.currentStep--;
        this.updateWizardUI();
    }
    
    updateWizardUI() {
        // Update step indicators
        document.querySelectorAll('.wizard-step').forEach((step, index) => {
            const stepNum = index + 1;
            step.classList.remove('active', 'completed');
            if (stepNum < this.currentStep) {
                step.classList.add('completed');
            } else if (stepNum === this.currentStep) {
                step.classList.add('active');
            }
        });
        
        // Update panels
        document.querySelectorAll('.wizard-panel').forEach((panel, index) => {
            panel.classList.toggle('active', index + 1 === this.currentStep);
        });
        
        // Update buttons
        const prevBtn = document.querySelector('.wizard-btn-prev');
        const nextBtn = document.querySelector('.wizard-btn-next');
        const finishBtn = document.querySelector('.wizard-btn-finish');
        
        prevBtn.style.display = this.currentStep > 1 ? 'block' : 'none';
        nextBtn.style.display = this.currentStep < 4 ? 'inline-block' : 'none';
        finishBtn.style.display = this.currentStep === 4 ? 'inline-block' : 'none';
    }
    
    updateLocationDropdown() {
        const template = this.courseTemplates.find(t => t.id === this.wizardData.selectedTemplate.id);
        const isTaxable = template && template.is_taxable !== false;
        const locationSelect = document.getElementById('wizardLocation');
        
        if (!locationSelect) return;
        
        // Update all option text to show or hide tax rates
        this.locations.forEach(location => {
            const option = locationSelect.querySelector(`option[value="${location.id}"]`);
            if (option) {
                console.log("*************************");
                console.log("Updating location option:", location.name, "isTaxable:", isTaxable);
                console.log(template)
                console.log("*************************");
                if (isTaxable) {
                    const taxRate = location.tax_rate ? (parseFloat(location.tax_rate) * 100).toFixed(2) : '0.00';
                    option.textContent = `${location.name} (Tax: ${taxRate}%)`;
                } else {
                    option.textContent = location.name;
                }
            }
        });
    }
    
    updateSummary() {
        const template = this.courseTemplates.find(t => t.id === this.wizardData.selectedTemplate.id);
        const c1Instructor = this.instructors.find(i => i.id === parseInt(this.wizardData.c1InstructorId));
        const c2Instructor = this.instructors.find(i => i.id === parseInt(this.wizardData.c2InstructorId));
        const location = this.locations.find(l => l.id === this.wizardData.locationId);
        
        const taxRate = location && location.tax_rate ? (parseFloat(location.tax_rate) * 100).toFixed(2) : '0.00';
        const isTaxable = template && template.is_taxable !== false;
        
        const summary = `
            <p><strong>Course:</strong> ${this.wizardData.selectedTemplate.name}${!isTaxable ? ' <span class="badge bg-info">Tax Exempt</span>' : ''}</p>
            <p><strong>Start:</strong> ${new Date(this.wizardData.selectedDate).toLocaleDateString()} at ${this.wizardData.selectedTime}</p>
            <p><strong>Duration:</strong> ${this.wizardData.duration} day${this.wizardData.duration > 1 ? 's' : ''}</p>
            <p><strong>Location:</strong> ${location ? location.name : 'Unknown'}</p>
            <p><strong>Tax Rate:</strong> ${!isTaxable ? '<span class="text-muted">Tax Exempt</span>' : taxRate + '%'}</p>
            <p><strong>Max Students:</strong> ${this.wizardData.maxStudents}</p>
            ${c1Instructor ? `<p><strong>C1 Instructor:</strong> ${c1Instructor.user.first_name} ${c1Instructor.user.last_name}</p>` : ''}
            ${c2Instructor ? `<p><strong>C2 Instructor:</strong> ${c2Instructor.user.first_name} ${c2Instructor.user.last_name}</p>` : ''}
            ${this.wizardData.notes ? `<p><strong>Notes:</strong> ${this.wizardData.notes}</p>` : ''}
        `;
        
        document.getElementById('wizardSummary').innerHTML = summary;
    }
    
    async submitCreateCourse() {
        const data = {
            course_template_id: this.wizardData.selectedTemplate.id,
            start_date: this.wizardData.selectedDate,
            start_time: this.wizardData.selectedTime,
            duration_days: this.wizardData.duration,
            max_students: this.wizardData.maxStudents,
            location_id: this.wizardData.locationId,
            c1_instructor_id: this.wizardData.c1InstructorId ? parseInt(this.wizardData.c1InstructorId) : null,
            c2_instructor_id: this.wizardData.c2InstructorId ? parseInt(this.wizardData.c2InstructorId) : null,
            notes: this.wizardData.notes || null
        };
        
        try {
            const response = await fetch('/courses/admin/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                await Modal.alert({
                    title: 'Success',
                    message: result.message || 'Course created successfully!'
                });
                
                window.currentModal.close();
                
                // Reload page to refresh calendar
                window.location.reload();
            } else {
                await Modal.alert({
                    title: 'Error',
                    message: result.message || 'Failed to create course'
                });
            }
        } catch (error) {
            await Modal.alert({
                title: 'Error',
                message: `Error creating course: ${error.message}`
            });
        }
    }
    
    showDayEventsModal(date, events) {
        const dateStr = date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const eventsList = events.map(event => {
            const spotsLeft = event.maxStudents - event.enrollmentCount;
            return `
                <div class="card mb-2" style="border-left: 4px solid ${event.color}; cursor: pointer;" 
                     onclick="window.adminCalendar.showEventDetailsModal(${JSON.stringify(event).replace(/"/g, '&quot;')})">
                    <div class="card-body">
                        <h6 class="card-title mb-2">${event.title}</h6>
                        <div class="small text-muted">
                            ${event.startTime ? `<div><i class="bi bi-clock me-2"></i>${event.startTime}</div>` : ''}
                            ${event.location ? `<div><i class="bi bi-geo-alt me-2"></i>${event.location}</div>` : ''}
                            <div><i class="bi bi-people me-2"></i>${event.enrollmentCount}/${event.maxStudents} enrolled (${spotsLeft} spots left)</div>
                            ${event.instructorText ? `<div><i class="bi bi-person me-2"></i>${event.instructorText}</div>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        const content = `
            <div class="mb-3">
                <p class="text-muted">Click a course to manage it</p>
                ${eventsList}
            </div>
            <button type="button" class="btn btn-primary w-100" onclick="window.adminCalendar.showCreateCourseModal(new Date('${date.toISOString()}')); window.currentModal.close();">
                <i class="bi bi-plus-circle me-2"></i>Add New Course on This Day
            </button>
        `;
        
        const modal = new Modal({
            size: 'md',
            title: `Courses on ${dateStr}`,
            content: content
        });
        
        window.currentModal = modal;
        modal.open();
    }
    
    showEventDetailsModal(event) {
        const spotsLeft = event.maxStudents - event.enrollmentCount;
        const eventDate = new Date(event.start);
        const dateStr = eventDate.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const content = `
            <div class="mb-3">
                <h5>${event.title}</h5>
                <p class="text-muted mb-3">${event.shortBlurb || event.description || 'No description available'}</p>
                
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
                <div class="row mb-2">
                    <div class="col-4 fw-bold">Enrollment:</div>
                    <div class="col-8">
                        <span class="badge ${spotsLeft > 3 ? 'bg-success' : spotsLeft > 0 ? 'bg-warning' : 'bg-danger'}">
                            ${event.enrollmentCount}/${event.maxStudents} enrolled
                        </span>
                    </div>
                </div>
                <div class="row mb-2">
                    <div class="col-4 fw-bold">Status:</div>
                    <div class="col-8">
                        <span class="badge bg-info">${event.status}</span>
                    </div>
                </div>
            </div>
        `;
        
        const footer = `
            <a href="/courses/admin/view/${event.id}" class="btn btn-primary">Manage Course</a>
            <button type="button" class="btn btn-secondary" onclick="window.currentModal.close()">Close</button>
        `;
        
        const modal = new Modal({
            size: 'md',
            title: 'Course Details',
            content: content,
            footer: footer
        });
        
        window.currentModal = modal;
        modal.open();
    }
}

// Export for use in templates
window.AdminCalendar = AdminCalendar;
