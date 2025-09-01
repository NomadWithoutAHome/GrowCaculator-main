// Utility functions
export function debounce(func, wait) {
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

export function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

export function formatLargeNumber(num) {
    if (num >= 1e21) {
        return (num / 1e21).toFixed(2) + ' Sextillion';
    } else if (num >= 1e18) {
        return (num / 1e18).toFixed(2) + ' Quintillion';
    } else if (num >= 1e15) {
        return (num / 1e15).toFixed(2) + ' Quadrillion';
    } else if (num >= 1e12) {
        return (num / 1e12).toFixed(2) + ' Trillion';
    } else if (num >= 1e9) {
        return (num / 1e9).toFixed(2) + ' Billion';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(2) + ' Million';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(2) + 'K';
    } else {
        return num.toFixed(2);
    }
}
