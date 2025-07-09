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

// Enhanced PWA features initialization
function initializePWAFeatures() {
    console.log('🚀 Initializing PWA features...');
    
    // Check if app is already installed
    if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
        console.log('📱 App is running in standalone mode (installed)');
        hideInstallButton();
        return;
    }
    
    // Show install button if PWA can be installed
    if (window.deferredPrompt) {
        console.log('💾 PWA can be installed, showing install button');
        showInstallButton();
    }
    
    // Enhanced notification permission handling
    if ('Notification' in window) {
        console.log('🔔 Notification permission status:', Notification.permission);
        
        if (Notification.permission === 'default') {
            // Don't auto-request on page load, wait for user interaction
            console.log('ℹ️ Notification permission is default, will request on user interaction');
        } else if (Notification.permission === 'granted') {
            console.log('✅ Notification permission already granted');
            initializePushNotifications();
        } else {
            console.log('❌ Notification permission denied');
        }
    } else {
        console.log('❌ Notifications not supported in this browser');
    }
}

// Enhanced push notification initialization
function initializePushNotifications() {
    console.log('🔔 Initializing push notifications...');
    
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.ready.then(function(registration) {
            console.log('✅ Service Worker ready for push notifications');
            
            // Check if user is already subscribed
            return registration.pushManager.getSubscription();
        }).then(function(subscription) {
            if (subscription) {
                console.log('✅ Already subscribed to push notifications');
                // Update server with current subscription
                sendSubscriptionToServer(subscription);
                hidePushButton();
            } else {
                console.log('ℹ️ Not subscribed to push notifications');
                showPushButton();
            }
        }).catch(error => {
            console.error('❌ Error checking push subscription:', error);
        });
    } else {
        console.log('❌ Push notifications not supported');
    }
}

// Show/hide push notification button
function showPushButton() {
    const enableBtn = document.getElementById('enablePushBtn');
    if (enableBtn) {
        enableBtn.style.display = 'inline-block';
        enableBtn.onclick = requestPushPermission;
    }
}

function hidePushButton() {
    const enableBtn = document.getElementById('enablePushBtn');
    if (enableBtn) {
        enableBtn.style.display = 'none';
    }
}

// Enhanced push permission request
function requestPushPermission() {
    console.log('🔔 User requesting push notification permission');
    
    if (!('Notification' in window)) {
        showToastNotification('Varslinger støttes ikke av denne nettleseren', 'error');
        return;
    }
    
    if (Notification.permission === 'denied') {
        showToastNotification('Varslinger er blokkert. Aktiver dem i nettleserinnstillingene.', 'warning', 8000);
        return;
    }
    
    // Request notification permission first
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            console.log('✅ Notification permission granted');
            showToastNotification('Varslinger aktivert! 🔔', 'success');
            
            // Now subscribe to push notifications
            subscribeToPushNotifications();
        } else {
            console.log('❌ Notification permission denied');
            showToastNotification('Varslinger er nødvendig for å motta påminnelser', 'warning');
        }
    });
}

// Subscribe to push notifications
function subscribeToPushNotifications() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.ready.then(function(registration) {
            console.log('🔔 Subscribing to push notifications...');
            
            return registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY') // Replace with actual key
            });
        }).then(function(subscription) {
            console.log('✅ Push subscription successful');
            sendSubscriptionToServer(subscription);
            hidePushButton();
            showToastNotification('Push-varslinger aktivert! 📱', 'success');
        }).catch(function(error) {
            console.error('❌ Push subscription failed:', error);
            showToastNotification('Kunne ikke aktivere push-varslinger', 'error');
        });
    }
}

// Send subscription to server
function sendSubscriptionToServer(subscription) {
    console.log('📤 Sending subscription to server...');
    
    fetch('/api/push-subscription', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            subscription: subscription,
            timestamp: Date.now()
        })
    }).then(response => {
        if (response.ok) {
            console.log('✅ Subscription sent to server successfully');
        } else {
            console.error('❌ Failed to send subscription to server');
        }
    }).catch(error => {
        console.error('❌ Error sending subscription to server:', error);
    });
}

