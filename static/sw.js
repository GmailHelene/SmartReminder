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
            options.body = data.message || options.body;
            options.title = data.title || 'SmartReminder';
            if (data.url) {
                options.data.url = data.url;
            }
        } catch (e) {
            console.error('Error parsing push data:', e);
        }
    }
    
    event.waitUntil(self.registration.showNotification('SmartReminder', options));
});

// Notification click event
self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click Received.');
    
    event.notification.close();
    
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