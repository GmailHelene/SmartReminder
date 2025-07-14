// SmartReminder App JavaScript
console.log('🚀 SmartReminder App Starting...');

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 DOM loaded, initializing app...');
    
    // Initialize PWA features
    initializePWAFeatures();
    
    // Auto-focus first input on forms
    const firstInput = document.querySelector('input:not([type="hidden"])');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Initialize notification permissions
    if ('Notification' in window) {
        console.log('🔔 Notification permission status:', Notification.permission);
    }
    
    // Initialize service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js', { scope: '/' })
            .then(registration => {
                console.log('✅ Service Worker registered successfully');
            })
            .catch(error => {
                console.error('❌ Service Worker registration failed:', error);
            });
    }
});

// Enhanced PWA features initialization
function initializePWAFeatures() {
    console.log('🚀 Initializing PWA features...');
    
    // Check if app is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
        console.log('📱 App is running in standalone mode (installed)');
        hideInstallButton();
    }
    
    // Show install button if PWA can be installed
    window.addEventListener('beforeinstallprompt', (e) => {
        console.log('💾 PWA can be installed, showing install button');
        showInstallButton();
    });
}

// Show install button
function showInstallButton() {
    const installButton = document.getElementById('installButton');
    if (installButton) {
        installButton.style.display = 'block';
    }
}

// Hide install button
function hideInstallButton() {
    const installButton = document.getElementById('installButton');
    if (installButton) {
        installButton.style.display = 'none';
    }
}

// Enhanced push permission request
function requestPushPermission() {
    console.log('🔔 User requesting push notification permission');
    
    if (!('Notification' in window)) {
        showToastNotification('Varslinger støttes ikke av denne nettleseren', 'info');
        return;
    }
    
    if (Notification.permission === 'denied') {
        // Show helpful instructions for enabling notifications
        showNotificationHelpModal();
        return;
    }
    
    // Request permission
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            console.log('✅ Notification permission granted');
            showToastNotification('Varslinger aktivert! 🎉', 'success');
        } else {
            console.log('❌ Notification permission denied');
            showToastNotification('Varslinger ikke aktivert - appen fungerer normalt uten dem! 👍', 'info');
        }
    }).catch(error => {
        console.error('Error requesting notification permission:', error);
        showToastNotification('Feil ved aktivering av varslinger', 'error');
    });
}

// Show notification help modal
function showNotificationHelpModal() {
    const helpText = `
        <div style="text-align: left; font-size: 0.9em;">
            <p><strong>💡 Slik aktiverer du varslinger (helt valgfritt):</strong></p>
            <p><strong>Chrome/Edge:</strong> Klikk på låsikonet 🔒 ved adresselinjen → Tillat notifikasjoner</p>
            <p><strong>Firefox:</strong> Klikk på skjoldikonet 🛡️ → Tillat notifikasjoner</p>
            <p><strong>Safari:</strong> Safari → Innstillinger → Nettsteder → Notifikasjoner</p>
            <p><strong>Mobil:</strong> Innstillinger → Nettleser → Nettsteder → Tillatelser</p>
            <br>
            <p><em>✨ Husk: Varslinger er kun for push-meldinger til mobilen. Appen fungerer perfekt uten dem!</em></p>
        </div>
    `;
    
    const modal = document.createElement('div');
    modal.className = 'modal fade show';
    modal.style.display = 'block';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">🔔 Varslinger er blokkert</h5>
                    <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                </div>
                <div class="modal-body">
                    ${helpText}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">OK</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Auto-remove after 15 seconds
    setTimeout(() => {
        if (modal.parentNode) {
            modal.remove();
        }
    }, 15000);
}

// Play notification sound
function playNotificationSound(sound) {
    try {
        console.log('🔊 Attempting to play notification sound:', sound);
        const soundFile = sound || 'pristine.mp3';
        const audio = new Audio(`/static/sounds/${soundFile}`);
        
        // Set volume and play
        audio.volume = 0.7;
        audio.play().then(() => {
            console.log('✅ Sound played successfully');
        }).catch(error => {
            console.error('❌ Failed to play sound:', error);
            // Fallback: show visual notification
            showNotificationFallback(soundFile);
        });
    } catch (error) {
        console.error('❌ Error playing notification sound:', error);
        showNotificationFallback(sound);
    }
}

// Test notification sound
function testNotificationSound() {
    console.log('🔊 Testing notification sound...');
    
    // Check if notifications are allowed
    if ('Notification' in window) {
        if (Notification.permission === 'granted') {
            // Play sound and show notification
            playNotificationSound('pristine.mp3');
            
            // Show test notification
            const notification = new Notification('Test Notification', {
                body: 'Dette er en test-notifikasjon fra SmartReminder',
                icon: '/static/images/icon-192x192.png',
                badge: '/static/images/icon-192x192.png'
            });
            
            setTimeout(() => {
                notification.close();
            }, 5000);
            
            showToastNotification('Test-notifikasjon sendt! 🔔', 'success');
        } else if (Notification.permission === 'denied') {
            showToastNotification('Notifikasjon-tillatelse ikke gitt. Aktiver i nettleserinnstillinger.', 'warning');
        } else {
            // Request permission first
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    testNotificationSound(); // Retry
                } else {
                    showToastNotification('Notifikasjonstillatelse avvist', 'warning');
                }
            });
        }
    } else {
        showToastNotification('Notifikasjoner støttes ikke', 'warning');
    }
}

// Show notification fallback
function showNotificationFallback(soundFile) {
    const fallbackDiv = document.createElement('div');
    fallbackDiv.innerHTML = `
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            padding: 15px;
            border-radius: 10px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        ">
            <div style="font-weight: bold; margin-bottom: 5px;">🔔 Påminnelse</div>
            <div>Lyd: ${soundFile}</div>
            <div style="margin-top: 10px;">
                <button onclick="this.closest('div').remove()" style="
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 5px;
                    cursor: pointer;
                ">OK</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(fallbackDiv);
    
    // Auto-remove after 8 seconds
    setTimeout(() => {
        if (fallbackDiv.parentNode) {
            fallbackDiv.remove();
        }
    }, 8000);
}

// Toast notification function
function showToastNotification(message, type = 'info', duration = 4000) {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.closest('.toast').remove()"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, duration);
}

// Create toast container
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Initialize push notifications
function initializePushNotifications() {
    console.log('🔔 Initializing push notifications...');
    
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.ready.then(registration => {
            console.log('✅ Service Worker ready for push notifications');
            
            // Check if already subscribed
            return registration.pushManager.getSubscription();
        }).then(subscription => {
            if (subscription) {
                console.log('✅ Already subscribed to push notifications');
            } else {
                console.log('ℹ️ Not subscribed to push notifications yet');
            }
        }).catch(error => {
            console.error('❌ Error checking push subscription:', error);
        });
    }
}

// Global functions for window
window.requestPushPermission = requestPushPermission;
window.testNotificationSound = testNotificationSound;
window.playNotificationSound = playNotificationSound;
window.showToastNotification = showToastNotification;

console.log('✅ SmartReminder App JavaScript loaded successfully');
