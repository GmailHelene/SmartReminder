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
    navigator.serviceWorker.register('/static/js/sw.js')
      .then((registration) => {
        console.log('Service Worker registrert:', registration.scope);
      })
      .catch((err) => {
        console.log('Service Worker registrering feilet:', err);
      });
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

// Form validation
document.addEventListener('DOMContentLoaded', function() {
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });
  
  // Auto-focus på første input
  const firstInput = document.querySelector('input[type="text"], input[type="email"]');
  if (firstInput) {
    firstInput.focus();
  }
  
  // Request notification permission on page load
  requestNotificationPermission();
});

// Offline form handling
function handleOfflineForm(formData) {
  const offlineData = JSON.parse(localStorage.getItem('offlineReminders') || '[]');
  offlineData.push({
    ...formData,
    timestamp: Date.now(),
    synced: false
  });
  localStorage.setItem('offlineReminders', JSON.stringify(offlineData));
  
  // Register background sync
  if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
    navigator.serviceWorker.ready.then(registration => {
      return registration.sync.register('background-sync');
    });
  }
  
  showNotification('Påminnelse lagret offline. Synkroniseres når du er tilbake online.', 'info');
}

// Share API for reminder sharing
async function shareReminder(title, text, url) {
  if (navigator.share) {
    try {
      await navigator.share({
        title: title,
        text: text,
        url: url
      });
      console.log('Deling vellykket');
    } catch (err) {
      console.log('Deling feilet:', err);
    }
  } else {
    // Fallback til clipboard
    if (navigator.clipboard) {
      navigator.clipboard.writeText(`${title}\n${text}\n${url}`)
        .then(() => showNotification('Kopiert til utklippstavle!', 'success'));
    }
  }
}