/**
 * Toast notification component
 * 
 * Usage: 
 * showToast('Título', 'Mensagem a ser exibida', 'error', 5000);
 * Types: 'error', 'success', 'warning', 'info'
 */

// Remove any existing toast when showing a new one
function removeExistingToasts() {
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => {
        toast.remove();
    });
}

// SVG icons for different toast types
const toastIcons = {
    error: '<svg class="error-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
    success: '<svg class="success-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>',
    warning: '<svg class="warning-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>',
    info: '<svg class="info-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
};

// Default titles for different toast types
const defaultTitles = {
    error: 'Erro',
    success: 'Sucesso',
    warning: 'Aviso',
    info: 'Informação'
};

/**
 * Show a toast notification
 * @param {string} title - Toast title (optional, defaults based on type)
 * @param {string} message - Toast message content
 * @param {string} type - Toast type: 'error', 'success', 'warning', 'info'
 * @param {number} duration - Duration in ms (optional, default 5000ms)
 */
function showToast(title, message, type = 'info', duration = 5000) {
    // Remove any existing toasts
    removeExistingToasts();
    
    // If title is not provided, use default for the type
    if (!title) {
        title = defaultTitles[type] || 'Notificação';
    }
    
    // Create toast container
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Create toast content
    toast.innerHTML = `
        <div class="toast-icon">
            ${toastIcons[type] || toastIcons.info}
        </div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" aria-label="Fechar">&times;</button>
    `;
    
    // Add toast to the document
    document.body.appendChild(toast);
    
    // Get close button
    const closeButton = toast.querySelector('.toast-close');
    
    // Handle close button click
    closeButton.addEventListener('click', () => {
        toast.classList.add('hide');
        setTimeout(() => {
            toast.remove();
        }, 300);
    });
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (document.body.contains(toast)) {
                toast.classList.add('hide');
                setTimeout(() => {
                    toast.remove();
                }, 300);
            }
        }, duration);
    }
    
    return toast;
}

// Make the function available globally
window.showToast = showToast;