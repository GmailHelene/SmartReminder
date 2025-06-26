// PWA Installation and Updates
let deferredPrompt;
let isInstalled = false;

// Check if app is already installed
window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show install button
    showInstallButton();
});

// Check if app is launched from home screen
window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
    hideInstallButton();
    isInstalled = true;
    showToast('App installert! Du kan nå bruke den fra hjemskjermen.', 'success');
});

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateAvailable();
                        }
                    });
                });
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Install button functions
function showInstallButton() {
    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
        installBtn.style.display = 'block';
        installBtn.classList.add('pwa-install-banner');
    }
}

function hideInstallButton() {
    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
        installBtn.style.display = 'none';
    }
}

// Install app function
function installApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
                hideInstallButton();
            } else {
                console.log('User dismissed the install prompt');
            }
            deferredPrompt = null;
        });
    }
}

// Update available notification
function showUpdateAvailable() {
    showToast('En ny versjon er tilgjengelig! Oppdater for å få de nyeste funksjonene.', 'info', 10000, () => {
        window.location.reload();
    });
}

// Toast notification function
function showToast(message, type = 'info', duration = 5000, callback = null) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-pwa');
    existingToasts.forEach(toast => toast.remove());

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-pwa alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 350px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    `;
    
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        ${callback ? '<button type="button" class="btn btn-sm btn-outline-primary ms-2" onclick="updateApp()">Oppdater nå</button>' : ''}
    `;

    // Add to page
    document.body.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, duration);

    // Store callback for update button
    if (callback) {
        window.updateApp = callback;
    }
}

// Check online/offline status
window.addEventListener('online', () => {
    document.body.classList.remove('offline');
    showToast('Du er nå tilkoblet internett!', 'success');
});

window.addEventListener('offline', () => {
    document.body.classList.add('offline');
    showToast('Du er offline. Noen funksjoner kan være begrenset.', 'warning');
});

// Check if device supports installation
function checkInstallability() {
    // Check if standalone mode (already installed)
    if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
        isInstalled = true;
        hideInstallButton();
        return;
    }

    // Check if iOS and not in standalone mode
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (isIOS && !isInstalled) {
        showIOSInstallInstructions();
    }
}

// Show iOS install instructions
function showIOSInstallInstructions() {
    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
        installBtn.innerHTML = `
            <i class="fas fa-download"></i>
            Installer appen: Trykk <i class="fas fa-share"></i> og "Legg til på hjemskjerm"
        `;
        installBtn.style.display = 'block';
        installBtn.onclick = () => {
            showToast('For å installere på iOS: Trykk deling-ikonet nederst og velg "Legg til på hjemskjerm"', 'info', 8000);
        };
    }
}

// Initialize PWA features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    checkInstallability();
    
    // Add install button event listener
    const installBtn = document.getElementById('installBtn');
    if (installBtn && !installBtn.onclick) {
        installBtn.onclick = installApp;
    }
});

// Notification permission request
function requestNotificationPermission() {
    if ('Notification' in window && navigator.serviceWorker) {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('Notification permission granted');
                showToast('Notifikasjoner aktivert!', 'success');
            }
        });
    }
}

// Auto-request notification permission after install
window.addEventListener('appinstalled', () => {
    setTimeout(requestNotificationPermission, 3000);
});
