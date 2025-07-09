// Enhanced PWA Installation and Updates
// Global variable for PWA install prompt
window.deferredPrompt = null;
let isInstalled = false;

// Enhanced mobile detection
function isMobileDevice() {
    return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function isIOSDevice() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent);
}

function isStandaloneMode() {
    return window.matchMedia && window.matchMedia('(display-mode: standalone)').matches;
}

// Enhanced beforeinstallprompt handling
window.addEventListener('beforeinstallprompt', (e) => {
    console.log('🚀 PWA install prompt ready');
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    window.deferredPrompt = e;
    // Show enhanced install button
    showInstallButton();
});

// Enhanced app installed event
window.addEventListener('appinstalled', () => {
    console.log('✅ PWA was installed successfully');
    hideInstallButton();
    isInstalled = true;
    
    // Show success message
    showToast('✅ App installert! Du kan nå bruke den fra hjemskjermen.', 'success', 6000);
    
    // Request notification permission after install
    setTimeout(() => {
        if ('Notification' in window && Notification.permission === 'default') {
            requestNotificationPermissionForPWA();
        }
    }, 2000);
});

// Enhanced Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        console.log('🔧 Registering Service Worker...');
        
        navigator.serviceWorker.register('/sw.js', { 
            scope: '/' 
        }).then((registration) => {
            console.log('✅ Service Worker registered successfully:', registration.scope);
            
            // Enhanced update detection
            registration.addEventListener('updatefound', () => {
                console.log('🔄 Service Worker update found');
                const newWorker = registration.installing;
                
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        console.log('📦 New Service Worker installed, showing update notification');
                        showUpdateAvailable();
                    }
                });
            });
            
            // Check for updates periodically
            setInterval(() => {
                console.log('🔍 Checking for Service Worker updates...');
                registration.update();
            }, 30000); // Check every 30 seconds
            
        }).catch((registrationError) => {
            console.error('❌ Service Worker registration failed:', registrationError);
        });
    });
}

// Enhanced install button functions
function showInstallButton() {
    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
        installBtn.style.display = 'block';
        installBtn.classList.add('pwa-install-banner');
        
        // Enhanced button styling for mobile
        if (isMobileDevice()) {
            installBtn.style.cssText += `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 9998;
                padding: 12px 24px;
                border-radius: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                animation: slideUp 0.3s ease-out;
            `;
        }
    }
    
    // Create install button if it doesn't exist
    if (!installBtn) {
        createInstallButton();
    }
}

function createInstallButton() {
    const button = document.createElement('button');
    button.id = 'installBtn';
    button.className = 'btn btn-primary pwa-install-btn';
    button.innerHTML = isIOSDevice() ? 
        '<i class="fas fa-plus-circle"></i> Installer app' : 
        '<i class="fas fa-download"></i> Installer app';
    
    // Mobile-optimized styling
    if (isMobileDevice()) {
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9998;
            padding: 12px 24px;
            border-radius: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            font-size: 16px;
            font-weight: bold;
            min-width: 200px;
            animation: slideUp 0.3s ease-out;
        `;
    }
    
    // Set click handler
    button.onclick = installApp;
    
    // Add to page
    document.body.appendChild(button);
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideUp {
            from {
                transform: translateX(-50%) translateY(100px);
                opacity: 0;
            }
            to {
                transform: translateX(-50%) translateY(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
}

function hideInstallButton() {
    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
        installBtn.style.display = 'none';
        installBtn.remove();
    }
}

// Enhanced install app function
function installApp() {
    console.log('🚀 User initiated app installation');
    
    if (isIOSDevice()) {
        // Show iOS installation instructions
        showIOSInstallInstructions();
    } else if (window.deferredPrompt) {
        // Android/Chrome installation
        handleAndroidInstall();
    } else {
        // Fallback for other browsers
        showToast('Installasjon støttes ikke i denne nettleseren', 'warning');
    }
}

// Enhanced iOS install instructions
function showIOSInstallInstructions() {
    const instructions = `
        <div class="text-center">
            <h5><i class="fab fa-apple"></i> Installer SmartReminder på iOS</h5>
            <div class="install-steps mt-3">
                <p class="mb-2">1. Trykk på <i class="fas fa-share" style="color: #007AFF;"></i> (Del) nederst på skjermen</p>
                <p class="mb-2">2. Velg <strong>"Legg til på hjemskjerm"</strong></p>
                <p class="mb-2">3. Trykk <strong>"Legg til"</strong> øverst til høyre</p>
                <p class="text-muted small">Appen vil da være tilgjengelig fra hjemskjermen din!</p>
            </div>
        </div>
    `;
    
    showToast(instructions, 'info', 15000);
}

// Enhanced Android install handling
function handleAndroidInstall() {
    console.log('📱 Handling Android installation');
    
    window.deferredPrompt.prompt();
    window.deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
            console.log('✅ User accepted the install prompt');
            hideInstallButton();
            showToast('📱 App installeres...', 'success', 3000);
            
            // Request notification permission after install
            setTimeout(() => {
                requestNotificationPermissionForPWA();
            }, 2000);
        } else {
            console.log('❌ User dismissed the install prompt');
            showToast('Du kan installere appen senere fra nettlesermenyen', 'info', 5000);
        }
        window.deferredPrompt = null;
    });
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
