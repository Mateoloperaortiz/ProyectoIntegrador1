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
    
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('id_content');
    
    if (messageForm && messageInput) {
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); // Prevent default behavior (new line)
                messageForm.submit(); // Submit the form
            }
        });
    }
});
