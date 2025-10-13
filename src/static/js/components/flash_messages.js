/**
 * Flash Messages Component
 * Handles auto-dismissal with visual progress indicator and hover pause functionality
 * Messages stack like cards - only the top message timer is active
 */

(function() {
    'use strict';

    // Configuration
    const FLASH_CONFIG = {
        defaultTimeout: 5000, // 5 seconds
        animationDuration: 300 // matches CSS animation duration
    };

    // Queue management
    let messageQueue = [];
    let activeMessage = null;

    /**
     * Initialize flash message handlers
     */
    function initFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');
        
        // Add entering animation to all messages
        flashMessages.forEach(function(message) {
            message.classList.add('flash-message--entering');
            messageQueue.push(message);
        });

        // Start processing the queue
        processQueue();
    }

    /**
     * Process the message queue - activate the first message
     */
    function processQueue() {
        // If there's already an active message or queue is empty, do nothing
        if (activeMessage || messageQueue.length === 0) {
            return;
        }

        // Get the first message in the queue
        activeMessage = messageQueue[0];
        
        // Setup the active message with timer and interactions
        setupFlashMessage(activeMessage);
    }

    /**
     * Setup individual flash message with timeout and interactions
     * @param {HTMLElement} message - Flash message element
     */
    function setupFlashMessage(message) {
        const progressBar = message.querySelector('.flash-message__progress-bar');
        const closeButton = message.querySelector('.flash-message__close');
        
        let timeoutId = null;
        let startTime = null;
        let remainingTime = FLASH_CONFIG.defaultTimeout;
        let isPaused = false;

        // Start the auto-dismiss timer
        startTimer();

        // Close button handler
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                dismissMessage(message);
            });
        }

        // Pause on hover
        message.addEventListener('mouseenter', function() {
            pauseTimer();
        });

        // Resume on mouse leave
        message.addEventListener('mouseleave', function() {
            resumeTimer();
        });

        /**
         * Start the countdown timer
         */
        function startTimer() {
            startTime = Date.now();
            isPaused = false;
            
            // Set progress bar animation
            if (progressBar) {
                // Reset to full width first
                progressBar.style.transition = 'none';
                progressBar.style.transform = 'scaleX(1)';
                
                // Force reflow to ensure the browser registers the initial state
                progressBar.offsetHeight;
                
                // Now animate to zero
                progressBar.style.transition = `transform ${remainingTime}ms linear`;
                progressBar.style.transform = 'scaleX(0)';
            }

            // Set timeout for auto-dismiss
            timeoutId = setTimeout(function() {
                dismissMessage(message);
            }, remainingTime);
        }

        /**
         * Pause the countdown timer
         */
        function pauseTimer() {
            if (isPaused || !timeoutId) {
                return;
            }

            // Clear the timeout
            clearTimeout(timeoutId);
            
            // Calculate remaining time
            const elapsed = Date.now() - startTime;
            remainingTime = Math.max(0, remainingTime - elapsed);
            
            // Pause the progress bar animation
            if (progressBar) {
                const computedStyle = window.getComputedStyle(progressBar);
                const currentTransform = computedStyle.transform;
                progressBar.style.transition = 'none';
                progressBar.style.transform = currentTransform;
            }

            isPaused = true;
            message.classList.add('flash-message--paused');
        }

        /**
         * Resume the countdown timer
         */
        function resumeTimer() {
            if (!isPaused) {
                return;
            }

            message.classList.remove('flash-message--paused');
            startTimer();
        }

        /**
         * Dismiss the flash message
         * @param {HTMLElement} messageElement - Message to dismiss
         */
        function dismissMessage(messageElement) {
            // Clear any existing timeout
            if (timeoutId) {
                clearTimeout(timeoutId);
            }

            // Add closing animation class
            messageElement.classList.add('flash-message--closing');

            // Remove from DOM after animation
            setTimeout(function() {
                messageElement.remove();
                
                // Remove from queue
                const index = messageQueue.indexOf(messageElement);
                if (index > -1) {
                    messageQueue.splice(index, 1);
                }
                
                // Clear active message
                if (activeMessage === messageElement) {
                    activeMessage = null;
                }
                
                // Process next message in queue
                processQueue();
                
                // Remove container if no more messages
                const container = document.querySelector('.flash-messages-container');
                if (container && container.querySelectorAll('.flash-message').length === 0) {
                    container.remove();
                }
            }, FLASH_CONFIG.animationDuration);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFlashMessages);
    } else {
        initFlashMessages();
    }

})();
