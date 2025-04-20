// Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Search functionality enhancement
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        // Keep track of the last query to avoid duplicate requests
        let lastQuery = '';
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            // Only proceed if query is different from last and not empty
            if (query !== lastQuery && query.length > 2) {
                lastQuery = query;
                
                // Show loading indicator here if needed
                
                // In a real app, we would implement AJAX search here
                console.log('Searching for:', query);
            }
        });
    }
    
    // NOTE: The Enter key event listener for message form was moved to conversation_detail.html
    // to avoid duplicate form submissions

    // Initialize highlight.js for all pages
    initializeHighlightJS();
});

/**
 * Initialize highlight.js and apply syntax highlighting to all code blocks
 */
function initializeHighlightJS() {
    // Set up custom renderer for marked.js if it exists
    if (typeof marked !== 'undefined') {
        const renderer = new marked.Renderer();
        renderer.code = function(code, language) {
            // Extract language from the first line if it follows a specific pattern: ```language
            let detectedLanguage = language;
            
            if (!detectedLanguage || detectedLanguage === 'plaintext') {
                // Try to extract language from the first line if it starts with a specific pattern
                const firstLine = code.split('\n')[0].trim();
                if (firstLine.match(/^[a-zA-Z0-9_+-]+$/)) {
                    detectedLanguage = firstLine;
                    code = code.substring(firstLine.length).trim();
                }
            }
            
            // Normalize language name
            const languageMap = {
                'js': 'javascript',
                'ts': 'typescript',
                'py': 'python',
                'rb': 'ruby',
                'sh': 'bash',
                'shell': 'bash',
                'html': 'xml',
                'md': 'markdown'
            };
            
            if (languageMap[detectedLanguage]) {
                detectedLanguage = languageMap[detectedLanguage];
            }
            
            const validLanguage = hljs.getLanguage(detectedLanguage) ? detectedLanguage : 'plaintext';
            
            try {
                const highlightedCode = hljs.highlight(code, { language: validLanguage }).value;
                
                // Add language badge and copy button for all code blocks with improved positioning
                if (validLanguage !== 'plaintext') {
                    return '<div class="code-block-container"><pre><span class="code-language-badge">' + validLanguage + '</span><button class="copy-code-button" onclick="copyCodeToClipboard(this)"><i class="fas fa-copy"></i></button><code class="hljs language-' + validLanguage + '">' + highlightedCode + '</code></pre></div>';
                } else {
                    return '<div class="code-block-container"><pre><button class="copy-code-button" onclick="copyCodeToClipboard(this)"><i class="fas fa-copy"></i></button><code class="hljs language-' + validLanguage + '">' + highlightedCode + '</code></pre></div>';
                }
            } catch (e) {
                console.error("Highlight.js error:", e);
                return '<div class="code-block-container"><pre><button class="copy-code-button" onclick="copyCodeToClipboard(this)"><i class="fas fa-copy"></i></button><code class="hljs">' + hljs.escape(code) + '</code></pre></div>';
            }
        };
        
        // Configure marked.js
        marked.setOptions({
            breaks: true,
            gfm: true,
            pedantic: false,
            smartLists: true,
            xhtml: false
        });
        
        // Use the custom renderer with marked
        marked.use({ renderer: renderer });
    }
    
    // Apply highlighting to all code blocks
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    // Add copy buttons to code blocks that don't already have them
    document.querySelectorAll('pre:not(.code-block-container pre)').forEach((pre) => {
        const container = document.createElement('div');
        container.className = 'code-block-container';
        
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-code-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.onclick = function() { copyCodeToClipboard(this); };
        
        // Replace the pre with our container containing the original pre
        pre.parentNode.insertBefore(container, pre);
        container.appendChild(pre);
        pre.appendChild(copyButton);
    });
}

/**
 * Function to copy code to clipboard
 * @param {HTMLElement} button - The copy button element
 */
function copyCodeToClipboard(button) {
    const codeBlock = button.parentElement.querySelector('code');
    const code = codeBlock.textContent;
    
    navigator.clipboard.writeText(code).then(function() {
        // Show success feedback
        button.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(function() {
            button.innerHTML = '<i class="fas fa-copy"></i>';
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

// Make functions globally available
window.copyCodeToClipboard = copyCodeToClipboard;
