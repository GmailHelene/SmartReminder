console.log('🚀 PWA.js loading...');

// Global variables for PWA functionality
window.deferredPrompt = null;
window.isStandalone = false;
window.installPromptShown = false;

// Check if app is already installed
function checkInstallationStatus() {
    // Check if running in standalone mode
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
                        window.navigator.standalone === true;
    
    window.isStandalone = isStandalone;
    
    console.log('📱 Installation status:', {
        isStandalone: isStandalone,
        userAgent: navigator.userAgent,
        platform: navigator.platform
    });
    
    return isStandalone;
}

// Show install prompt
function showInstallPrompt() {
    if (window.installPromptShown) return;
    
    console.log('📱 Showing install prompt...');
    
    const installBanner = document.createElement('div');
    installBanner.id = 'pwa-install-banner';
    installBanner.innerHTML = `
        <div class="alert alert-info alert-dismissible fade show position-fixed" style="top: 10px; left: 10px; right: 10px; z-index: 9999; max-width: 400px; margin: 0 auto;">
            <div class="d-flex align-items-center">
                <i class="fas fa-mobile-alt me-2"></i>
                <div class="flex-grow-1">
                    <strong>Installer appen!</strong><br>
                    <small>Legg til SmartReminder på hjemskjermen for raskere tilgang</small>
                </div>
                <button type="button" class="btn btn-sm btn-primary me-2" onclick="installPWA()">
                    Installer
                </button>
                <button type="button" class="btn-close" onclick="hideInstallPrompt()"></button>
            </div>
        </div>
    `;
    
    document.body.appendChild(installBanner);
    window.installPromptShown = true;
    
    // Auto-hide after 15 seconds
    setTimeout(() => {
        hideInstallPrompt();
    }, 15000);
}

// Hide install prompt
function hideInstallPrompt() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
        banner.remove();
    }
}

// Install PWA
window.installPWA = function() {
    console.log('📱 Install PWA clicked');
    
    if (window.deferredPrompt) {
        console.log('📱 Using deferred prompt');
        window.deferredPrompt.prompt();
        
        window.deferredPrompt.userChoice.then((choiceResult) => {
            console.log('📱 User choice:', choiceResult.outcome);
            if (choiceResult.outcome === 'accepted') {
                console.log('✅ User accepted PWA installation');
            } else {
                console.log('❌ User declined PWA installation');
            }
            window.deferredPrompt = null;
            hideInstallPrompt();
        });
    } else {
        // Fallback for browsers that don't support beforeinstallprompt
        console.log('📱 No deferred prompt, showing manual instructions');
        showManualInstallInstructions();
    }
};

// Show manual install instructions
function showManualInstallInstructions() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    
    let instructions = '';
    
    if (isIOS) {
        instructions = `
            <div class="alert alert-info">
                <h6><i class="fab fa-apple me-2"></i>Installer på iOS:</h6>
                <ol class="mb-0 small">
                    <li>Trykk på del-knappen <i class="fas fa-share"></i> nederst</li>
                    <li>Velg "Legg til på hjemskjerm"</li>
                    <li>Trykk "Legg til"</li>
                </ol>
            </div>
        `;
    } else if (isAndroid) {
        instructions = `
            <div class="alert alert-info">
                <h6><i class="fab fa-android me-2"></i>Installer på Android:</h6>
                <ol class="mb-0 small">
                    <li>Trykk på meny-knappen <i class="fas fa-ellipsis-v"></i> øverst</li>
                    <li>Velg "Legg til på startskjermen" eller "Installer app"</li>
                    <li>Bekreft installasjonen</li>
                </ol>
            </div>
        `;
    } else {
        instructions = `
            <div class="alert alert-info">
                <h6><i class="fas fa-desktop me-2"></i>Installer på desktop:</h6>
                <p class="mb-0 small">Se etter installer-ikonet <i class="fas fa-plus"></i> i adresselinjen</p>
            </div>
        `;
    }
    
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Installer SmartReminder</h5>
                        <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                    </div>
                    <div class="modal-body">
                        ${instructions}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Lukk</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    hideInstallPrompt();
}

