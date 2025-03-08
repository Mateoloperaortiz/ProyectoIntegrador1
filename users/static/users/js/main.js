/**
 * Main JavaScript for InspireAI
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('InspireAI JavaScript loaded');
    
    // Initialize all components
    initFadeInSections();
    initFormValidation();
    initPopularityBars();
    initCategoryFilters();
    
    // Add loading state to search
    initSearchLoading();
});

/**
 * Initialize fade-in sections when scrolled into view
 */
function initFadeInSections() {
    const sections = document.querySelectorAll('.fade-in-section');
    
    if (sections.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

/**
 * Initialize popularity bars with animation
 */
function initPopularityBars() {
    const popularityBars = document.querySelectorAll('.popularity-progress');
    
    if (popularityBars.length === 0) return;
    
    // Add animation when in viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetWidth = entry.target.getAttribute('data-width');
                setTimeout(() => {
                    entry.target.style.width = `${targetWidth}%`;
                }, 200);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    popularityBars.forEach(bar => {
        observer.observe(bar);
    });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    if (forms.length === 0) return;
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize category filters with active state
 */
function initCategoryFilters() {
    const categoryFilters = document.querySelectorAll('.category-filter-item');
    
    if (categoryFilters.length === 0) return;
    
    // Get the current URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const currentCategory = urlParams.get('category');
    
    // Add active class to current category
    categoryFilters.forEach(filter => {
        const filterCategory = filter.getAttribute('data-category');
        
        if ((currentCategory === null && filterCategory === '') || 
            (currentCategory === filterCategory)) {
            filter.classList.add('active');
        } else {
            filter.classList.remove('active');
        }
        
        // Add click event
        filter.addEventListener('click', () => {
            // Add loading state
            document.body.classList.add('loading');
            
            // Get base URL (either the tool_list or current category-specific URL)
            let baseUrl;
            const pathParts = window.location.pathname.split('/');
            
            if (pathParts.includes('category')) {
                // We're on a category page, need to change to the base tools URL
                baseUrl = '/tools/';
            } else if (pathParts.includes('search')) {
                // We're on a search page, stay there but update the category
                baseUrl = '/search/';
            } else {
                // We're on the main tools page
                baseUrl = window.location.pathname;
            }
            
            // Get current parameters
            const params = new URLSearchParams(window.location.search);
            
            // Update or remove category parameter
            if (filterCategory === '') {
                params.delete('category');
            } else {
                params.set('category', filterCategory);
            }
            
            // Remove page parameter to start from page 1
            params.delete('page');
            
            // Build new URL
            let newUrl = baseUrl;
            const queryString = params.toString();
            if (queryString) {
                newUrl += '?' + queryString;
            }
            
            // Navigate to new URL
            window.location.href = newUrl;
        });
    });
}

/**
 * Add loading state to search
 */
function initSearchLoading() {
    const searchForms = document.querySelectorAll('form[role="search"]');
    
    if (searchForms.length === 0) return;
    
    searchForms.forEach(form => {
        form.addEventListener('submit', () => {
            document.body.classList.add('loading');
        });
    });
}
