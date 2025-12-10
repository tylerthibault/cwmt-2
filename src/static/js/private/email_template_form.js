/**
 * Email Template Form - Rich Text Editor with MJML Support
 * Handles Quill.js, MJML editor, and mode switching
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Quill editor
    const quillEditor = document.getElementById('quillEditor');
    const bodyHtmlField = document.getElementById('body_html');
    const bodyHtmlCodeField = document.getElementById('body_html_code');
    const bodyMjmlField = document.getElementById('body_mjml');
    
    if (!quillEditor) return;
    
    // Configure Quill with formatting options
    const quill = new Quill('#quillEditor', {
        theme: 'snow',
        modules: {
            toolbar: [
                [{ 'header': [1, 2, 3, false] }],
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'color': [] }, { 'background': [] }],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                [{ 'align': [] }],
                ['link', 'image'],
                ['clean']
            ]
        },
        placeholder: 'Compose your email content here...'
    });
    
    // Load existing HTML content if editing
    const existingHtml = bodyHtmlField.value;
    const existingMjml = bodyMjmlField.value;
    
    if (existingHtml) {
        quill.clipboard.dangerouslyPasteHTML(existingHtml);
        bodyHtmlCodeField.value = existingHtml;
    }
    
    // Editor mode switching
    const editorModeRadios = document.getElementsByName('editorMode');
    const richTextContainer = document.getElementById('richTextContainer');
    const mjmlContainer = document.getElementById('mjmlContainer');
    const htmlCodeContainer = document.getElementById('htmlCodeContainer');
    const convertMjmlBtn = document.getElementById('convertMjmlBtn');
    const loadMjmlTemplateBtn = document.getElementById('loadMjmlTemplate');
    const toggleHtmlPreviewBtn = document.getElementById('toggleHtmlPreview');
    
    // Track current mode
    let currentMode = 'rich'; // 'rich', 'mjml', or 'html'
    
    // If there's existing MJML, switch to MJML mode on load
    if (existingMjml && existingMjml.trim()) {
        currentMode = 'mjml';
        document.getElementById('editorModeMjml').checked = true;
        switchEditorMode('mjml');
    }
    
    // Handle editor mode changes
    editorModeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentMode = this.value;
            switchEditorMode(currentMode);
        });
    });
    
    function switchEditorMode(mode) {
        // Hide all containers
        richTextContainer.classList.add('d-none');
        mjmlContainer.classList.add('d-none');
        htmlCodeContainer.classList.add('d-none');
        convertMjmlBtn.style.display = 'none';
        toggleHtmlPreviewBtn.classList.add('d-none');
        
        // Show selected container and relevant buttons
        if (mode === 'rich') {
            richTextContainer.classList.remove('d-none');
        } else if (mode === 'mjml') {
            mjmlContainer.classList.remove('d-none');
            convertMjmlBtn.style.display = 'inline-block';
        } else if (mode === 'html') {
            htmlCodeContainer.classList.remove('d-none');
            toggleHtmlPreviewBtn.classList.remove('d-none');
        }
    }
    
    // Convert MJML to HTML
    convertMjmlBtn.addEventListener('click', async function() {
        const mjmlContent = bodyMjmlField.value;
        
        if (!mjmlContent || !mjmlContent.trim()) {
            alert('Please enter MJML code first');
            return;
        }
        
        const btn = this;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Converting...';
        btn.disabled = true;
        
        try {
            // Send MJML to backend for conversion
            const response = await fetch('/admin/email-templates/convert-mjml', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mjml: mjmlContent })
            });
            
            const data = await response.json();
            
            if (data.success) {
                bodyHtmlField.value = data.html;
                bodyHtmlCodeField.value = formatHtml(data.html);
                
                // Show success message
                btn.innerHTML = '<i class="bi bi-check-circle"></i> Converted!';
                btn.classList.remove('btn-success');
                btn.classList.add('btn-success');
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }, 2000);
            } else {
                alert('MJML Conversion Error: ' + data.error);
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        } catch (error) {
            alert('Error converting MJML: ' + error.message);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
    
    // Load MJML template
    loadMjmlTemplateBtn.addEventListener('click', function() {
        const templates = {
            'Basic': `<mjml>
  <mj-body>
    <mj-section>
      <mj-column>
        <mj-text font-size="20px" color="#626262">Hello {user_name}!</mj-text>
        <mj-text>Replace this with your content.</mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>`,
            'Button': `<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-text font-size="20px" color="#626262">Hello {user_name}!</mj-text>
        <mj-text>Please click the button below to continue.</mj-text>
        <mj-button background-color="#007bff" href="{action_link}">Click Here</mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>`,
            'Welcome': `<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-text font-size="24px" color="#007bff" font-weight="bold" align="center">Welcome to {app_name}!</mj-text>
        <mj-divider border-color="#007bff"></mj-divider>
        <mj-text>Hello {user_name},</mj-text>
        <mj-text>We're excited to have you join us!</mj-text>
        <mj-button background-color="#007bff" href="{login_link}">Get Started</mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>`
        };
        
        const choice = prompt('Choose a template:\n1 = Basic\n2 = Button\n3 = Welcome', '1');
        const templateMap = { '1': 'Basic', '2': 'Button', '3': 'Welcome' };
        const templateName = templateMap[choice];
        
        if (templateName && templates[templateName]) {
            bodyMjmlField.value = templates[templateName];
            // Switch to MJML mode
            document.getElementById('editorModeMjml').checked = true;
            switchEditorMode('mjml');
        }
    });
    
    // HTML Preview Toggle
    const htmlCodeColumn = document.getElementById('htmlCodeColumn');
    const htmlPreviewColumn = document.getElementById('htmlPreviewColumn');
    const htmlPreview = document.getElementById('htmlPreview');
    let previewVisible = false;
    
    if (toggleHtmlPreviewBtn) {
        toggleHtmlPreviewBtn.addEventListener('click', function() {
            previewVisible = !previewVisible;
            
            if (previewVisible) {
                // Hide code, show preview only
                htmlCodeColumn.classList.add('d-none');
                htmlPreviewColumn.classList.remove('d-none');
                htmlPreviewColumn.classList.remove('col-6');
                htmlPreviewColumn.classList.add('col-12');
                
                // Update preview
                updateHtmlPreview();
                
                // Update button
                this.innerHTML = '<i class="bi bi-code-slash"></i> Show Code';
                this.classList.remove('btn-outline-secondary');
                this.classList.add('btn-secondary');
            } else {
                // Hide preview, show code only
                htmlCodeColumn.classList.remove('d-none');
                htmlCodeColumn.classList.remove('col-6');
                htmlCodeColumn.classList.add('col-12');
                htmlPreviewColumn.classList.add('d-none');
                htmlPreviewColumn.classList.remove('col-12');
                
                // Update button
                this.innerHTML = '<i class="bi bi-eye"></i> Preview';
                this.classList.remove('btn-secondary');
                this.classList.add('btn-outline-secondary');
            }
        });
        
        // Update preview on typing (with debounce)
        let previewTimeout;
        bodyHtmlCodeField.addEventListener('input', function() {
            if (previewVisible) {
                clearTimeout(previewTimeout);
                previewTimeout = setTimeout(updateHtmlPreview, 500);
            }
        });
    }
    
    function updateHtmlPreview() {
        const htmlContent = bodyHtmlCodeField.value;
        if (htmlContent) {
            htmlPreview.innerHTML = htmlContent;
        } else {
            htmlPreview.innerHTML = '<p class="text-muted text-center">No HTML to preview</p>';
        }
    }
    
    // Update hidden field on form submission
    const form = document.getElementById('emailTemplateForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Get HTML content based on current mode
            let htmlContent;
            if (currentMode === 'rich') {
                htmlContent = quill.root.innerHTML;
            } else if (currentMode === 'html') {
                htmlContent = bodyHtmlCodeField.value;
            } else if (currentMode === 'mjml') {
                // HTML should already be set from MJML conversion
                htmlContent = bodyHtmlField.value;
                if (!htmlContent) {
                    e.preventDefault();
                    alert('Please convert your MJML to HTML before saving');
                    return;
                }
            }
            
            // Clean up empty Quill content
            if (htmlContent === '<p><br></p>' || htmlContent === '<p></p>') {
                htmlContent = '';
            }
            
            // Set the value in the hidden field
            if (currentMode !== 'mjml') {
                bodyHtmlField.value = htmlContent;
            }
        });
    }
    
    // Add HTML to Plain Text converter
    addPlainTextGenerator(quill);
    
    // Add variable insertion helper
    addVariableInsertionHelper(quill);
});

/**
 * Add HTML to Plain Text converter
 */
