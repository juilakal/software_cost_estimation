// ═══════════════════════════════════════════════════════════════
// Planix – Service Worker (Offline-first with network fallback)
// ═══════════════════════════════════════════════════════════════

const CACHE_NAME = 'planix-v1';
const STATIC_ASSETS = [
    '/',
    '/login',
    '/register',
    '/history',
    '/static/style.css',
    '/static/script.js',
    '/static/icon-192.png',
    '/static/icon-512.png',
    '/static/manifest.json',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js'
];

// ── Install: cache static assets ───────────────────────────────
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// ── Activate: clean up old caches ──────────────────────────────
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// ── Fetch: network-first for API, cache-first for assets ──────
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // API calls → network first, no cache
    if (url.pathname.startsWith('/auth/') ||
        url.pathname.startsWith('/estimate/') ||
        url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                return new Response(
                    JSON.stringify({ detail: 'You are offline. Please check your connection.' }),
                    { status: 503, headers: { 'Content-Type': 'application/json' } }
                );
            })
        );
        return;
    }

    // Static assets → cache first, network fallback
    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) return cached;
            return fetch(event.request).then((response) => {
                // Cache successful GET responses
                if (response.ok && event.request.method === 'GET') {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return response;
            }).catch(() => {
                // Offline fallback for navigation
                if (event.request.mode === 'navigate') {
                    return caches.match('/login');
                }
            });
        })
    );
});
