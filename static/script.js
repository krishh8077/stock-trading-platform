// ============================================
// STOCK TRADING PLATFORM - JAVASCRIPT
// ============================================

// Alert dismissal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Dismiss alerts on close button click
    const closeButtons = document.querySelectorAll('[data-dismiss="alert"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.display = 'none';
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});

// ============================================
// FORM VALIDATION
// ============================================

/**
 * Validates email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validates password strength
 */
function isStrongPassword(password) {
    return password.length >= 6;
}

/**
 * Validates signup form
 */
function validateSignupForm() {
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');

    if (!username || !password || !confirmPassword) return true; // Form doesn't exist on this page

    let isValid = true;

    if (username.value.trim().length < 3) {
        showFieldError(username, 'Username must be at least 3 characters');
        isValid = false;
    } else {
        clearFieldError(username);
    }

    if (!isStrongPassword(password.value)) {
        showFieldError(password, 'Password must be at least 6 characters');
        isValid = false;
    } else {
        clearFieldError(password);
    }

    if (password.value !== confirmPassword.value) {
        showFieldError(confirmPassword, 'Passwords do not match');
        isValid = false;
    } else {
        clearFieldError(confirmPassword);
    }

    return isValid;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    field.style.borderColor = '#ef4444';
    const errorDiv = field.nextElementSibling;
    if (!errorDiv || !errorDiv.classList.contains('field-error')) {
        const error = document.createElement('div');
        error.className = 'field-error';
        error.textContent = message;
        error.style.color = '#ef4444';
        error.style.fontSize = '0.875rem';
        error.style.marginTop = '0.25rem';
        field.parentNode.insertBefore(error, field.nextSibling);
    }
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.style.borderColor = '';
    const errorDiv = field.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains('field-error')) {
        errorDiv.remove();
    }
}

// ============================================
// CURRENCY FORMATTING
// ============================================

/**
 * Format number as USD currency
 */
function formatCurrency(value) {
    return '$' + parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Format percentage
 */
function formatPercent(value) {
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(2) + '%';
}

// ============================================
// API UTILITIES
// ============================================

/**
 * Make API request
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, finalOptions);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============================================
// PORTFOLIO UTILITIES
// ============================================

/**
 * Calculate portfolio totals
 */
function calculatePortfolioTotals(portfolio) {
    let totalValue = 0;
    let totalCost = 0;

    portfolio.forEach(holding => {
        totalValue += holding.position_value;
        totalCost += holding.avg_price * holding.shares;
    });

    return {
        totalValue: totalValue,
        totalGainLoss: totalValue - totalCost,
        totalGainLossPercent: totalCost > 0 ? ((totalValue - totalCost) / totalCost * 100) : 0
    };
}

// ============================================
// UI UTILITIES
// ============================================

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '400px';
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Show loading spinner
 */
function showLoadingSpinner(text = 'Loading...') {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div style="border: 4px solid #f3f4f6; border-top: 4px solid #2563eb; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; margin-bottom: 1rem;"></div>
            <p>${text}</p>
        </div>
    `;
    return spinner;
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================
// TABLE UTILITIES
// ============================================

/**
 * Sort table by column
 */
function sortTableByColumn(tableElement, columnIndex, isAscending = true) {
    const rows = Array.from(tableElement.querySelectorAll('.table-row'));
    
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();

        // Try to parse as numbers
        const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }

        // Otherwise, sort as strings
        return isAscending ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });

    rows.forEach(row => tableElement.appendChild(row));
}

// ============================================
// SEARCH UTILITIES
// ============================================

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Filter items based on search query
 */
function filterItems(query, items, searchFields) {
    query = query.toLowerCase().trim();
    
    if (!query) return items;

    return items.filter(item => {
        return searchFields.some(field => {
            const fieldValue = field(item).toLowerCase();
            return fieldValue.includes(query);
        });
    });
}

// ============================================
// ANIMATION UTILITIES
// ============================================

/**
 * Add fade-in animation to element
 */
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease`;
    
    // Trigger reflow
    element.offsetHeight;
    
    element.style.opacity = '1';
}

/**
 * Add fade-out animation to element
 */
function fadeOut(element, duration = 300) {
    element.style.opacity = '1';
    element.style.transition = `opacity ${duration}ms ease`;
    element.style.opacity = '0';
    
    setTimeout(() => {
        element.style.display = 'none';
    }, duration);
}

/**
 * Slide element from left
 */
function slideInFromLeft(element, duration = 300) {
    element.style.transform = 'translateX(-100%)';
    element.style.transition = `transform ${duration}ms ease`;
    
    // Trigger reflow
    element.offsetHeight;
    
    element.style.transform = 'translateX(0)';
}

// ============================================
// LOCAL STORAGE UTILITIES
// ============================================

/**
 * Store data in localStorage
 */
function storeData(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error storing data:', error);
    }
}

/**
 * Retrieve data from localStorage
 */
function retrieveData(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (error) {
        console.error('Error retrieving data:', error);
        return null;
    }
}

/**
 * Remove data from localStorage
 */
function removeData(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing data:', error);
    }
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

/**
 * Export table as CSV
 */
function exportTableAsCSV(tableElement, filename = 'export.csv') {
    const rows = [];
    
    // Get headers
    const headers = Array.from(tableElement.querySelectorAll('.table-header .table-cell'))
        .map(cell => cell.textContent.trim());
    rows.push(headers.join(','));
    
    // Get data rows
    tableElement.querySelectorAll('.table-row').forEach(row => {
        const cells = Array.from(row.querySelectorAll('.table-cell'))
            .map(cell => `"${cell.textContent.trim()}"`);
        rows.push(cells.join(','));
    });

    const csv = rows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Print table
 */
function printTable(tableElement, title = 'Print') {
    const printWindow = window.open('', '', 'width=900,height=500');
    printWindow.document.write(`
        <html>
        <head>
            <title>${title}</title>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { text-align: center; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
                th { background-color: #f5f5f5; }
            </style>
        </head>
        <body>
            <h1>${title}</h1>
            ${tableElement.outerHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K: Focus search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.getElementById('stockSearch');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape: Close modals/forms
    if (event.key === 'Escape') {
        const form = document.getElementById('tradeForm');
        if (form) {
            form.style.display = 'none';
        }
    }
});

// ============================================
// PAGE LOAD UTILITIES
// ============================================

/**
 * Check if page is ready
 */
function whenReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// ============================================
// CONSOLE UTILITIES
// ============================================

/**
 * Log with styling
 */
function styledLog(message, style = 'color: #2563eb; font-weight: bold;') {
    console.log(`%c${message}`, style);
}

// Initialize on page load
whenReady(() => {
    styledLog('Stock Trading Platform - Ready');
});
