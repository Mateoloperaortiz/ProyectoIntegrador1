/**
 * Unified Chat Interface JavaScript
 * 
 * This file provides all the functionality for the chat interface, including:
 * - Message sending and receiving
 * - UI interactions (auto-resize textarea, scroll to bottom)
 * - Markdown processing
 * - Typing indicators
 * - Error handling
 */

class ChatInterface {
    constructor(options = {}) {
        // Default options
        this.options = {
            enableMarkdown: true,
            enableKeyboardShortcuts: true,
            enableAutoScroll: true,
            enableAutoFocus: true,
            debug: false,
            ...options
        };
        
        // Initialize elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');
        this.messagesContainer = document.getElementById('messagesContainer');
        
        if (this.options.debug) {
            console.log('Chat interface initialized with options:', this.options);
        }
        
        this.init();
    }
    
    init() {
        // Exit if required elements aren't found
        if (!this.chatMessages || !this.messageForm || !this.messageInput || !this.messagesContainer) {
            console.error('Required chat elements not found');
            return;
        }
        
        // Focus input on page load if enabled
        if (this.options.enableAutoFocus) {
            this.messageInput.focus();
        }
        
        // Set up event listeners
        this.setupListeners();
        
        // Scroll to bottom on page load if enabled
        if (this.options.enableAutoScroll) {
            this.scrollToBottom();
        }
    }
    
    setupListeners() {
        // Auto-resize textarea
        this.messageInput.addEventListener('input', this.handleInputResize.bind(this));
        
        // Input focus/blur effects
        this.messageInput.addEventListener('focus', this.handleInputFocus.bind(this));
        this.messageInput.addEventListener('blur', this.handleInputBlur.bind(this));
        
        // Send button hover effects
        const sendButton = this.messageForm.querySelector('button[type="submit"]');
        if (sendButton) {
            sendButton.addEventListener('mouseenter', this.handleSendButtonHover.bind(this, true));
            sendButton.addEventListener('mouseleave', this.handleSendButtonHover.bind(this, false));
        }
        
        // Form submission
        this.messageForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // Keyboard shortcuts
        if (this.options.enableKeyboardShortcuts) {
            document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        }
    }
    
    handleInputResize() {
        // Reset height to auto so it doesn't keep growing
        this.messageInput.style.height = 'auto';
        // Set to scrollHeight to match content
        this.messageInput.style.height = (this.messageInput.scrollHeight) + 'px';
    }
    
    handleInputFocus() {
        this.messageInput.style.borderColor = '#4f46e5';
        this.messageInput.style.boxShadow = '0 0 0 3px rgba(79, 70, 229, 0.2)';
    }
    
    handleInputBlur() {
        this.messageInput.style.borderColor = '#e5e7eb';
        this.messageInput.style.boxShadow = 'none';
    }
    
