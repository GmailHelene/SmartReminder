const CACHE_NAME = 'smart-reminder-v1.0.0';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/js/pwa.js',
  '/offline'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        return fetch(event.request).then(
          response => {
            // Check if we received a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      }).catch(() => {
        // If both fail, show the offline page
        if (event.request.destination === 'document') {
          return caches.match('/offline');
        }
      })
  );
});

// Activate event
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Enhanced mobile push notification handling
self.addEventListener('push', function(event) {
    console.log('[Service Worker] Push Received.');
    
    let data = {};
    let options = {
        body: 'Du har en ny påminnelse!',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-96x96.png',
        vibrate: [200, 100, 200, 100, 200], // Enhanced vibration pattern
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '1',
            sound: 'pristine.mp3'
        },
        actions: [
            {
                action: 'open',
                title: 'Åpne app',
                icon: '/static/images/icon-192x192.png'
            },
            {
                action: 'close',
                title: 'Lukk',
                icon: '/static/images/icon-192x192.png'
            }
        ],
        requireInteraction: true, // Keep notification visible until user interacts
        silent: false, // Allow system sound
        tag: 'smartreminder-notification' // Group notifications
    };
    
    if (event.data) {
        try {
            data = event.data.json();
            options.body = data.message || data.body || options.body;
            options.title = data.title || 'SmartReminder';
            if (data.url) {
                options.data.url = data.url;
            }
            
            // Enhanced sound handling for mobile
            if (data.sound) {
                options.data.sound = data.sound;
                options.silent = false;
                
                // Add sound info to notification body for mobile users
                if (data.sound !== 'pristine.mp3') {
                    options.body += ` (${data.sound.replace('.mp3', '')})`;
                }
            }
            
            // Set badge count if provided
            if (data.badgeCount) {
                options.badge = data.badgeCount;
            }
            
            // Enhanced vibration for important notifications
            if (data.priority === 'high') {
                options.vibrate = [300, 100, 300, 100, 300];
                options.requireInteraction = true;
            }
        } catch (e) {
            console.error('Error parsing push data:', e);
        }
    }
    
    // Show notification first
    const showNotificationPromise = self.registration.showNotification(options.title || 'SmartReminder', options);
    
    // Enhanced sound handling for mobile
    const soundToPlay = options.data.sound;
    console.log('[Service Worker] Will attempt to play notification sound:', soundToPlay);
    
    // Wait for notification to show, then trigger sound playback
    event.waitUntil(
        showNotificationPromise.then(() => {
            return playNotificationSoundViaClients(soundToPlay);
        })
    );
});

// Enhanced function to play notification sound via active clients
function playNotificationSoundViaClients(soundFile) {
    return self.clients.matchAll({
        includeUncontrolled: true,
        type: 'window'
    }).then(clients => {
        console.log('[Service Worker] Found clients for sound playback:', clients.length);
        
        let messageSent = false;
        
        if (clients.length > 0) {
            // Send message to all clients to play the sound
            clients.forEach(client => {
                console.log('[Service Worker] Sending play sound message to client', client.id);
                client.postMessage({
                    type: 'PLAY_NOTIFICATION_SOUND',
                    sound: soundFile,
                    timestamp: Date.now(),
                    isMobile: /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
                });
                messageSent = true;
            });
        }
        
        // Enhanced fallback mechanism for mobile
        if (!messageSent) {
            console.log('[Service Worker] No clients received message, creating enhanced fallback');
            // Store for later playback when app opens
            return caches.open('sound-notifications').then(cache => {
                return cache.put('/pending-sounds', new Response(JSON.stringify({
                    timestamp: Date.now(),
                    sound: soundFile,
                    isMobile: true,
                    notificationId: 'smartreminder-notification'
                }), {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }));
            });
        }
    });
}

// Enhanced notification click handling
self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click Received.');
    
    const notification = event.notification;
    const action = event.action;
    
    notification.close();
    
    // Handle different actions
    if (action === 'close') {
        console.log('[Service Worker] Notification closed by user');
        return;
    }
    
    // Default action or 'open' action
    let urlToOpen = '/dashboard';
    if (notification.data && notification.data.url) {
        urlToOpen = notification.data.url;
    }
    
    // Try to play sound again when notification is clicked (for mobile)
    if (notification.data && notification.data.sound) {
        console.log('[Service Worker] Playing sound on notification click:', notification.data.sound);
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'PLAY_NOTIFICATION_SOUND',
                    sound: notification.data.sound,
                    fromClick: true
                });
            });
        });
    }
    
    // Enhanced window handling for mobile
    event.waitUntil(
        self.clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        }).then(clientList => {
            // Check if app is already open
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if (client.url.includes(urlToOpen) && 'focus' in client) {
                    return client.focus();
                }
            }
            
            // Open new window if not already open
            if (self.clients.openWindow) {
                return self.clients.openWindow(urlToOpen);
            }
        })
    );
});

// Background sync for board updates
self.addEventListener('sync', function(event) {
    if (event.tag === 'board-update-sync') {
        event.waitUntil(syncBoardUpdates());
    }
});

function syncBoardUpdates() {
    // Sync offline board updates when connection is restored
    return fetch('/api/sync-board-updates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).catch(error => {
        console.error('Background sync failed:', error);
    });
}

// Message handling for client communication
self.addEventListener('message', function(event) {
    console.log('[Service Worker] Message received:', event.data);
    
    if (event.data && event.data.type === 'PLAY_NOTIFICATION_SOUND') {
        // Client is asking us to play a sound
        const soundFile = event.data.sound || 'pristine.mp3';
        console.log('[Service Worker] Playing sound requested by client:', soundFile);
        
        // Send the sound request back to all clients
        playNotificationSoundViaClients(soundFile);
    }
    
    if (event.data && event.data.type === 'CLIENT_READY') {
        // Client is ready to receive messages
        console.log('[Service Worker] Client is ready for messages');
        
        // Check if there are any pending sounds
        caches.open('sound-notifications').then(cache => {
            cache.match('/pending-sounds').then(response => {
                if (response) {
                    response.json().then(data => {
                        // Check if the sound notification is recent (last 10 minutes)
                        const now = Date.now();
                        const tenMinutesAgo = now - (10 * 60 * 1000);
                        
                        if (data.timestamp > tenMinutesAgo) {
                            console.log('[Service Worker] Playing pending sound for ready client:', data.sound);
                            event.ports[0].postMessage({
                                type: 'PLAY_NOTIFICATION_SOUND',
                                sound: data.sound,
                                pending: true
                            });
                        }
                        
                        // Clear the pending sound
                        cache.delete('/pending-sounds');
                    });
                }
            });
        });
    }
});