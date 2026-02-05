/**
 * Core Calendar Component
 * Handles month rendering, navigation, and event display
 * Can be extended by role-specific modules (admin, student, instructor)
 */

class Calendar {
    constructor(options = {}) {
        this.events = options.events || window.calendarEvents || [];
        this.role = options.role || window.calendarRole || 'public';
        this.currentDate = new Date();
        this.selectedDate = null;
        
        // DOM elements
        this.gridElement = document.getElementById('calendarGrid');
        this.mobileListElement = document.getElementById('mobileEventsList');
        this.monthYearElement = document.getElementById('monthYear');
        this.prevButton = document.getElementById('prevMonth');
        this.nextButton = document.getElementById('nextMonth');
        
        // Event handlers
        this.onDayClick = options.onDayClick || null;
        this.onEventClick = options.onEventClick || null;
        
        this.init();
    }
    
    init() {
        if (!this.gridElement && !this.mobileListElement) {
            console.error('Calendar elements not found');
            return;
        }
        
        console.log('Calendar initialized with', this.events.length, 'events');
        console.log('Grid element:', this.gridElement);
        console.log('Mobile list element:', this.mobileListElement);
        
        // Setup navigation
        if (this.prevButton) {
            this.prevButton.addEventListener('click', () => this.previousMonth());
        }
        if (this.nextButton) {
            this.nextButton.addEventListener('click', () => this.nextMonth());
        }
        
        // Initial render
        this.render();
    }
    
    // Helper function to parse date strings as local dates (not UTC)
    parseLocalDate(dateString) {
        // Parse date string as YYYY-MM-DD and create a local date object
        const parts = dateString.split('T')[0].split('-');
        return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
    }
    
    render() {
        this.updateMonthYear();
        this.renderDesktopCalendar();
        this.renderMobileList();
    }
    
    updateMonthYear() {
        if (!this.monthYearElement) return;
        
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        
        const month = monthNames[this.currentDate.getMonth()];
        const year = this.currentDate.getFullYear();
        
        this.monthYearElement.textContent = `${month} ${year}`;
    }
    
    renderDesktopCalendar() {
        if (!this.gridElement) return;
        
        this.gridElement.innerHTML = '';
        
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Get first day of month and number of days
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();
        
        // Get previous month days
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        
        // Calculate total cells needed (6 weeks max)
        const totalCells = 42;
        
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // Render calendar cells
        for (let i = 0; i < totalCells; i++) {
            const dayCell = document.createElement('div');
            dayCell.classList.add('calendar-day');
            
            let dayNumber;
            let cellDate;
            let isCurrentMonth = false;
            
            if (i < startingDayOfWeek) {
                // Previous month days
                dayNumber = prevMonthLastDay - (startingDayOfWeek - i - 1);
                cellDate = new Date(year, month - 1, dayNumber);
                dayCell.classList.add('other-month');
            } else if (i >= startingDayOfWeek + daysInMonth) {
                // Next month days
                dayNumber = i - (startingDayOfWeek + daysInMonth) + 1;
                cellDate = new Date(year, month + 1, dayNumber);
                dayCell.classList.add('other-month');
            } else {
                // Current month days
                dayNumber = i - startingDayOfWeek + 1;
                cellDate = new Date(year, month, dayNumber);
                isCurrentMonth = true;
            }
            
            // Check if today
            if (cellDate.getTime() === today.getTime()) {
                dayCell.classList.add('today');
            }
            
            // Add day number
            const dayNumberElement = document.createElement('div');
            dayNumberElement.classList.add('calendar-day-number');
            dayNumberElement.textContent = dayNumber;
            dayCell.appendChild(dayNumberElement);
            
            // Add events for this day
            const dayEvents = this.getEventsForDate(cellDate);
            
            if (dayEvents.length > 0) {
                const eventsContainer = document.createElement('div');
                eventsContainer.classList.add('calendar-events');
                
                // Show max 3 events, then "+X more"
                const maxVisible = 3;
                const visibleEvents = dayEvents.slice(0, maxVisible);
                
                visibleEvents.forEach(event => {
                    const eventElement = this.createEventElement(event, cellDate);
                    eventsContainer.appendChild(eventElement);
                });
                
                if (dayEvents.length > 3) {
                    const moreElement = document.createElement('div');
                    moreElement.classList.add('calendar-event-more');
                    moreElement.textContent = `+${dayEvents.length - 3} more`;
                    moreElement.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.showAllEventsForDay(cellDate, dayEvents);
                    });
                    eventsContainer.appendChild(moreElement);
                }
                
                dayCell.appendChild(eventsContainer);
            }
            
            // Add click handler for day cell
            dayCell.addEventListener('click', () => {
                this.handleDayClick(cellDate, dayEvents);
            });
            
