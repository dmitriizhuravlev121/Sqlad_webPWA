```javascript
self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return new Response('Нет соединения', { status: 503 });
    })
  );
});

// Периодическая проверка соединения для синхронизации
self.addEventListener('periodicsync', event => {
  if (event.tag === 'sync-offline') {
    event.waitUntil(
      fetch('https://api.airtable.com/v0/ping', { method: 'HEAD' })
        .then(() => {
          self.clients.matchAll().then(clients => {
            clients.forEach(client => client.postMessage({ type: 'SYNC' }));
          });
        })
        .catch(() => {})
    );
  }
});
```