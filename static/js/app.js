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
    
    // Check for pending notification sounds
    checkPendingSounds();
    
    // Set user interaction flag for audio playback on mobile
    document.body.addEventListener('click', function() {
        window.userInteracted = true;
    }, { once: true });
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
function notifyBoardUpdate(boardId, updateType, noteContent, sound = 'pristine.mp3') {
    if ('Notification' in window && Notification.permission === 'granted') {
        // Create notification
        new Notification('Tavle oppdatert', {
            body: `${updateType}: ${noteContent?.substring(0, 50)}...`,
            icon: '/static/icon-192x192.png',
            tag: `board-${boardId}`,
            sound: sound,
            silent: false
        });
        
        // Play sound separately (because browser notification sound support is limited)
        playNotificationSound(sound);
    }
}

// Play notification sound
function playNotificationSound(sound) {
  try {
    console.log(`Attempting to play notification sound: ${sound}`);
    const soundFile = sound || 'pristine.mp3';
    
    // Create a visible button for user to interact with (needed for mobile)
    const soundButton = document.createElement('button');
    soundButton.id = 'play-sound-button';
    soundButton.className = 'btn btn-warning position-fixed';
    soundButton.innerHTML = '<i class="fas fa-volume-up me-2"></i> Spill påminnelseslyd';
    soundButton.style.bottom = '20px';
    soundButton.style.right = '20px';
    soundButton.style.zIndex = '9999';
    soundButton.style.padding = '10px 15px';
    soundButton.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
    
    // Button click handler - this will work on mobile due to user interaction
    soundButton.onclick = function() {
      const buttonAudio = new Audio(`/static/sounds/${soundFile}`);
      buttonAudio.volume = 1.0;
      buttonAudio.play()
        .then(() => {
          console.log('Sound played successfully via button click');
          // Success - remove button
          if (soundButton.parentNode) {
            soundButton.parentNode.removeChild(soundButton);
          }
        })
        .catch(err => {
          console.error('Failed to play sound even with button click:', err);
          showToastNotification('Kunne ikke spille lyd. Sjekk lydinnstillinger.', 'error');
        });
      
      return false;
    };
    
    // First attempt - try to play directly (works on desktop browsers)
    const audio = new Audio(`/static/sounds/${soundFile}`);
    audio.volume = 1.0;
    
    const playPromise = audio.play();
    
    if (playPromise !== undefined) {
      playPromise.then(() => {
        console.log(`Sound ${soundFile} playing successfully`);
        // No need to show button if it worked
      }).catch(error => {
        console.error(`Error playing notification sound: ${error}`);
        
        // Add button to DOM for user to click (needed for mobile)
        document.body.appendChild(soundButton);
        
        // Use vibration as fallback
        if ('vibrate' in navigator) {
          navigator.vibrate([200, 100, 200]);
        }
        
        // Show notification to user
        showToastNotification('⏰ Ny påminnelse! Trykk på knappen for å høre varsellyd', 'warning');
        
        // Auto-remove button after 15 seconds if not clicked
        setTimeout(() => {
          if (soundButton.parentNode) {
            soundButton.parentNode.removeChild(soundButton);
          }
        }, 15000);
      });
    }
  } catch (error) {
    console.error(`Failed to play notification sound: ${error}`);
  }
}

// Check for any pending notification sounds
function checkPendingSounds() {
  if ('caches' in window) {
    caches.open('sound-notifications').then(cache => {
      cache.match('/pending-sounds').then(response => {
        if (response) {
          response.json().then(data => {
            // Check if the sound notification is recent (last 5 minutes)
            const now = Date.now();
            const fiveMinutesAgo = now - (5 * 60 * 1000);
            
            if (data.timestamp > fiveMinutesAgo) {
              console.log('Found pending sound notification:', data);
              playNotificationSound(data.sound);
            }
            
            // Clear the pending sound
            cache.delete('/pending-sounds');
          });
        }
      });
    });
  }
}