            this.gridElement.appendChild(dayCell);
        }
    }
    
    renderMobileList() {
        if (!this.mobileListElement) return;
        
        this.mobileListElement.innerHTML = '';
        
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Get all events for current month
        const monthEvents = this.events.filter(event => {
            const eventDate = this.parseLocalDate(event.start);
            return eventDate.getFullYear() === year && eventDate.getMonth() === month;
        });
        
        // Sort by date
        monthEvents.sort((a, b) => this.parseLocalDate(a.start) - this.parseLocalDate(b.start));
        
        if (monthEvents.length === 0) {
            const emptyState = document.createElement('div');
            emptyState.classList.add('calendar-empty');
            emptyState.innerHTML = `
                <i class="bi bi-calendar-x"></i>
                <p>No courses scheduled for this month</p>
            `;
            this.mobileListElement.appendChild(emptyState);
            return;
        }
        
        monthEvents.forEach(event => {
            const card = this.createMobileEventCard(event);
            this.mobileListElement.appendChild(card);
        });
    }
    
    createEventElement(event, cellDate) {
        const eventElement = document.createElement('div');
        eventElement.classList.add('calendar-event');
        eventElement.style.backgroundColor = event.color || '#0d6efd';
        
        // Set title attribute for tooltip on hover
        const eventStart = this.parseLocalDate(event.start);
        const duration = event.duration || 1;
        const spotsLeft = event.maxStudents - event.enrollmentCount;
        const spotsText = spotsLeft > 0 ? `${spotsLeft} spots left` : 'Full';
        
        eventElement.title = `${event.title} - ${spotsText}`;
        
        // Add text content for desktop/tablet view
        const eventText = document.createElement('span');
        eventText.classList.add('calendar-event-text');
        eventText.textContent = event.title;
        eventElement.appendChild(eventText);
        
        // Add status classes for styling
        if (spotsLeft === 0) {
            eventElement.classList.add('full');
        } else if (spotsLeft <= 3) {
            eventElement.classList.add('limited');
        }
        
        // Add enrolled class if applicable
        if (this.isUserEnrolled(event)) {
            eventElement.classList.add('enrolled');
        }
        
        eventElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.handleEventClick(event);
        });
        
        return eventElement;
    }
    
    createMobileEventCard(event) {
        const card = document.createElement('div');
        card.classList.add('calendar-event-card');
        card.style.borderLeftColor = event.color || '#0d6efd';
        
        if (this.isUserEnrolled(event)) {
            card.classList.add('enrolled');
        }
        
        const eventDate = this.parseLocalDate(event.start);
        const dateStr = eventDate.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const spotsLeft = event.maxStudents - event.enrollmentCount;
        const spotsText = spotsLeft > 0 ? `${spotsLeft} spots available` : 'Full';
        
        card.innerHTML = `
            <div class="calendar-event-card-date">${dateStr}</div>
            <div class="calendar-event-card-title">${event.title}</div>
            <div class="calendar-event-card-details">
                ${event.startTime ? `
                    <div class="calendar-event-card-detail">
                        <i class="bi bi-clock"></i>
                        <span>${event.startTime}</span>
                    </div>
                ` : ''}
                ${event.location ? `
                    <div class="calendar-event-card-detail">
                        <i class="bi bi-geo-alt"></i>
                        <span>${event.location}</span>
                    </div>
                ` : ''}
                ${event.instructorText ? `
                    <div class="calendar-event-card-detail">
                        <i class="bi bi-person"></i>
                        <span>${event.instructorText}</span>
                    </div>
                ` : ''}
                <div class="calendar-event-card-detail">
                    <i class="bi bi-people"></i>
                    <span>${spotsText} (${event.enrollmentCount}/${event.maxStudents})</span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            this.handleEventClick(event);
        });
        
        return card;
    }
    
    getEventsForDate(date) {
        const normalizedDate = new Date(date);
        normalizedDate.setHours(0, 0, 0, 0);
        
        return this.events.filter(event => {
            const eventStart = this.parseLocalDate(event.start);
            
            const duration = event.duration || 1;
            const eventEnd = new Date(eventStart);
            eventEnd.setDate(eventEnd.getDate() + duration - 1);
            
            // Include events only if this date is between start and end (inclusive)
            return normalizedDate >= eventStart && normalizedDate <= eventEnd;
        });
    }
    
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    handleDayClick(date, events) {
        this.selectedDate = date;
        
        if (this.onDayClick) {
            this.onDayClick(date, events);
        }
    }
    
    handleEventClick(event) {
        if (this.onEventClick) {
            this.onEventClick(event);
        }
    }
    
    showAllEventsForDay(date, events) {
        // This will be implemented by role-specific modules
        // or use Modal.show() to display all events
        if (this.onDayClick) {
            this.onDayClick(date, events);
        }
    }
    
    isUserEnrolled(event) {
        // Check if user is enrolled - will be overridden by student calendar
        if (window.enrolledCourseIds && Array.isArray(window.enrolledCourseIds)) {
            return window.enrolledCourseIds.includes(event.id);
        }
        return false;
    }
    
    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.render();
    }
    
    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.render();
    }
    
    refresh(newEvents) {
        if (newEvents) {
            this.events = newEvents;
        }
        this.render();
    }
}

// Export for use in other modules
window.Calendar = Calendar;