// VAPID key conversion utility
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Request notification permission with fallback for mobile
function requestNotificationPermissionWithFallback() {
    if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        showToastNotification('Varslinger støttes ikke av denne nettleseren', 'warning');
        return Promise.resolve('denied');
    }
    
    if (Notification.permission === 'granted') {
        return Promise.resolve('granted');
    }
    
    if (Notification.permission === 'denied') {
        showToastNotification('Varslinger er deaktivert. Aktiver dem i nettleserinnstillingene for å motta påminnelser.', 'warning', 8000);
        return Promise.resolve('denied');
    }
    
    // Request permission
    return Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            showToastNotification('Varslinger aktivert! 🔔', 'success');
            // Try to initialize push notifications
            if ('serviceWorker' in navigator && 'PushManager' in window) {
                initializePushNotifications();
            }
        } else {
            showToastNotification('Varslinger er nødvendig for å motta påminnelser', 'warning');
        }
        return permission;
    });
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

// Enhanced mobile-specific notification sound handling
function playNotificationSound(sound) {
    try {
        console.log(`🔊 Attempting to play notification sound: ${sound}`);
        const soundFile = sound || 'pristine.mp3';
        const audio = new Audio(`/static/sounds/${soundFile}`);
        audio.volume = 0.8;
        
        // Enhanced mobile device detection
        const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            console.log('📱 Mobile device detected, using enhanced mobile sound handling');
            
            // Check if user has interacted with the page
            if (window.userInteracted) {
                console.log('✅ User has interacted, attempting direct play');
                const playPromise = audio.play();
                
                if (playPromise !== undefined) {
                    playPromise.then(() => {
                        console.log('✅ Mobile sound played successfully');
                        // Add haptic feedback if available
                        if ('vibrate' in navigator) {
                            navigator.vibrate([100, 50, 100]);
                        }
                    }).catch(error => {
                        console.log('❌ Mobile autoplay failed, showing manual play button');
                        showMobileNotificationButton(soundFile);
                    });
                }
            } else {
                console.log('⚠️ No user interaction detected, showing mobile notification button');
                showMobileNotificationButton(soundFile);
            }
        } else {
            // Desktop handling - more straightforward
            console.log('🖥️ Desktop device detected');
            const playPromise = audio.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('✅ Desktop sound played successfully');
                }).catch(error => {
                    console.error('❌ Desktop sound play failed:', error);
                    showDesktopNotificationFallback(soundFile);
                });
            }
        }
    } catch (error) {
        console.error('💥 Failed to create audio element:', error);
        showNotificationFallback(sound);
    }
}

