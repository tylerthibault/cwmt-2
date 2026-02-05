/**
 * Clock Picker Component
 * A circular time picker for selecting hours and minutes
 */

class ClockPicker {
    constructor(initialTime = '09:00') {
        this.selectedTime = initialTime;
        this.is24Hour = false;
        this.mode = 'hour'; // 'hour' or 'minute'
        
        const [hours, minutes] = initialTime.split(':');
        this.hours = parseInt(hours);
        this.minutes = parseInt(minutes);
        this.period = this.hours >= 12 ? 'PM' : 'AM';
        
        if (!this.is24Hour && this.hours > 12) {
            this.hours -= 12;
        } else if (!this.is24Hour && this.hours === 0) {
            this.hours = 12;
        }
    }
    
    render() {
        const container = document.createElement('div');
        container.className = 'clock-picker-container';
        
        container.innerHTML = `
            <div class="clock-picker">
                <div class="clock-display">
                    <div class="clock-time">
                        <span class="clock-hour ${this.mode === 'hour' ? 'active' : ''}" data-mode="hour">${String(this.hours).padStart(2, '0')}</span>
                        <span class="clock-separator">:</span>
                        <span class="clock-minute ${this.mode === 'minute' ? 'active' : ''}" data-mode="minute">${String(this.minutes).padStart(2, '0')}</span>
                        ${!this.is24Hour ? `
                            <div class="clock-period">
                                <button type="button" class="clock-period-btn ${this.period === 'AM' ? 'active' : ''}" data-period="AM">AM</button>
                                <button type="button" class="clock-period-btn ${this.period === 'PM' ? 'active' : ''}" data-period="PM">PM</button>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="clock-face">
                    <div class="clock-center"></div>
                    <div class="clock-hand"></div>
                    ${this.renderClockNumbers()}
                </div>
            </div>
        `;
        
        this.attachEventListeners(container);
        this.updateClock(container);
        
        return container;
    }
    
    renderClockNumbers() {
        const numbers = this.mode === 'hour' ? 
            (this.is24Hour ? Array.from({length: 24}, (_, i) => i) : Array.from({length: 12}, (_, i) => i === 0 ? 12 : i)) :
            Array.from({length: 12}, (_, i) => i * 5);
        
        return numbers.map((num, index) => {
            const angle = this.mode === 'hour' ? 
                (360 / numbers.length) * index - 90 :
                (360 / 12) * index - 90;
            const radius = 90; // pixels from center
            
            const x = Math.cos(angle * Math.PI / 180) * radius;
            const y = Math.sin(angle * Math.PI / 180) * radius;
            
            const isSelected = this.mode === 'hour' ? num === this.hours : num === this.minutes;
            
            return `
                <div class="clock-number ${isSelected ? 'selected' : ''}" 
                     style="transform: translate(${x}px, ${y}px)"
                     data-value="${num}">
                    ${num}
                </div>
            `;
        }).join('');
    }
    
    attachEventListeners(container) {
        // Mode switching (hour/minute)
        const hourDisplay = container.querySelector('.clock-hour');
        const minuteDisplay = container.querySelector('.clock-minute');
        
        hourDisplay?.addEventListener('click', () => {
            this.mode = 'hour';
            this.updateDisplay(container);
        });
        
        minuteDisplay?.addEventListener('click', () => {
            this.mode = 'minute';
            this.updateDisplay(container);
        });
        
        // Period switching (AM/PM)
        const periodButtons = container.querySelectorAll('.clock-period-btn');
        periodButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.period = e.target.dataset.period;
                this.updateDisplay(container);
            });
        });
        
        // Clock face clicking
        const clockNumbers = container.querySelectorAll('.clock-number');
        clockNumbers.forEach(num => {
            num.addEventListener('click', (e) => {
                const value = parseInt(e.target.dataset.value);
                if (this.mode === 'hour') {
                    this.hours = value;
                    this.mode = 'minute'; // Auto-switch to minutes
                } else {
                    this.minutes = value;
                }
                this.updateDisplay(container);
            });
        });
        
        // Clock face dragging
        const clockFace = container.querySelector('.clock-face');
        const handleClockInteraction = (e) => {
            const rect = clockFace.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const x = e.clientX - rect.left - centerX;
            const y = e.clientY - rect.top - centerY;
            
            let angle = Math.atan2(y, x) * 180 / Math.PI + 90;
            if (angle < 0) angle += 360;
            
            if (this.mode === 'hour') {
                const hourCount = this.is24Hour ? 24 : 12;
                let hour = Math.round(angle / (360 / hourCount));
                if (hour === 0 && !this.is24Hour) hour = 12;
                if (hour === 24) hour = 0;
                this.hours = hour;
            } else {
                const minute = Math.round(angle / (360 / 12)) * 5;
                this.minutes = minute === 60 ? 0 : minute;
            }
            
            this.updateDisplay(container);
        };
        
        clockFace.addEventListener('click', handleClockInteraction);
    }
    
    updateDisplay(container) {
        // Update time display
        const hourDisplay = container.querySelector('.clock-hour');
        const minuteDisplay = container.querySelector('.clock-minute');
        
        hourDisplay.textContent = String(this.hours).padStart(2, '0');
        minuteDisplay.textContent = String(this.minutes).padStart(2, '0');
        
        hourDisplay.classList.toggle('active', this.mode === 'hour');
        minuteDisplay.classList.toggle('active', this.mode === 'minute');
        
        // Update period buttons
        const periodButtons = container.querySelectorAll('.clock-period-btn');
        periodButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.period === this.period);
        });
        
        // Re-render clock face
        const clockFace = container.querySelector('.clock-face');
        const numbersHtml = this.renderClockNumbers();
        
        // Replace only the numbers, keep hand and center
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = numbersHtml;
        
        const existingNumbers = clockFace.querySelectorAll('.clock-number');
        existingNumbers.forEach(num => num.remove());
        
        while (tempDiv.firstChild) {
            clockFace.appendChild(tempDiv.firstChild);
        }
        
        // Re-attach number listeners
        const clockNumbers = clockFace.querySelectorAll('.clock-number');
        clockNumbers.forEach(num => {
            num.addEventListener('click', (e) => {
                const value = parseInt(e.target.dataset.value);
                if (this.mode === 'hour') {
                    this.hours = value;
                    this.mode = 'minute';
                } else {
                    this.minutes = value;
                }
                this.updateDisplay(container);
            });
        });
        
        this.updateClock(container);
    }
    
    updateClock(container) {
        const hand = container.querySelector('.clock-hand');
        
        const value = this.mode === 'hour' ? this.hours : this.minutes;
        const max = this.mode === 'hour' ? (this.is24Hour ? 24 : 12) : 60;
        const step = this.mode === 'hour' ? 1 : 5;
        
        const angle = (value / max) * 360;
        hand.style.transform = `rotate(${angle}deg)`;
    }
    
    getValue() {
        let hours = this.hours;
        
        if (!this.is24Hour) {
            if (this.period === 'PM' && hours !== 12) {
                hours += 12;
            } else if (this.period === 'AM' && hours === 12) {
                hours = 0;
            }
        }
        
        return `${String(hours).padStart(2, '0')}:${String(this.minutes).padStart(2, '0')}`;
    }
}
