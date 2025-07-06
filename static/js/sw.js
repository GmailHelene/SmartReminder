const CACHE_NAME = 'smart-reminder-v1.0.0';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png',
  '/offline',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache åpnet');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.log('Cache install feil:', err))
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Returner cached versjon hvis den finnes
        if (response) {
          return response;
        }
        
        // Ellers hent fra nettverk
        return fetch(event.request)
          .then(response => {
            // Sjekk om vi fikk en gyldig response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Klon response
            const responseToCache = response.clone();
            
            // Legg til i cache
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            
            return response;
          })
          .catch(() => {
            // Hvis nettverket feiler, vis offline-side
            if (event.request.destination === 'document') {
              return caches.match('/offline');
            }
          });
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
            console.log('Sletter gammel cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Background sync for offline påminnelser
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  return fetch('/api/sync-offline-data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(response => {
    console.log('Background sync fullført');
  }).catch(err => {
    console.log('Background sync feilet:', err);
  });
}

// Push notifications
self.addEventListener('push', event => {
  let data = {};
  try {
    data = event.data.json();
  } catch {
    data = { body: event.data ? event.data.text() : 'Ny påminnelse!' };
  }
  const badgeCount = data.badgeCount || 1;
  const options = {
    body: data.body || 'Ny påminnelse!',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/badge-96x96.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1,
      badgeCount: badgeCount
    },
    actions: [
      {
        action: 'explore',
        title: 'Åpne app',
        icon: '/static/images/icon-192x192.png'
      },
      {
        action: 'close',
        title: 'Lukk',
        icon: '/static/images/icon-192x192.png'
      }
    ]
  };
  event.waitUntil(
    self.registration.showNotification('Smart Påminner Pro', options)
  );
});

// Notification click
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});