    handleSendButtonHover(isHovering) {
        const sendButton = this.messageForm.querySelector('button[type="submit"]');
        if (isHovering) {
            sendButton.style.transform = 'scale(1.05)';
            sendButton.style.backgroundColor = '#4338ca';
        } else {
            sendButton.style.transform = 'scale(1)';
            sendButton.style.backgroundColor = '#4f46e5';
        }
    }
    
    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            if (this.options.debug) {
                console.log('Scrolled to bottom, height:', this.chatMessages.scrollHeight);
            }
        }
    }
    
    formatTime(date) {
        return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    }
    
    processMessageContent(content) {
        if (!this.options.enableMarkdown) {
            return content;
        }
        
        // Convert newlines to <br> tags
        let processed = content.replace(/\n/g, '<br>');
        
        // Simple markdown-like formatting
        processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>');
        processed = processed.replace(/`(.*?)`/g, '<code>$1</code>');
        
        return processed;
    }
    
    createTypingIndicator() {
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'message-group ai-message';
        
        loadingIndicator.innerHTML = `
            <div class="avatar ai-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="message-content-wrapper">
                <div class="message-bubble">
                    <div class="message-content">
                        <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return loadingIndicator;
    }
    
    createUserMessageElement(messageContent) {
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'message-group user-message';
        
        const processedContent = this.processMessageContent(messageContent);
        
        userMessageElement.innerHTML = `
            <div class="avatar user-avatar">
                <i class="bi bi-person-fill"></i>
            </div>
            <div class="message-content-wrapper">
                <div class="message-bubble">
                    <div class="message-content">${processedContent}</div>
                </div>
                <div class="message-time">
                    You • ${this.formatTime(new Date())}
                </div>
            </div>
        `;
        
        return userMessageElement;
    }
    
    createAIMessageElement(messageContent) {
        const aiMessageElement = document.createElement('div');
        aiMessageElement.className = 'message-group ai-message';
        
        const processedContent = this.processMessageContent(messageContent);
        
        aiMessageElement.innerHTML = `
            <div class="avatar ai-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="message-content-wrapper">
                <div class="message-bubble">
                    <div class="message-content">${processedContent}</div>
                </div>
                <div class="message-time">
                    AI Assistant • ${this.formatTime(new Date())}
                </div>
            </div>
        `;
        
        return aiMessageElement;
    }
    
    createErrorMessageElement(errorMessage) {
        const errorMessageElement = document.createElement('div');
        errorMessageElement.className = 'message-group ai-message error-message';
        
        errorMessageElement.innerHTML = `
            <div class="avatar">
                <i class="bi bi-exclamation-triangle"></i>
            </div>
            <div class="message-content-wrapper">
                <div class="message-bubble">
                    <div class="message-content">
                        <i class="bi bi-exclamation-circle me-2"></i>
                        ${errorMessage}
                    </div>
                </div>
                <div class="message-time">
                    System • ${this.formatTime(new Date())}
                </div>
            </div>
        `;
        
        return errorMessageElement;
    }
    
    handleFormSubmit(e) {
        e.preventDefault();
        
        const messageContent = this.messageInput.value.trim();
        if (!messageContent) {
            return;
        }
        
        // Clear input and reset height
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.messageInput.focus();
        
        // Add user message to UI immediately
        const userMessageElement = this.createUserMessageElement(messageContent);
        this.messagesContainer.appendChild(userMessageElement);
        this.scrollToBottom();
        
        // Remove empty state message if present
        const emptyStateMessage = this.messagesContainer.querySelector('.empty-state');
        if (emptyStateMessage) {
            this.messagesContainer.removeChild(emptyStateMessage);
        }
        
        // Show loading indicator
        const loadingIndicator = this.createTypingIndicator();
        this.messagesContainer.appendChild(loadingIndicator);
        this.scrollToBottom();
        
        // Get CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Create form data
        const formData = new FormData(this.messageForm);
        formData.set('message', messageContent);
        
        // Get conversation ID from URL if available
        const urlParams = new URLSearchParams(window.location.search);
        const conversationId = urlParams.get('conversation_id');
        if (conversationId) {
            formData.set('conversation_id', conversationId);
        }
        
        // Send request
        fetch(this.messageForm.getAttribute('action'), {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            this.messagesContainer.removeChild(loadingIndicator);
            
            if (data.error) {
                // Show error message
                const errorMessageElement = this.createErrorMessageElement(data.error);
                this.messagesContainer.appendChild(errorMessageElement);
            } else {
                // Add AI response to UI
                const aiMessageElement = this.createAIMessageElement(data.message);
                this.messagesContainer.appendChild(aiMessageElement);
                
                // Update conversation ID if provided
                if (data.conversation_id) {
                    // Update hidden input
                    const conversationIdInput = document.querySelector('input[name="conversation_id"]');
                    if (conversationIdInput) {
                        conversationIdInput.value = data.conversation_id;
                    }
                    
                    // Update URL without refreshing page
                    const newUrl = window.location.pathname + '?conversation_id=' + data.conversation_id;
                    window.history.pushState({path: newUrl}, '', newUrl);
                }
            }
            
            this.scrollToBottom();
        })
        .catch(error => {
            // Remove loading indicator
            this.messagesContainer.removeChild(loadingIndicator);
            
            // Show error message
            const errorMessageElement = this.createErrorMessageElement(
                'An error occurred while sending your message. Please try again.'
            );
            this.messagesContainer.appendChild(errorMessageElement);
            this.scrollToBottom();
            
            if (this.options.debug) {
                console.error('Error:', error);
            }
        });
    }
    
    handleKeyboardShortcuts(e) {
        // Enter to send (without shift)
        if (e.key === 'Enter' && !e.shiftKey && document.activeElement === this.messageInput) {
            e.preventDefault();
            if (this.messageInput.value.trim()) {
                this.messageForm.dispatchEvent(new Event('submit'));
            }
        }
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get configuration from data attributes
    const chatEl = document.querySelector('.chat-container');
    
    // Only initialize if chat container exists
    if (chatEl) {
        const chatOptions = {
            enableMarkdown: chatEl.dataset.enableMarkdown !== 'false',
            enableKeyboardShortcuts: chatEl.dataset.enableKeyboardShortcuts !== 'false',
            enableAutoScroll: chatEl.dataset.enableAutoScroll !== 'false',
            enableAutoFocus: chatEl.dataset.enableAutoFocus !== 'false',
            debug: chatEl.dataset.debug === 'true'
        };
        
        const chat = new ChatInterface(chatOptions);
    }
});