function addPlainTextGenerator(quill) {
    const generateBtn = document.getElementById('generatePlainText');
    const bodyTextArea = document.getElementById('body_text');
    const bodyHtmlCodeField = document.getElementById('body_html_code');
    
    if (!generateBtn || !bodyTextArea) return;
    
    generateBtn.addEventListener('click', function() {
        // Get current HTML content
        let htmlContent;
        
        // Check if we're in code view or WYSIWYG view
        if (bodyHtmlCodeField && !bodyHtmlCodeField.classList.contains('d-none')) {
            htmlContent = bodyHtmlCodeField.value;
        } else {
            htmlContent = quill.root.innerHTML;
        }
        
        // Convert HTML to plain text
        const plainText = htmlToPlainText(htmlContent);
        
        // Set the plain text value
        bodyTextArea.value = plainText;
        
        // Visual feedback
        const originalText = generateBtn.innerHTML;
        generateBtn.innerHTML = '<i class="bi bi-check-circle"></i> Generated!';
        generateBtn.classList.remove('btn-primary');
        generateBtn.classList.add('btn-success');
        
        setTimeout(() => {
            generateBtn.innerHTML = originalText;
            generateBtn.classList.remove('btn-success');
            generateBtn.classList.add('btn-primary');
        }, 2000);
    });
}

