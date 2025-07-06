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
    
    // Push notifications
    initializePushNotifications();
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
    
    // Initialize push notifications
    initializePushNotifications();
}

function initializePushNotifications() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.ready.then(function(registration) {
            // Check if user is already subscribed
            return registration.pushManager.getSubscription();
        }).then(function(subscription) {
            if (subscription) {
                console.log('✅ Already subscribed to push notifications');
                // Update server with subscription
                sendSubscriptionToServer(subscription);
            } else {
                // Ask for permission and subscribe
                requestPushPermission();
            }
        });
    }
}

function requestPushPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {
                subscribeToPush();
                // Hide the enable button
                const enableBtn = document.getElementById('enablePushBtn');
                if (enableBtn) {
                    enableBtn.style.display = 'none';
                }
            }
        });
    }
}

function subscribeToPush() {
    // First get the VAPID public key from server
    fetch('/api/vapid-public-key')
        .then(response => response.json())
        .then(data => {
            const applicationServerKey = urlBase64ToUint8Array(data.public_key);
            
            return navigator.serviceWorker.ready.then(function(registration) {
                return registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: applicationServerKey
                });
            });
        })
        .then(function(subscription) {
            console.log('✅ Subscribed to push notifications');
            sendSubscriptionToServer(subscription);
        })
        .catch(function(error) {
            console.error('❌ Push subscription failed:', error);
        });
}

function sendSubscriptionToServer(subscription) {
    fetch('/api/subscribe-push', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.content
        },
        body: JSON.stringify(subscription)
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Push subscription sent to server');
        }
    }).catch(error => {
        console.error('❌ Failed to send subscription to server:', error);
    });
}

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Board notifications
function notifyBoardUpdate(boardId, updateType, noteContent) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Tavle oppdatert', {
            body: `${updateType}: ${noteContent?.substring(0, 50)}...`,
            icon: '/static/icon-192x192.png',
            tag: `board-${boardId}`
        });
    }
}

// Connection status
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

// Reminder counts
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