// Enhanced mobile-optimized notification button
function showMobileNotificationButton(soundFile) {
    // Remove any existing button
    const existingBtn = document.getElementById('mobileNotificationBtn');
    if (existingBtn) existingBtn.remove();
    
    // Create mobile-optimized button with better styling
    const button = document.createElement('button');
    button.id = 'mobileNotificationBtn';
    button.className = 'btn btn-warning position-fixed';
    button.style.cssText = `
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        padding: 15px 25px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        min-width: 280px;
        max-width: 90vw;
        text-align: center;
        animation: pulseGlow 2s infinite;
        border: 2px solid #ffc107;
        background: linear-gradient(45deg, #ffc107, #ff8c00);
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    `;
    
    button.innerHTML = `
        <i class="fas fa-volume-up me-2"></i>
        🔔 Ny påminnelse - Trykk for lyd
        <br><small>Tap to play notification sound</small>
    `;
    
    button.onclick = function() {
        console.log('📱 Mobile user tapped notification button');
        const audio = new Audio(`/static/sounds/${soundFile}`);
        audio.volume = 0.9;
        
        // Set user interaction flag
        window.userInteracted = true;
        
        audio.play().then(() => {
            console.log('✅ Manual sound playback successful');
            this.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
            this.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                Lyd avspilt! 🎵
            `;
            
            // Vibrate if available
            if ('vibrate' in navigator) {
                navigator.vibrate([200, 100, 200]);
            }
            
            // Auto-remove after success
            setTimeout(() => {
                this.remove();
            }, 2000);
        }).catch(error => {
            console.error('❌ Manual sound playback failed:', error);
            this.style.background = 'linear-gradient(45deg, #dc3545, #c82333)';
            this.innerHTML = `
                <i class="fas fa-exclamation-triangle me-2"></i>
                Lyd feilet
            `;
        });
    };
    
    document.body.appendChild(button);
    
    // Add enhanced CSS animation
    const style = document.createElement('style');
    style.id = 'mobileNotificationStyle';
    style.textContent = `
        @keyframes pulseGlow {
            0% { 
                transform: translateX(-50%) scale(1);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }
            50% { 
                transform: translateX(-50%) scale(1.05);
                box-shadow: 0 12px 35px rgba(255,193,7,0.4);
            }
            100% { 
                transform: translateX(-50%) scale(1);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }
        }
        
        #mobileNotificationBtn:hover {
            background: linear-gradient(45deg, #e0a800, #e07600) !important;
            transform: translateX(-50%) scale(1.02);
        }
        
        #mobileNotificationBtn:active {
            transform: translateX(-50%) scale(0.98);
        }
    `;
    
    // Remove existing style if present
    const existingStyle = document.getElementById('mobileNotificationStyle');
    if (existingStyle) existingStyle.remove();
    
    document.head.appendChild(style);
    
    // Auto-remove after 60 seconds
    setTimeout(() => {
        if (button.parentNode) {
            button.style.animation = 'fadeOut 0.5s ease-out';
            setTimeout(() => button.remove(), 500);
        }
    }, 60000);
    
    // Enhanced vibration pattern to get attention
    if ('vibrate' in navigator) {
        navigator.vibrate([300, 100, 300, 100, 300]);
    }
    
    // Show toast notification as backup
    showToastNotification('🔔 Ny påminnelse mottatt! Trykk på knappen for å spille lyd.', 'warning', 5000);
}

// Desktop notification fallback
function showDesktopNotificationFallback(soundFile) {
    const button = document.createElement('button');
    button.className = 'btn btn-outline-warning position-fixed';
    button.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        padding: 10px 15px;
        border-radius: 20px;
    `;
    
    button.innerHTML = '<i class="fas fa-volume-up me-2"></i>Spill lyd';
    
    button.onclick = function() {
        const audio = new Audio(`/static/sounds/${soundFile}`);
        audio.play();
        this.remove();
    };
    
    document.body.appendChild(button);
    
    setTimeout(() => {
        if (button.parentNode) {
            button.remove();
        }
    }, 15000);
}

// General notification fallback
function showNotificationFallback(soundFile) {
    showToastNotification(`⏰ Ny påminnelse! (Lyd: ${soundFile})`, 'warning', 8000);
    
    // Vibrate if available
    if ('vibrate' in navigator) {
        navigator.vibrate([200, 100, 200, 100, 200]);
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

// Check for pending sounds on load
window.addEventListener('load', () => {
  setTimeout(checkPendingSounds, 1000);
});

// Enhanced Service Worker message handling
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', function(event) {
    console.log('📨 Received message from Service Worker:', event.data);
    
    if (event.data && event.data.type === 'PLAY_NOTIFICATION_SOUND') {
      console.log('🎵 Playing notification sound from service worker message:', event.data.sound);
      
      // Play the sound
      playNotificationSound(event.data.sound);
      
      // Show visual notification for mobile
      if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        showToastNotification('🔔 Ny påminnelse mottatt!', 'info', 4000);
        
        // Vibration feedback
        if ('vibrate' in navigator) {
          navigator.vibrate([200, 100, 200, 100, 200]);
        }
      }
      
      // Track notification attempt
      localStorage.setItem('last_notification_attempt', JSON.stringify({
        timestamp: Date.now(),
        sound: event.data.sound,
        fromServiceWorker: true
      }));
    }
  });
  
  // Enhanced Service Worker ready handling
  navigator.serviceWorker.ready.then(registration => {
    console.log('✅ Service Worker ready, registering client');
    
    if (registration.active) {
      // Tell service worker this client is ready
      registration.active.postMessage({
        type: 'CLIENT_READY',
        timestamp: Date.now()
      });
    }
    
    // Set up message channel for bidirectional communication
    const channel = new MessageChannel();
    channel.port1.onmessage = function(event) {
      console.log('📨 Received message via channel:', event.data);
      
      if (event.data && event.data.type === 'PLAY_NOTIFICATION_SOUND') {
        playNotificationSound(event.data.sound);
      }
    };
    
    // Send the port to service worker
    if (registration.active) {
      registration.active.postMessage({
        type: 'CLIENT_READY',
        port: channel.port2
      }, [channel.port2]);
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

// Mobile notification improvements
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           ('ontouchstart' in window) || 
           (navigator.maxTouchPoints > 0);
}