/**
 * Calendar Core Module
 * Handles calendar rendering, navigation, and day cell creation
 */

class CalendarCore {
    constructor(config) {
        this.role = config.role;
        this.currentUserId = config.currentUserId;
        this.currentInstructorId = config.currentInstructorId;
        this.events = config.events || [];
        this.currentDate = new Date();
    }

    /**
     * Initialize calendar and set up event listeners
     */
    init() {
        this.renderCalendar(this.currentDate.getFullYear(), this.currentDate.getMonth());
        this.setupNavigation();
    }

    /**
     * Set up month navigation buttons
     */
    setupNavigation() {
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar(this.currentDate.getFullYear(), this.currentDate.getMonth());
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar(this.currentDate.getFullYear(), this.currentDate.getMonth());
        });
    }

    /**
     * Render the calendar for a given year and month
     */
    renderCalendar(year, month) {
        const calendar = document.getElementById('calendar');
        const monthName = new Date(year, month).toLocaleDateString('en-US', { 
            month: 'long', 
            year: 'numeric' 
        });
        document.getElementById('currentMonth').textContent = monthName;

        // Remove existing day cells
        const dayCells = calendar.querySelectorAll('.calendar-day');
        dayCells.forEach(cell => cell.remove());

        // Get first day of month and number of days
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const daysInPrevMonth = new Date(year, month, 0).getDate();

        // Create array to store all day cells
        const dayCellsArray = [];

        // Add previous month days
        for (let i = firstDay - 1; i >= 0; i--) {
            const dayDiv = this.createDayCell(daysInPrevMonth - i, true);
            calendar.appendChild(dayDiv);
            dayCellsArray.push({ 
                div: dayDiv, 
                date: new Date(year, month - 1, daysInPrevMonth - i) 
            });
        }

        // Add current month days
        for (let day = 1; day <= daysInMonth; day++) {
            const dayDiv = this.createDayCell(day, false);
            const date = new Date(year, month, day);
            calendar.appendChild(dayDiv);
            dayCellsArray.push({ div: dayDiv, date: date });
        }

        // Add next month days
        const totalCells = calendar.children.length - 7; // Subtract header cells
        const remainingCells = 42 - totalCells; // 6 weeks
        for (let day = 1; day <= remainingCells; day++) {
            const dayDiv = this.createDayCell(day, true);
            calendar.appendChild(dayDiv);
            dayCellsArray.push({ 
                div: dayDiv, 
                date: new Date(year, month + 1, day) 
            });
        }

        // Render events using the event renderer
        if (window.CalendarEvents) {
            const eventRenderer = new window.CalendarEvents(
                this.events, 
                this.role, 
                this.currentInstructorId
            );
            eventRenderer.renderSpanningEvents(dayCellsArray);
        }
    }

    /**
     * Create a single day cell
     */
    createDayCell(day, isOtherMonth) {
        const dayDiv = document.createElement('div');
        dayDiv.className = 'calendar-day' + (isOtherMonth ? ' other-month' : '');

        // Mark today's date
        if (!isOtherMonth) {
            const today = new Date();
            const cellDate = new Date(
                this.currentDate.getFullYear(), 
                this.currentDate.getMonth(), 
                day
            );
            if (cellDate.getDate() === today.getDate() && 
                cellDate.getMonth() === today.getMonth() && 
                cellDate.getFullYear() === today.getFullYear()) {
                dayDiv.classList.add('today');
            }
        }

        const dayNumber = document.createElement('div');
        dayNumber.className = 'day-number';
        dayNumber.textContent = day;
        dayDiv.appendChild(dayNumber);

        // Only admins can click days to create courses
        if (this.role === 'admin') {
            dayDiv.classList.add('clickable');
            dayDiv.addEventListener('click', (e) => {
                if (e.target === dayDiv || e.target === dayNumber) {
                    const clickedDate = this.getDateForDayCell(dayDiv, day, isOtherMonth);
                    if (window.CalendarAdmin) {
                        window.CalendarAdmin.openScheduleWizard(clickedDate);
                    }
                }
            });
        }

        return dayDiv;
    }

    /**
     * Get the actual date for a day cell
     */
    getDateForDayCell(dayDiv, day, isOtherMonth) {
        const calendar = document.getElementById('calendar');
        const allDays = Array.from(calendar.querySelectorAll('.calendar-day'));
        const dayIndex = allDays.indexOf(dayDiv);

        if (isOtherMonth) {
            if (dayIndex < 7) {
                return new Date(
                    this.currentDate.getFullYear(), 
                    this.currentDate.getMonth() - 1, 
                    day
                );
            } else {
                return new Date(
                    this.currentDate.getFullYear(), 
                    this.currentDate.getMonth() + 1, 
                    day
                );
            }
        } else {
            return new Date(
                this.currentDate.getFullYear(), 
                this.currentDate.getMonth(), 
                day
            );
        }
    }
}

// Export to window for use in other modules
window.CalendarCore = CalendarCore;