// Listen for messages from service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', function(event) {
    console.log('Received message from Service Worker:', event.data);
    
    if (event.data && event.data.type === 'PLAY_NOTIFICATION_SOUND') {
      console.log('Playing notification sound from service worker message:', event.data.sound);
      
      // First try standard playback
      playNotificationSound(event.data.sound);
      
      // For mobile, show a visual toast notification and vibrate if possible
      if ('ontouchstart' in document.documentElement) {
        // Visual notification
        showToastNotification('Ny påminnelse! ⏰', 'warning', 5000);
        
        // Vibration API if available
        if ('vibrate' in navigator) {
          navigator.vibrate([200, 100, 200, 100, 200]);
        }
        
        // Track that we attempted a notification
        localStorage.setItem('last_notification_attempt', JSON.stringify({
          timestamp: Date.now(),
          sound: event.data.sound
        }));
        
        // Add a manual play button to DOM
        const manualPlayBtn = document.createElement('button');
        manualPlayBtn.id = 'manualSoundBtn';
        manualPlayBtn.className = 'btn btn-warning position-fixed bottom-0 start-50 translate-middle-x mb-4 px-4 py-2 rounded-pill';
        manualPlayBtn.innerHTML = '<i class="fas fa-volume-up me-2"></i> Spill påminnelselyd';
        manualPlayBtn.style.zIndex = '9999';
        manualPlayBtn.style.boxShadow = '0 4px 10px rgba(0,0,0,0.3)';
        manualPlayBtn.onclick = function() {
          // This should work because it's from a user interaction
          const audio = new Audio(`/static/sounds/${event.data.sound || 'pristine.mp3'}`);
          audio.play();
          this.remove();
          window.userInteracted = true;
        };
        
        // Remove any existing button
        const existingBtn = document.getElementById('manualSoundBtn');
        if (existingBtn) existingBtn.remove();
        
        // Add to document
        document.body.appendChild(manualPlayBtn);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
          if (manualPlayBtn.parentNode) {
            manualPlayBtn.remove();
          }
        }, 10000);
      }
    }
  });
  
  // Notify service worker that this client is ready to receive messages
  navigator.serviceWorker.ready.then(registration => {
    if (registration.active) {
      registration.active.postMessage({
        type: 'CLIENT_READY'
      });
    }
  });
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
    // Wait a bit for other service worker registrations to complete
    setTimeout(() => {
      navigator.serviceWorker.register('/static/sw.js', { scope: '/' })
        .then((registration) => {
          console.log('Service Worker registrert:', registration.scope);
        })
        .catch((err) => {
          console.log('Service Worker registrering feilet:', err);
        });
    }, 1000);
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

// Helper function to show toast notifications
function showToastNotification(message, type = 'info', duration = 3000) {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'position-fixed top-0 end-0 p-3';
    toastContainer.style.zIndex = '9999';
    document.body.appendChild(toastContainer);
  }
  
  // Generate a unique ID for this toast
  const toastId = 'toast-' + Date.now();
  
  // Create the toast element
  const toastEl = document.createElement('div');
  toastEl.id = toastId;
  toastEl.className = `toast toast-pwa align-items-center text-white bg-${type} border-0`;
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  
  // Create toast content
  const toastContent = document.createElement('div');
  toastContent.className = 'd-flex';
  
  const toastBody = document.createElement('div');
  toastBody.className = 'toast-body';
  toastBody.textContent = message;
  
  const closeButton = document.createElement('button');
  closeButton.type = 'button';
  closeButton.className = 'btn-close btn-close-white me-2 m-auto';
  closeButton.setAttribute('data-bs-dismiss', 'toast');
  closeButton.setAttribute('aria-label', 'Lukk');
  
  // Assemble the toast
  toastContent.appendChild(toastBody);
  toastContent.appendChild(closeButton);
  toastEl.appendChild(toastContent);
  
  // Add to container
  toastContainer.appendChild(toastEl);
  
  // Initialize Bootstrap toast
  const toast = new bootstrap.Toast(toastEl, {
    animation: true,
    autohide: true,
    delay: duration
  });
  
  // Show the toast
  toast.show();
  
  // Set up auto-removal
  setTimeout(() => {
    if (toastEl && toastEl.parentNode) {
      toastEl.parentNode.removeChild(toastEl);
    }
  }, duration + 500);
  
  return toastId;
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

// Check for any pending notification sounds
function checkPendingSounds() {
  if ('caches' in window) {
    caches.open('sound-notifications').then(cache => {
      cache.match('/pending-sounds').then(response => {
        if (response) {
          response.json().then(data => {
            // Check if the sound notification is recent (last 5 minutes)
            const now = Date.now();
            const fiveMinutesAgo = now - (5 * 60 * 1000);
            
            if (data.timestamp > fiveMinutesAgo) {
              console.log('Found pending sound notification:', data);
              playNotificationSound(data.sound);
            }
            
            // Clear the pending sound
            cache.delete('/pending-sounds');
          });
        }
      });
    });
  }
}

// Check for pending sounds on load
window.addEventListener('load', () => {
  setTimeout(checkPendingSounds, 1000);
});

// Notify service worker that this client is ready to receive messages
if (navigator.serviceWorker.controller) {
  navigator.serviceWorker.controller.postMessage({
    type: 'CLIENT_READY',
    timestamp: Date.now()
  });
}