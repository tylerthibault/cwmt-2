/**
 * Schedule Management JavaScript
 * Handles calendar interaction and course instance creation with wizard flow
 */

document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    let calendar;
    let currentWizardStep = 1;
    let selectedTemplate = null;
    let selectedDate = null;

    // Initialize FullCalendar
    if (calendarEl) {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            selectable: false,
            selectMirror: false,
            editable: false,
            eventClick: handleEventClick,
            dateClick: handleDateClick,
            events: loadExistingCourses(),
            eventDidMount: function(info) {
                // Add tooltip to events
                info.el.title = info.event.title + '\n' + 
                                (info.event.extendedProps.location || 'No location') + '\n' +
                                'Status: ' + (info.event.extendedProps.status || 'scheduled');
            }
        });
        
        calendar.render();
    }

    /**
     * Initialize wizard functionality
     */
    initializeWizard();

    /**
     * Load existing courses from server data
     */
    function loadExistingCourses() {
        const courses = window.existingCourses || [];
        const events = [];

        courses.forEach(course => {
            if (course.course_date && course.template) {
                const startDate = new Date(course.course_date);
                const endDate = new Date(startDate);
                endDate.setDate(endDate.getDate() + course.template.duration_days);

                events.push({
                    id: course.id,
                    title: course.template.name,
                    start: course.course_date,
                    end: endDate.toISOString().split('T')[0],
                    backgroundColor: getStatusColor(course.status),
                    borderColor: getStatusColor(course.status),
                    extendedProps: {
                        courseId: course.id,
                        templateId: course.course_template_id,
                        status: course.status,
                        location: course.location,
                        studentId: course.student_id,
                        instructor1Id: course.instructor1_id,
                        instructor2Id: course.instructor2_id,
                        duration: course.template.duration_days
                    }
                });
            }
        });

        return events;
    }

    /**
     * Get color based on course status
     */
    function getStatusColor(status) {
        const colors = {
            'scheduled': '#3788d8',
            'in_progress': '#ffa500',
            'completed': '#28a745',
            'cancelled': '#dc3545'
        };
        return colors[status] || '#3788d8';
    }

    /**
     * Handle clicking on calendar date - Open wizard modal
     */
    function handleDateClick(info) {
        selectedDate = info.dateStr;
        openWizardModal(info.dateStr);
    }

    /**
     * Handle clicking on existing event
     */
    function handleEventClick(info) {
        const courseId = info.event.extendedProps.courseId;
        showCourseDetails(courseId);
    }

    /**
     * Open wizard modal for adding course
     */
    function openWizardModal(dateStr) {
        const modal = new bootstrap.Modal(document.getElementById('addCourseWizardModal'));
        
        // Reset wizard to step 1
        currentWizardStep = 1;
        selectedTemplate = null;
        updateWizardUI();
        
        // Set selected date
        const dateObj = new Date(dateStr);
        const formattedDate = dateObj.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        document.getElementById('selectedDateDisplay').textContent = formattedDate;
        document.getElementById('selectedDateDisplay2').textContent = formattedDate;
        document.getElementById('wizardCourseDate').value = dateStr;
        
        // Clear all template selections
        document.querySelectorAll('.template-selection-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        modal.show();
    }

    /**
     * Initialize wizard functionality
     */
    function initializeWizard() {
        // Template selection cards
        document.querySelectorAll('.template-selection-card').forEach(card => {
            card.addEventListener('click', function() {
                // Deselect all
                document.querySelectorAll('.template-selection-card').forEach(c => {
                    c.classList.remove('selected');
                });
                
                // Select this one
                this.classList.add('selected');
                
                // Store selected template data
                selectedTemplate = {
                    id: this.dataset.templateId,
                    name: this.dataset.templateName,
                    duration: parseInt(this.dataset.duration),
                    description: this.dataset.description
                };
                
                // Update hidden input
                document.getElementById('wizardTemplateId').value = selectedTemplate.id;
            });
        });

        // Wizard navigation buttons
        document.getElementById('wizardNextBtn').addEventListener('click', function() {
            if (validateCurrentStep()) {
                currentWizardStep++;
                updateWizardUI();
            }
        });

        document.getElementById('wizardPrevBtn').addEventListener('click', function() {
            currentWizardStep--;
            updateWizardUI();
        });

        // Reset wizard when modal closes
        document.getElementById('addCourseWizardModal').addEventListener('hidden.bs.modal', function() {
            currentWizardStep = 1;
            selectedTemplate = null;
            updateWizardUI();
            
            // Clear form
            document.getElementById('addCourseWizardForm').reset();
        });
    }

    /**
     * Validate current wizard step
     */
    function validateCurrentStep() {
        if (currentWizardStep === 1) {
            // Validate template selection
            if (!selectedTemplate) {
                showNotification('Please select a course template', 'warning');
                return false;
            }
        } else if (currentWizardStep === 2) {
            // Validate course details
            const time = document.getElementById('courseTime').value;
            if (!time) {
                showNotification('Please enter a start time', 'warning');
                return false;
            }
        }
        return true;
    }

    /**
     * Update wizard UI based on current step
     */
    function updateWizardUI() {
        // Update step indicators
        document.querySelectorAll('.wizard-step').forEach(step => {
            const stepNum = parseInt(step.dataset.step);
            step.classList.remove('active', 'completed');
            
            if (stepNum === currentWizardStep) {
                step.classList.add('active');
            } else if (stepNum < currentWizardStep) {
                step.classList.add('completed');
            }
        });

        // Update panels
        document.querySelectorAll('.wizard-panel').forEach(panel => {
            const panelNum = parseInt(panel.dataset.panel);
            if (panelNum === currentWizardStep) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });

        // Update buttons
        const prevBtn = document.getElementById('wizardPrevBtn');
        const nextBtn = document.getElementById('wizardNextBtn');
        const submitBtn = document.getElementById('wizardSubmitBtn');

        if (currentWizardStep === 1) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        } else if (currentWizardStep === 3) {
            prevBtn.style.display = 'inline-block';
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
        } else {
            prevBtn.style.display = 'inline-block';
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        }

        // Update template info in step 2
        if (currentWizardStep === 2 && selectedTemplate) {
            document.getElementById('selectedTemplateName').textContent = selectedTemplate.name;
            document.getElementById('selectedTemplateDuration').textContent = 
                selectedTemplate.duration + ' day' + (selectedTemplate.duration > 1 ? 's' : '');
        }
    }

    /**
     * Show course details in modal
     */
    function showCourseDetails(courseId) {
        const modal = new bootstrap.Modal(document.getElementById('viewCourseModal'));
        const contentDiv = document.getElementById('courseDetailsContent');
        
        // Find course in existing courses
        const course = window.existingCourses.find(c => c.id === courseId);
        
        if (course) {
            // Build students list HTML
            let studentsHTML = '';
            if (course.students && course.students.length > 0) {
                studentsHTML = '<ul class="list-unstyled mb-0">';
                course.students.forEach(student => {
                    studentsHTML += `<li><i class="fas fa-user"></i> ${student.username} (${student.email})</li>`;
                });
                studentsHTML += '</ul>';
            } else {
                studentsHTML = '<p class="text-muted mb-0">No students enrolled</p>';
            }
            
            // Get max students info
            const maxStudents = course.max_students || (course.template ? course.template.max_students : 1);
            const enrolledCount = course.enrolled_count || 0;
            const availableSlots = maxStudents - enrolledCount;
            
            contentDiv.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Course Information</h6>
                        <p><strong>Template:</strong> ${course.template ? course.template.name : 'N/A'}</p>
                        <p><strong>Date:</strong> ${formatDate(course.course_date)}</p>
                        <p><strong>Time:</strong> ${course.course_time || 'N/A'}</p>
                        <p><strong>Duration:</strong> ${course.template ? course.template.duration_days : 'N/A'} day(s)</p>
                        <p><strong>Location:</strong> ${course.location || 'Not specified'}</p>
                        <p><strong>Status:</strong> <span class="badge" style="background-color: ${getStatusColor(course.status)}">${course.status}</span></p>
                    </div>
                    <div class="col-md-6">
                        <h6>Participants</h6>
                        <div class="mb-3">
                            <strong>Students (${enrolledCount}/${maxStudents}):</strong>
                            ${availableSlots > 0 ? `<span class="badge bg-success ms-2">${availableSlots} slots available</span>` : '<span class="badge bg-danger ms-2">Full</span>'}
                            <div class="mt-2">
                                ${studentsHTML}
                            </div>
                        </div>
                        <p><strong>Instructor 1:</strong> ${course.instructor1 ? course.instructor1.username : 'Not assigned'}</p>
                        <p><strong>Instructor 2:</strong> ${course.instructor2 ? course.instructor2.username : 'Not assigned'}</p>
                    </div>
                </div>
            `;
            
            // Set button URLs
            document.getElementById('viewCourseDetailsBtn').href = `/admin/schedule/view/${courseId}`;
            document.getElementById('editCourseBtn').href = `/admin/schedule/edit/${courseId}`;
        }
        
        modal.show();
    }

    /**
     * Format date for display
     */
    function formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }

    /**
     * Show notification message matching flash message component style
     */
    function showNotification(message, type = 'info') {
        // Create or get flash messages container
        let container = document.querySelector('.flash-messages-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'flash-messages-container';
            document.body.appendChild(container);
        }

        // Create flash message element
        const flashMessage = document.createElement('div');
        flashMessage.className = `flash-message flash-message--${type} flash-message--entering`;
        flashMessage.setAttribute('role', 'alert');
        flashMessage.setAttribute('aria-live', 'polite');

        // Determine icon based on type
        let iconSVG;
        switch(type) {
            case 'success':
                iconSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>';
                break;
            case 'error':
            case 'danger':
                iconSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>';
                break;
            case 'warning':
                iconSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg>';
                break;
            default: // info
                iconSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>';
        }

        flashMessage.innerHTML = `
            <div class="flash-message__content">
                <span class="flash-message__icon">
                    ${iconSVG}
                </span>
                <span class="flash-message__text">${message}</span>
                <button class="flash-message__close" aria-label="Close message" type="button">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                    </svg>
                </button>
            </div>
            <div class="flash-message__progress">
                <div class="flash-message__progress-bar"></div>
            </div>
        `;

        // Add to container
        container.appendChild(flashMessage);

        // Setup close button
        const closeBtn = flashMessage.querySelector('.flash-message__close');
        closeBtn.addEventListener('click', function() {
            dismissFlashMessage(flashMessage);
        });

        // Setup auto-dismiss with progress bar
        const progressBar = flashMessage.querySelector('.flash-message__progress-bar');
        const timeout = 5000; // 5 seconds

        // Animate progress bar
        setTimeout(() => {
            progressBar.style.transition = `transform ${timeout}ms linear`;
            progressBar.style.transform = 'scaleX(0)';
        }, 10);

        // Auto-dismiss
        const timeoutId = setTimeout(() => {
            dismissFlashMessage(flashMessage);
        }, timeout);

        // Pause on hover
        let isPaused = false;
        let remainingTime = timeout;
        let startTime = Date.now();

        flashMessage.addEventListener('mouseenter', function() {
            if (!isPaused) {
                clearTimeout(timeoutId);
                const elapsed = Date.now() - startTime;
                remainingTime = Math.max(0, timeout - elapsed);
                const currentTransform = window.getComputedStyle(progressBar).transform;
                progressBar.style.transition = 'none';
                progressBar.style.transform = currentTransform;
                isPaused = true;
            }
        });

        flashMessage.addEventListener('mouseleave', function() {
            if (isPaused) {
                startTime = Date.now();
                progressBar.style.transition = `transform ${remainingTime}ms linear`;
                progressBar.style.transform = 'scaleX(0)';
                setTimeout(() => {
                    dismissFlashMessage(flashMessage);
                }, remainingTime);
                isPaused = false;
            }
        });
    }

    /**
     * Dismiss flash message with animation
     */
    function dismissFlashMessage(messageElement) {
        messageElement.classList.add('flash-message--closing');
        setTimeout(() => {
            messageElement.remove();
            
            // Remove container if empty
            const container = document.querySelector('.flash-messages-container');
            if (container && container.querySelectorAll('.flash-message').length === 0) {
                container.remove();
            }
        }, 300);
    }

    /**
     * Handle form submission
     */
    document.getElementById('addCourseWizardForm').addEventListener('submit', function(e) {
        // Form will submit normally to server
        // Show loading state on submit button
        const submitBtn = document.getElementById('wizardSubmitBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
    });
});
