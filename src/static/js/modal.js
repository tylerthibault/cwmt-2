/**
 * Universal Modal System
 * A flexible, reusable modal system for displaying content overlays
 */

class Modal {
    constructor(options = {}) {
        this.options = {
            size: options.size || 'md', // sm, md, lg, xl, full
            title: options.title || '',
            content: options.content || '',
            footer: options.footer || null,
            closeOnOverlay: options.closeOnOverlay !== false,
            closeOnEscape: options.closeOnEscape !== false,
            onOpen: options.onOpen || null,
            onClose: options.onClose || null,
            className: options.className || ''
        };
        
        this.isOpen = false;
        this.overlay = null;
        this.container = null;
        
        this.init();
    }
    
    init() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-overlay';
        
        // Create container
        this.container = document.createElement('div');
        this.container.className = `modal-container modal-${this.options.size}`;
        if (this.options.className) {
            this.container.classList.add(this.options.className);
        }
        
        this.overlay.appendChild(this.container);
        document.body.appendChild(this.overlay);
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Close on overlay click
        if (this.options.closeOnOverlay) {
            this.overlay.addEventListener('click', (e) => {
                if (e.target === this.overlay) {
                    this.close();
                }
            });
        }
        
        // Close on escape key
        if (this.options.closeOnEscape) {
            this.escapeHandler = (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            };
            document.addEventListener('keydown', this.escapeHandler);
        }
    }
    
    setTitle(title) {
        this.options.title = title;
        if (this.isOpen) {
            const titleElement = this.container.querySelector('.modal-title');
            if (titleElement) {
                titleElement.textContent = title;
            }
        }
        return this;
    }
    
    setContent(content) {
        this.options.content = content;
        if (this.isOpen) {
            const bodyElement = this.container.querySelector('.modal-body');
            if (bodyElement) {
                if (typeof content === 'string') {
                    bodyElement.innerHTML = content;
                } else {
                    bodyElement.innerHTML = '';
                    bodyElement.appendChild(content);
                }
            }
        }
        return this;
    }
    
    setFooter(footer) {
        this.options.footer = footer;
        if (this.isOpen) {
            this.renderFooter();
        }
        return this;
    }
    
    showLoading() {
        const body = this.container.querySelector('.modal-body');
        if (body) {
            body.innerHTML = '<div class="modal-loading"><div class="modal-spinner"></div></div>';
        }
        return this;
    }
    
    render() {
        // Render header
        const header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = `
            <h3 class="modal-title">${this.options.title}</h3>
            <button type="button" class="modal-close" aria-label="Close">&times;</button>
        `;
        
        const closeBtn = header.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => this.close());
        
        // Render body
        const body = document.createElement('div');
        body.className = 'modal-body';
        if (typeof this.options.content === 'string') {
            body.innerHTML = this.options.content;
        } else {
            body.appendChild(this.options.content);
        }
        
        // Clear container
        this.container.innerHTML = '';
        this.container.appendChild(header);
        this.container.appendChild(body);
        
        // Render footer if provided
        if (this.options.footer) {
            this.renderFooter();
        }
    }
    
    renderFooter() {
        // Remove existing footer
        const existingFooter = this.container.querySelector('.modal-footer');
        if (existingFooter) {
            existingFooter.remove();
        }
        
        // Add new footer if content provided
        if (this.options.footer) {
            const footer = document.createElement('div');
            footer.className = 'modal-footer';
            if (typeof this.options.footer === 'string') {
                footer.innerHTML = this.options.footer;
            } else {
                footer.appendChild(this.options.footer);
            }
            this.container.appendChild(footer);
        }
    }
    
    open() {
        if (this.isOpen) return this;
        
        this.render();
        this.isOpen = true;
        
        // Trigger animation
        requestAnimationFrame(() => {
            this.overlay.classList.add('active');
        });
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Call onOpen callback
        if (typeof this.options.onOpen === 'function') {
            this.options.onOpen(this);
        }
        
        return this;
    }
    
    close() {
        if (!this.isOpen) return this;
        
        this.overlay.classList.remove('active');
        this.isOpen = false;
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Call onClose callback
        if (typeof this.options.onClose === 'function') {
            this.options.onClose(this);
        }
        
        return this;
    }
    
    destroy() {
        this.close();
        
        // Remove event listeners
        if (this.escapeHandler) {
            document.removeEventListener('keydown', this.escapeHandler);
        }
        
        // Remove from DOM
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
        }
    }
    
    // Static method to create and open a modal in one call
    static show(options) {
        const modal = new Modal(options);
        modal.open();
        return modal;
    }
    
    // Static method to create a confirmation dialog
    static confirm(options) {
        const confirmOptions = {
            size: options.size || 'sm',
            title: options.title || 'Confirm',
            content: options.message || 'Are you sure?',
            footer: `
                <button type="button" class="btn btn-secondary modal-cancel-btn">Cancel</button>
                <button type="button" class="btn btn-primary modal-confirm-btn">${options.confirmText || 'Confirm'}</button>
            `,
            ...options
        };
        
        const modal = new Modal(confirmOptions);
        modal.open();
        
        // Return a promise
        return new Promise((resolve) => {
            const confirmBtn = modal.container.querySelector('.modal-confirm-btn');
            const cancelBtn = modal.container.querySelector('.modal-cancel-btn');
            
            confirmBtn.addEventListener('click', () => {
                modal.close();
                modal.destroy();
                resolve(true);
            });
            
            cancelBtn.addEventListener('click', () => {
                modal.close();
                modal.destroy();
                resolve(false);
            });
            
            // Also resolve false on close
            const originalOnClose = modal.options.onClose;
            modal.options.onClose = () => {
                if (originalOnClose) originalOnClose(modal);
                resolve(false);
            };
        });
    }
    
    // Static method to create an alert dialog
    static alert(options) {
        const alertOptions = {
            size: options.size || 'sm',
            title: options.title || 'Alert',
            content: options.message || '',
            footer: `
                <button type="button" class="btn btn-primary modal-ok-btn">OK</button>
            `,
            ...options
        };
        
        const modal = new Modal(alertOptions);
        modal.open();
        
        return new Promise((resolve) => {
            const okBtn = modal.container.querySelector('.modal-ok-btn');
            
            okBtn.addEventListener('click', () => {
                modal.close();
                modal.destroy();
                resolve();
            });
        });
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Modal;
}
