/* InstaFlow PWA Service Worker (Network First Strategy) */
const CACHE_NAME = "instaflow-v502";

self.addEventListener("install", (e) => {
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // APIs nunca devem ser cacheadas
  if (url.pathname.startsWith("/api/")) {
    return;
  }

  // Network First: Sempre busca a versão mais recente do servidor
  e.respondWith(
    fetch(e.request)
      .then((response) => {
        if (response && response.status === 200 && response.type === "basic") {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(e.request, responseToCache).catch(() => {});
          });
        }
        return response;
      })
      .catch(() => caches.match(e.request))
  );
});
