/**
 * Loading screen component
 * 
 * Usage:
 * - showLoading() - Show the loading overlay
 * - hideLoading() - Hide the loading overlay
 * - showLoading('Mensagem personalizada') - Show with custom message
 */

// Create the loading overlay if it doesn't exist
function createLoadingOverlay() {
    // Check if loading overlay already exists
    if (document.querySelector('.loading-overlay')) {
        return;
    }
    
    // Create the loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    
    // Create the internal structure
    loadingOverlay.innerHTML = `
        <div class="background-elements">
            <div class="background-circle"></div>
            <div class="background-circle"></div>
        </div>
        
        <div class="loading-container">
            <div class="loading-dots">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
            <div class="loading-text">Carregando</div>
            <div class="loading-subtext">Preparando seus dados com segurança e precisão...</div>
        </div>
    `;
    
    // Append to the body
    document.body.appendChild(loadingOverlay);
}

/**
 * Show the loading overlay
 * @param {string} message - Custom message to display (optional)
 */
function showLoading(message) {
    // Create the loading overlay if it doesn't exist
    createLoadingOverlay();
    
    // Get the loading overlay
    const loadingOverlay = document.querySelector('.loading-overlay');
    
    // Update the message if provided
    if (message) {
        const loadingSubtext = loadingOverlay.querySelector('.loading-subtext');
        if (loadingSubtext) {
            loadingSubtext.textContent = message;
        }
    }
    
    // Add active class to show the overlay
    loadingOverlay.classList.add('active');
}

/**
 * Hide the loading overlay
 */
function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('active');
    }
}

// Make functions available globally
window.showLoading = showLoading;
window.hideLoading = hideLoading;