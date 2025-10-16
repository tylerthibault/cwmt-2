/**
 * Schedule Management JavaScript
 * Handles calendar interaction and course instance creation
 */

document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    let calendar;
    let selectedTemplate = null;

    // Initialize FullCalendar
    if (calendarEl) {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            selectable: true,
            selectMirror: true,
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
     * Handle clicking on calendar date
     */
    function handleDateClick(info) {
        if (selectedTemplate) {
            openAddCourseModal(info.dateStr);
        } else {
            alert('Please select a course template from the sidebar first.');
        }
    }

    /**
     * Handle clicking on existing event
     */
    function handleEventClick(info) {
        const courseId = info.event.extendedProps.courseId;
        showCourseDetails(courseId);
    }

    /**
     * Add to calendar button click handlers
     */
    document.querySelectorAll('.add-to-calendar-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update selected template
            selectedTemplate = {
                id: this.dataset.templateId,
                name: this.dataset.templateName,
                duration: parseInt(this.dataset.duration)
            };

            // Highlight selected template card
            document.querySelectorAll('.template-card').forEach(card => {
                card.classList.remove('selected');
            });
            this.closest('.template-card').classList.add('selected');

            // Show instruction
            showNotification('Now click on the calendar to select a date for this course.', 'info');
        });
    });

    /**
     * Open modal to add course instance
     */
    function openAddCourseModal(dateStr) {
        if (!selectedTemplate) return;

        const modal = new bootstrap.Modal(document.getElementById('addCourseModal'));
        
        // Populate modal fields
        document.getElementById('modalTemplateId').value = selectedTemplate.id;
        document.getElementById('modalCourseName').value = selectedTemplate.name;
        document.getElementById('modalDuration').value = selectedTemplate.duration + ' day' + (selectedTemplate.duration > 1 ? 's' : '');
        document.getElementById('courseDate').value = dateStr;
        document.getElementById('durationDisplay').textContent = selectedTemplate.duration + ' day' + (selectedTemplate.duration > 1 ? 's' : '');

        modal.show();
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
                        <p><strong>Student:</strong> ${course.student ? course.student.username : 'Not assigned'}</p>
                        <p><strong>Instructor 1:</strong> ${course.instructor1 ? course.instructor1.username : 'Not assigned'}</p>
                        <p><strong>Instructor 2:</strong> ${course.instructor2 ? course.instructor2.username : 'Not assigned'}</p>
                    </div>
                </div>
            `;
            
            // Set edit button URL
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
     * Show notification message
     */
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * Handle form submission
     */
    const addCourseForm = document.getElementById('addCourseForm');
    if (addCourseForm) {
        addCourseForm.addEventListener('submit', function(e) {
            // Form will submit normally, no need to prevent default
            // The server will handle the creation and redirect
        });
    }

    /**
     * Reset template selection when modal is closed
     */
    document.getElementById('addCourseModal')?.addEventListener('hidden.bs.modal', function() {
        // Don't reset selection, keep it for multiple additions
        // selectedTemplate = null;
        // document.querySelectorAll('.template-card').forEach(card => {
        //     card.classList.remove('selected');
        // });
    });
});
