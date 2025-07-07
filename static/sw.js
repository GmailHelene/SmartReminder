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

// Push notification handling
self.addEventListener('push', function(event) {
    console.log('[Service Worker] Push Received.');
    
    const options = {
        body: 'Du har en ny påminnelse!',
        icon: '/static/icon-192x192.png',
        badge: '/static/icon-192x192.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '2'
        },
        actions: [
            {
                action: 'explore',
                title: 'Åpne app',
                icon: '/static/icon-192x192.png'
            },
            {
                action: 'close',
                title: 'Lukk',
                icon: '/static/icon-192x192.png'
            }
        ]
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            options.body = data.message || data.body || options.body;
            options.title = data.title || 'SmartReminder';
            if (data.url) {
                options.data.url = data.url;
            }
            
            // Store sound info in the notification data
            if (data.sound) {
                options.data.sound = data.sound;
                options.silent = false;
            }
            
            // Set badge count if provided
            if (data.badgeCount) {
                options.badge = data.badgeCount;
            }
        } catch (e) {
            console.error('Error parsing push data:', e);
        }
    }
    
    // Show notification first
    const showNotificationPromise = self.registration.showNotification('SmartReminder', options);
    
    // Then trigger sound playback for all clients
    if (options.data && options.data.sound) {
        const soundToPlay = options.data.sound;
        console.log('[Service Worker] Will attempt to play notification sound:', soundToPlay);
        
        // Wait for notification to show, then trigger sound playback
        event.waitUntil(
            showNotificationPromise.then(() => {
                return self.clients.matchAll({
                    includeUncontrolled: true,
                    type: 'window'
                });
            }).then(clients => {
                console.log('[Service Worker] Found clients:', clients.length);
                
                let messageSent = false;
                
                if (clients.length > 0) {
                    // Send message to all clients to play the sound
                    clients.forEach(client => {
                        console.log('[Service Worker] Sending play sound message to client', client.id);
                        client.postMessage({
                            type: 'PLAY_NOTIFICATION_SOUND',
                            sound: soundToPlay
                        });
                        messageSent = true;
                    });
                }
                
                // If couldn't send message or no clients, create a fallback mechanism
                if (!messageSent) {
                    console.log('[Service Worker] No clients received message, creating a fallback');
                    // Store for later playback when app opens
                    return caches.open('sound-notifications').then(cache => {
                        return cache.put('/pending-sounds', new Response(JSON.stringify({
                            timestamp: Date.now(),
                            sound: soundToPlay
                        }), {
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        }));
                    });
                }
            })
        );
    } else {
        // Just show the notification if no sound
        event.waitUntil(showNotificationPromise);
    }
});

// Play notification sound (must be called from the main thread)
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'PLAY_NOTIFICATION_SOUND') {
        // We'll pass this message to the client to play the sound
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'PLAY_NOTIFICATION_SOUND',
                    sound: event.data.sound || 'pristine.mp3'
                });
            });
        });
    }
});

self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click Received.');
    
    const notification = event.notification;
    notification.close();
    
    // Try to play sound again when notification is clicked
    if (notification.data && notification.data.sound) {
        console.log('[Service Worker] Playing sound on notification click:', notification.data.sound);
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'PLAY_NOTIFICATION_SOUND',
                    sound: notification.data.sound
                });
            });
        });
    }
    
    // Handle action button or default click
    if (event.action === 'explore') {
        // Open the app
        event.waitUntil(clients.openWindow('/dashboard'));
    } else if (event.action === 'close') {
        // Just close the notification
        return;
    } else {
        // Default action - open the app
        event.waitUntil(clients.openWindow('/dashboard'));
    }
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