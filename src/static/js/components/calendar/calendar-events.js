/**
 * Calendar Events Module
 * Handles event rendering, positioning, and display logic
 */

class CalendarEvents {
    constructor(events, role, currentInstructorId) {
        this.events = events;
        this.role = role;
        this.currentInstructorId = currentInstructorId;
    }

    /**
     * Generate a color for each course template based on its ID
     */
    getCourseColor(courseTemplateId) {
        const colors = [
            '#0d6efd', // Blue
            '#198754', // Green
            '#dc3545', // Red
            '#fd7e14', // Orange
            '#6f42c1', // Purple
            '#20c997', // Teal
            '#d63384', // Pink
            '#0dcaf0', // Cyan
            '#ffc107', // Yellow
            '#6c757d', // Gray
        ];

        return colors[courseTemplateId % colors.length];
    }

    /**
     * Check if color needs dark text for readability based on luminance
     */
    needsDarkText(hexColor) {
        const hex = hexColor.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16) / 255;
        const g = parseInt(hex.substr(2, 2), 16) / 255;
        const b = parseInt(hex.substr(4, 2), 16) / 255;

        const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        return luminance > 0.5;
    }

    /**
     * Parse ISO date strings in local timezone to avoid UTC conversion issues
     */
    parseLocalDate(isoString) {
        const [year, month, day] = isoString.split('T')[0].split('-').map(Number);
        return new Date(year, month - 1, day);
    }

    /**
     * Render all spanning events on the calendar
     */
    renderSpanningEvents(dayCellsArray) {
        const renderedEvents = new Set();
        const cellEventPositions = new Map();

        this.events.forEach(event => {
            if (!event.start || renderedEvents.has(event.id)) return;

            const eventStart = this.parseLocalDate(event.start);
            const eventEnd = event.end ? this.parseLocalDate(event.end) : eventStart;

            // Find all days this event spans
            const eventDays = dayCellsArray.filter(cell => {
                const cellDate = new Date(
                    cell.date.getFullYear(), 
                    cell.date.getMonth(), 
                    cell.date.getDate()
                );
                const startDate = new Date(
                    eventStart.getFullYear(), 
                    eventStart.getMonth(), 
                    eventStart.getDate()
                );
                const endDate = new Date(
                    eventEnd.getFullYear(), 
                    eventEnd.getMonth(), 
                    eventEnd.getDate()
                );
                return cellDate >= startDate && cellDate <= endDate;
            });

            if (eventDays.length === 0) return;

            // Find the first available vertical position
            let eventLayer = 0;
            let foundAvailableLayer = false;
            while (!foundAvailableLayer) {
                foundAvailableLayer = true;
                for (const dayCell of eventDays) {
                    const cellIndex = dayCellsArray.indexOf(dayCell);
                    if (!cellEventPositions.has(cellIndex)) {
                        cellEventPositions.set(cellIndex, new Set());
                    }
                    if (cellEventPositions.get(cellIndex).has(eventLayer)) {
                        foundAvailableLayer = false;
                        eventLayer++;
                        break;
                    }
                }
            }

            // Mark this layer as used for all days
            for (const dayCell of eventDays) {
                const cellIndex = dayCellsArray.indexOf(dayCell);
                cellEventPositions.get(cellIndex).add(eventLayer);
            }

            // Group consecutive days by week rows
            let currentRow = [];
            let currentRowStart = Math.floor(dayCellsArray.indexOf(eventDays[0]) / 7);

            eventDays.forEach((dayCell, index) => {
                const dayIndex = dayCellsArray.indexOf(dayCell);
                const rowIndex = Math.floor(dayIndex / 7);

                if (rowIndex !== currentRowStart) {
                    if (currentRow.length > 0) {
                        this.renderEventSpan(currentRow, event, index === 0, false, eventLayer);
                    }
                    currentRow = [dayCell];
                    currentRowStart = rowIndex;
                } else {
                    currentRow.push(dayCell);
                }
            });

            // Render last row
            if (currentRow.length > 0) {
                this.renderEventSpan(
                    currentRow, 
                    event, 
                    currentRow[0] === eventDays[0], 
                    true, 
                    eventLayer
                );
            }

            renderedEvents.add(event.id);
        });
    }

    /**
     * Render a single event span across one or more day cells
     */
    renderEventSpan(dayCells, event, isStart, isEnd, layer = 0) {
        const firstCell = dayCells[0].div;
        const spanCount = dayCells.length;

        const eventDiv = document.createElement('div');
        eventDiv.className = `calendar-event spanning status-${event.status}`;

        // Apply course-specific color
        const courseColor = event.color || 
            (event.course_template_id ? this.getCourseColor(event.course_template_id) : '#0d6efd');
        eventDiv.style.backgroundColor = courseColor;
        if (this.needsDarkText(courseColor)) {
            eventDiv.style.color = '#000';
        }

        // Add position classes
        if (isStart && isEnd && spanCount === 1) {
            eventDiv.classList.add('event-single');
        } else if (isStart) {
            eventDiv.classList.add('event-start');
        } else if (isEnd) {
            eventDiv.classList.add('event-end');
        } else {
            eventDiv.classList.add('event-middle');
        }

        // Highlight courses for instructors
        if (this.role === 'instructor' && this.currentInstructorId) {
            if (event.c1_instructor_id === this.currentInstructorId) {
                eventDiv.classList.add('my-course');
                eventDiv.setAttribute('data-instructor-role', 'C1');
            } else if (event.c2_instructor_id === this.currentInstructorId) {
                eventDiv.classList.add('my-course');
                eventDiv.setAttribute('data-instructor-role', 'C2');
            }
        }

        // For admin view, show which instructor slots are filled
        if (this.role === 'admin') {
            const slots = [];
            if (event.c1_instructor_id) slots.push('C1');
            if (event.c2_instructor_id) slots.push('C2');
            if (slots.length > 0) {
                eventDiv.classList.add('has-instructors');
                eventDiv.setAttribute('data-instructor-slots', slots.join(' '));
            }
        }

        eventDiv.textContent = event.title;
        eventDiv.title = `${event.title}\n${event.location}\n${event.enrollment} enrolled`;
        eventDiv.onclick = (e) => {
            e.stopPropagation();
            this.showEventDetails(event);
        };

        // Position the event
        const gap = 1;
        eventDiv.style.width = `calc(${spanCount * 100}% + ${(spanCount - 1) * gap}px)`;
        eventDiv.style.top = `${30 + (layer * 28)}px`;

        firstCell.appendChild(eventDiv);
    }

    /**
     * Show event details modal
     */
    showEventDetails(event) {
        if (this.role === 'admin' && window.CalendarAdmin) {
            window.CalendarAdmin.showEventDetails(event);
        } else if (this.role === 'instructor' && window.CalendarInstructor) {
            window.CalendarInstructor.showEventDetails(event);
        } else if (this.role === 'student' && window.CalendarStudent) {
            window.CalendarStudent.showEventDetails(event);
        } else {
            // Default view for public users
            this.showDefaultEventDetails(event);
        }
    }

    /**
     * Show default event details for public users
     */
    showDefaultEventDetails(event) {
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
            <button type="button" class="btn btn-primary" id="signup-btn">Sign Up</button>
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
                modal.close();
                // Trigger the same signup modal as the enroll button
                if (typeof showSignupModal === 'function') {
                    showSignupModal(event.id, event.title);
                } else {
                    console.error('showSignupModal function not found');
                }
            });
        }
    }
}

// Export to window for use in other modules
window.CalendarEvents = CalendarEvents;
