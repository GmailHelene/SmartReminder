// Main Application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize app features
    initializeApp();
    
    // Form validation
    initializeFormValidation();
    
    // Real-time updates
    initializeRealTimeUpdates();
    
    // PWA features
    initializePWAFeatures();
});

function initializeApp() {
    // Auto-focus first input on forms
    const firstInput = document.querySelector('input[type="text"], input[type="email"]');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Update connection status
    updateConnectionStatus();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeFormValidation() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

function initializeRealTimeUpdates() {
    // Update reminder counts every 30 seconds
    setInterval(updateReminderCounts, 30000);
}

function initializePWAFeatures() {
    // Show install button if PWA can be installed
    if (window.deferredPrompt) {
        showInstallButton();
    }
    
    // Request notification permission if not granted
    if ('Notification' in window && Notification.permission === 'default') {
        setTimeout(() => {
            if (confirm('Vil du motta notifikasjoner for påminnelser?')) {
                Notification.requestPermission();
            }
        }, 5000);
    }
}

function updateConnectionStatus() {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        if (navigator.onLine) {
            statusElement.innerHTML = '<i class="fas fa-wifi"></i> Online';
            statusElement.className = 'badge bg-success';
        } else {
            statusElement.innerHTML = '<i class="fas fa-wifi-slash"></i> Offline';
            statusElement.className = 'badge bg-warning';
        }
    }
}

function updateReminderCounts() {
    fetch('/api/reminder-count')
        .then(response => response.json())
        .then(data => {
            // Update counts in UI
            const myCount = document.getElementById('my-count');
            const sharedCount = document.getElementById('shared-count');
            const completedCount = document.getElementById('completed-count');
            
            if (myCount) myCount.textContent = data.my_reminders;
            if (sharedCount) sharedCount.textContent = data.shared_reminders;
            if (completedCount) completedCount.textContent = data.completed;
        })
        .catch(error => {
            console.log('Could not update counts:', error);
        });
}

// PWA Installation
let deferredPrompt;
let installButton;

window.addEventListener('beforeinstallprompt', (e) => {
  console.log('PWA installasjonsprompt klar');
  e.preventDefault();
  deferredPrompt = e;
  
  // Vis install-knapp
  installButton = document.getElementById('install-button');
  if (installButton) {
    installButton.style.display = 'block';
  }
});

// Install PWA
function installPWA() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((result) => {
      if (result.outcome === 'accepted') {
        console.log('PWA installasjon akseptert');
      } else {
        console.log('PWA installasjon avvist');
      }
      deferredPrompt = null;
      if (installButton) {
        installButton.style.display = 'none';
      }
    });
  }
}

// Service Worker registrering
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/sw.js')
      .then((registration) => {
        console.log('Service Worker registrert:', registration.scope);
      })
      .catch((err) => {
        console.log('Service Worker registrering feilet:', err);
      });
  });
}

// Notification permission
function requestNotificationPermission() {
  if ('Notification' in window && 'serviceWorker' in navigator) {
    if (Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          console.log('Notification tillatelse gitt');
        }
      });
    }
  }
}

// Online/offline status
window.addEventListener('online', () => {
  console.log('Tilbake online');
  document.body.classList.remove('offline');
  showNotification('Tilbake online!', 'success');
});

window.addEventListener('offline', () => {
  console.log('Offline');
  document.body.classList.add('offline');
  showNotification('Du er offline. Noen funksjoner kan være begrenset.', 'warning');
});

// Local notifications
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  notification.style.top = '20px';
  notification.style.right = '20px';
  notification.style.zIndex = '9999';
  notification.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 5000);
}

// Auto-refresh for reminders
setInterval(() => {
  if (window.location.pathname === '/dashboard') {
    fetch('/api/reminder-count')
      .then(response => response.json())
      .then(data => {
        updateReminderCounts(data);
      })
      .catch(err => console.log('Feil ved oppdatering:', err));
  }
}, 60000); // Hver minutt

function updateReminderCounts(data) {
  const elements = {
    'my-count': data.my_reminders,
    'shared-count': data.shared_reminders,
    'completed-count': data.completed
  };
  
  Object.entries(elements).forEach(([id, count]) => {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = count;
    }
  });
}

// Utility functions
function showLoading(element) {
    if (element) {
        element.innerHTML = '<span class="loading"></span>';
        element.disabled = true;
    }
}

function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Kopiert til utklippstavle!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Kopiert til utklippstavle!', 'success');
    }
}

// Event listeners for online/offline
window.addEventListener('online', updateConnectionStatus);
window.addEventListener('offline', updateConnectionStatus);

// Prevent zoom on mobile double-tap
let lastTouchEnd = 0;
document.addEventListener('touchend', function (event) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Handle back button in PWA
window.addEventListener('popstate', function(event) {
    if (window.history.length === 1) {
        // If this is the only page in history, don't allow back
        window.history.pushState(null, null, window.location.href);
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
            console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
        }
    });
}