/**
 * Convert HTML to plain text
 * Preserves structure and removes HTML tags
 */
function htmlToPlainText(html) {
    if (!html) return '';
    
    // Create a temporary div to parse HTML
    const temp = document.createElement('div');
    temp.innerHTML = html;
    
    // Process the content
    let text = '';
    
    // Recursive function to extract text
    function processNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            // Add text content
            const content = node.textContent.trim();
            if (content) {
                text += content;
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            const tagName = node.tagName.toLowerCase();
            
            // Handle different elements
            if (tagName === 'br') {
                text += '\n';
            } else if (tagName === 'p' || tagName === 'div') {
                // Process children first
                Array.from(node.childNodes).forEach(processNode);
                // Add line break after paragraphs
                text += '\n\n';
            } else if (tagName === 'h1' || tagName === 'h2' || tagName === 'h3' || 
                       tagName === 'h4' || tagName === 'h5' || tagName === 'h6') {
                // Headers with emphasis
                const headerText = node.textContent.trim();
                if (headerText) {
                    text += headerText.toUpperCase() + '\n';
                    text += '='.repeat(Math.min(headerText.length, 50)) + '\n\n';
                }
            } else if (tagName === 'li') {
                // List items with bullet
                text += '• ';
                Array.from(node.childNodes).forEach(processNode);
                text += '\n';
            } else if (tagName === 'ul' || tagName === 'ol') {
                // Process list
                Array.from(node.childNodes).forEach(processNode);
                text += '\n';
            } else if (tagName === 'a') {
                // Links with URL
                const linkText = node.textContent.trim();
                const href = node.getAttribute('href');
                if (linkText && href) {
                    text += `${linkText} (${href})`;
                } else if (linkText) {
                    text += linkText;
                }
            } else if (tagName === 'strong' || tagName === 'b') {
                // Bold text with asterisks
                const boldText = node.textContent.trim();
                if (boldText) {
                    text += `**${boldText}**`;
                }
            } else if (tagName === 'em' || tagName === 'i') {
                // Italic text with underscores
                const italicText = node.textContent.trim();
                if (italicText) {
                    text += `_${italicText}_`;
                }
            } else {
                // For other elements, just process children
                Array.from(node.childNodes).forEach(processNode);
            }
        }
    }
    
    processNode(temp);
    
    // Clean up excessive whitespace
    text = text.replace(/\n{3,}/g, '\n\n'); // Max 2 consecutive newlines
    text = text.replace(/[ \t]+/g, ' '); // Multiple spaces to single space
    text = text.trim();
    
    return text;
}

/**
 * Add helper to insert variables at cursor position
 */
function addVariableInsertionHelper(quill) {
    // Create variable insertion buttons if there's a variables list
    const variablesList = document.querySelector('.card-body ul');
    if (!variablesList) return;
    
    // Add click handlers to variable codes in the sidebar
    const variableCodes = document.querySelectorAll('.card-body code');
    variableCodes.forEach(code => {
        code.style.cursor = 'pointer';
        code.title = 'Click to insert at cursor';
        
        code.addEventListener('click', function() {
            const variable = this.textContent;
            const range = quill.getSelection(true);
            quill.insertText(range.index, variable);
            quill.setSelection(range.index + variable.length);
            
            // Visual feedback
            this.classList.add('text-success');
            setTimeout(() => {
                this.classList.remove('text-success');
            }, 500);
        });
    });
}

/**
 * Basic HTML formatter for code view
 */
function formatHtml(html) {
    // Simple formatting - add line breaks after tags
    let formatted = html;
    formatted = formatted.replace(/></g, '>\n<');
    
    // Basic indentation
    const lines = formatted.split('\n');
    let indentLevel = 0;
    const indentedLines = [];
    
    lines.forEach(line => {
        const trimmed = line.trim();
        if (!trimmed) return;
        
        // Decrease indent for closing tags
        if (trimmed.startsWith('</')) {
            indentLevel = Math.max(0, indentLevel - 1);
        }
        
        indentedLines.push('  '.repeat(indentLevel) + trimmed);
        
        // Increase indent for opening tags (not self-closing)
        if (trimmed.startsWith('<') && !trimmed.startsWith('</') && 
            !trimmed.endsWith('/>') && !trimmed.match(/<(br|img|hr|input)[^>]*>/)) {
            indentLevel++;
        }
    });
    
    return indentedLines.join('\n');
}
