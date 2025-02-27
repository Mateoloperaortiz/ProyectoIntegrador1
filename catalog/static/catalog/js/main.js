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
        
        if (filterCategory === currentCategory) {
            filter.classList.add('active');
        }
        
        // Add click event
        filter.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            let url = new URL(window.location);
            
            if (category) {
                url.searchParams.set('category', category);
            } else {
                url.searchParams.delete('category');
            }
            
            window.location.href = url.toString();
        });
    });
}

/**
 * Add loading state to search form
 */
function initSearchLoading() {
    const searchForms = document.querySelectorAll('form[role="search"]');
    
    if (searchForms.length === 0) return;
    
    searchForms.forEach(form => {
        form.addEventListener('submit', function() {
            // Create and show loading spinner
            const spinner = document.createElement('div');
            spinner.classList.add('spinner-border', 'spinner-border-sm', 'text-light', 'ms-2');
            spinner.setAttribute('role', 'status');
            
            const searchButton = this.querySelector('button[type="submit"]');
            searchButton.appendChild(spinner);
            searchButton.disabled = true;
        });
    });
}
