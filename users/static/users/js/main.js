/**
 * This file is deprecated and only exists for backward compatibility.
 * Please use the centralized version in /core/static/core/js/shared/main.js instead.
 */

// Dynamically import the centralized main.js
(function() {
    const script = document.createElement('script');
    script.src = '/static/core/js/shared/main.js';
    script.async = true;
    document.head.appendChild(script);
})();