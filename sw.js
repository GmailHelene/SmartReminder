// Service Worker for SmartReminder
const CACHE_NAME = 'smartreminder-v1';
const OFFLINE_URL = '/offline.html';

// Files to cache
const CACHE_FILES = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/driving_school_mode.js',
    '/static/sounds/alert.mp3',
    '/static/sounds/pristine.mp3',
    '/static/sounds/ding.mp3',
    '/static/sounds/chime.mp3',
    OFFLINE_URL
];

// Install Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(CACHE_FILES))
            .then(() => self.skipWaiting())
    );
});

// Activate new version
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.filter(name => name !== CACHE_NAME)
                        .map(name => caches.delete(name))
                );
            })
            .then(() => self.clients.claim())
    );
});

// Handle push notifications
self.addEventListener('push', event => {
    const data = event.data.json();
    
    // Set up notification options
    const options = {
        body: data.body,
        icon: '/static/images/notification-icon.png',
        badge: '/static/images/badge-icon.png',
        tag: data.tag || 'default',
        requireInteraction: data.priority === 'high',
        vibrate: data.priority === 'high' 
            ? [200, 100, 200, 100, 200]  // High priority vibration
            : [100, 50, 100],            // Normal vibration
        data: {
            priority: data.priority || 'normal',
            url: data.url,
            sound: data.sound || 'pristine.mp3'
        }
    };

    // Show notification and play sound
    event.waitUntil(
        Promise.all([
            self.registration.showNotification(data.title, options),
            playNotificationSound(data.sound || 'pristine.mp3')
        ])
    );
});

// Play notification sound
async function playNotificationSound(soundName) {
    try {
        const soundUrl = `/static/sounds/${soundName}`;
        const audioContext = new (self.AudioContext || self.webkitAudioContext)();
        const response = await fetch(soundUrl);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        source.start(0);
    } catch (error) {
        console.error('Error playing sound:', error);
    }
}

// Handle notification click
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    // Open relevant URL if available
    if (event.notification.data.url) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});
