// Powiadomienia push (US-086). Tylko wyświetlenie powiadomienia i otwarcie aplikacji po kliknięciu —
// bez pamięci podręcznej stron (aplikacja zawsze pobiera świeże dane z serwera).
self.addEventListener('push', event => {
  let data = {}
  try { data = event.data ? event.data.json() : {} } catch { data = {} }
  const title = typeof data.title === 'string' && data.title ? data.title : 'Kolejka'
  const url = typeof data.url === 'string' && data.url.startsWith('/') ? data.url : '/'
  event.waitUntil(self.registration.showNotification(title, {
    icon: '/icons/icon-192.png', badge: '/icons/icon-192.png', tag: data.tag || undefined,
    data: { url },
  }))
})

self.addEventListener('notificationclick', event => {
  event.notification.close()
  const target = new URL(event.notification.data?.url || '/', self.location.origin)
  if (target.origin !== self.location.origin) return          // tylko adresy tej aplikacji
  event.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
    const open = list.find(c => new URL(c.url).origin === target.origin)
    if (open) return open.navigate(target.href).then(c => (c || open).focus())
    return self.clients.openWindow(target.href)
  }))
})