// Listen for beforeinstallprompt event
window.addEventListener('beforeinstallprompt', (e) => {
    console.log('📱 beforeinstallprompt event fired');
    
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    
    // Store the event so it can be triggered later
    window.deferredPrompt = e;
    
    // Show custom install prompt after a delay
    setTimeout(() => {
        if (!window.isStandalone && !window.installPromptShown) {
            showInstallPrompt();
        }
    }, 3000);
});

// Listen for app installed event
window.addEventListener('appinstalled', (e) => {
    console.log('✅ PWA was installed successfully');
    window.deferredPrompt = null;
    window.isStandalone = true;
    hideInstallPrompt();
    
    // Show success message
    if (typeof showToastNotification === 'function') {
        showToastNotification('📱 App installert! Du kan nå åpne SmartReminder fra hjemskjermen.', 'success');
    }
});

// Initialize PWA functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing PWA functionality...');
    
    // Check installation status
    const isInstalled = checkInstallationStatus();
    
    if (isInstalled) {
        console.log('✅ App is already installed');
        hideInstallPrompt();
    } else {
        console.log('📱 App not installed, will show prompt when appropriate');
        
        // For iOS Safari, show prompt immediately since beforeinstallprompt doesn't fire
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        if (isIOS) {
            setTimeout(() => {
                if (!window.installPromptShown) {
                    showInstallPrompt();
                }
            }, 5000);
        }
    }
});

console.log('✅ PWA.js loaded successfully');

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

// Enhanced mobile PWA installation
function checkMobileInstallability() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    
    if (isStandalone) {
        console.log('App is already running in standalone mode');
        hideInstallButton();
        return;
    }
    
    if (isIOS) {
        showIOSInstallInstructions();
    } else if (isAndroid) {
        // Android will show the beforeinstallprompt event
        console.log('Android device detected, waiting for install prompt');
    } else {
        // Desktop or other mobile
        console.log('Desktop or other device detected');
    }
}

// Show iOS install instructions
function showIOSInstallInstructions() {
    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
        installBtn.innerHTML = `
            <i class="fas fa-plus-circle"></i>
            Installer app
        `;
        installBtn.style.display = 'block';
        installBtn.onclick = () => {
            showToast(`
                <strong>Installer SmartReminder:</strong><br>
                1. Trykk på <i class="fas fa-share"></i> (Del) nederst på skjermen<br>
                2. Velg "Legg til på hjemskjerm"<br>
                3. Trykk "Legg til" øverst til høyre
            `, 'info', 12000);
        };
    }
}

// Enhanced Android install handling
function handleAndroidInstall() {
    if (window.deferredPrompt) {
        window.deferredPrompt.prompt();
        window.deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
                hideInstallButton();
                showToast('App installeres... 📱', 'success');
                
                // Request notification permission after install
                setTimeout(() => {
                    requestNotificationPermissionWithFallback();
                }, 2000);
            } else {
                console.log('User dismissed the install prompt');
                showToast('Du kan installere appen senere fra nettlesermenyen', 'info');
            }
            window.deferredPrompt = null;
        });
    }
}

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

// Enhanced notification permission request for PWA
function requestNotificationPermissionForPWA() {
    if (!('Notification' in window)) {
        console.log('Notifications not supported');
        return;
    }
    
    if (Notification.permission === 'granted') {
        console.log('Notifications already granted');
        return;
    }
    
    // Show explanation first
    showToast(`
        <strong>Aktiver varslinger</strong><br>
        Få beskjed om påminnelser selv når appen ikke er åpen
    `, 'info', 6000);
    
    setTimeout(() => {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showToast('Varslinger aktivert! 🔔', 'success');
                initializePushNotifications();
            } else {
                showToast('Varslinger er deaktivert. Du kan aktivere dem i nettleserinnstillingene.', 'warning', 8000);
            }
        });
    }, 2000);
}

// Auto-request notification permission after install
window.addEventListener('appinstalled', () => {
    setTimeout(requestNotificationPermission, 3000);
});
                showToast('Varslinger aktivert! 🔔', 'success');
                initializePushNotifications();
            } else {
                showToast('Varslinger er deaktivert. Du kan aktivere dem i nettleserinnstillingene.', 'warning', 8000);
            }
        });
    }, 2000);
}

// Auto-request notification permission after install
window.addEventListener('appinstalled', () => {
    setTimeout(requestNotificationPermission, 3000);
});
