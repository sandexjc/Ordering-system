/*
 * offline/service-worker.js
 * -------------------------
 * Site-root service worker. Network-first for page navigations; on network
 * failure, serve the cached offline page. Does not intercept AJAX/fetch.
 * Stylesheets, scripts, and images that were precached with the offline page
 * are served from cache when the network fails.
 *
 * Served from:
 *   - /sw.js  (main.views.offline.ServiceWorker)
 *
 * Precaches:
 *   - /offline/ and its stylesheet, script, and favicon
 *   - city-background.png
 *
 * The offline snapshot is stored once when the worker installs (first
 * successful visit, or when /sw.js itself changes). Static file hashing
 * busts CSS/JS URLs; CACHE_NAME is only the Cache Storage bucket.
 */

const CACHE_NAME = "ttable-offline";
const OFFLINE_URL = "/offline/";
const PRECACHE_URLS = [
    "/static/images/city-background.png",
];
const FETCH_RELOAD = { cache: "reload" };

/**
 * Collect stylesheet, script, and icon URLs from the offline HTML.
 *
 * @param {string} html - Rendered /offline/ markup.
 * @returns {string[]}
 */
function urlsFromOfflineHtml(html)
{
    const urls = [];
    const pattern = /(?:href|src)="([^"]+)"/g;
    let match = pattern.exec(html);
    while (match)
    {
        urls.push(match[1]);
        match = pattern.exec(html);
    }
    return urls;
}

/**
 * Fetch a URL, bypassing the HTTP cache, and store it.
 *
 * @param {Cache} cache - Open Cache Storage bucket.
 * @param {string} url - Same-origin URL to store.
 * @returns {Promise<Response|undefined>}
 */
function putReloadedUrl(cache, url)
{
    return fetch(url, FETCH_RELOAD).then(function (response) {
        if (!response.ok) {
            return undefined;
        }
        return cache.put(url, response);
    }).catch(function () {
        return undefined;
    });
}

/**
 * Replace the cached offline page and its assets with a fresh network copy.
 *
 * @param {Cache} cache - Open Cache Storage bucket.
 * @returns {Promise<void>}
 */
function precacheOfflinePage(cache)
{
    return fetch(OFFLINE_URL, FETCH_RELOAD).then(function (response) {
        if (!response.ok) {
            throw new Error("Offline page fetch failed.");
        }
        cache.put(OFFLINE_URL, response.clone());
        return response.text();
    }).then(function (html) {
        const urls = urlsFromOfflineHtml(html).concat(PRECACHE_URLS);
        return Promise.all(
            urls.map(function (url) {
                return putReloadedUrl(cache, url);
            })
        );
    });
}

/**
 * Open the offline cache, drop previous entries, and store a fresh snapshot.
 * Called on worker install, not on every page load.
 *
 * @returns {Promise<void>}
 */
function refreshOfflineCache()
{
    return caches.open(CACHE_NAME).then(function (cache) {
        return cache.keys().then(function (keys) {
            return Promise.all(
                keys.map(function (key) {
                    return cache.delete(key);
                })
            );
        }).then(function () {
            return precacheOfflinePage(cache);
        });
    });
}

self.addEventListener("install", function (event) {
    event.waitUntil(
        refreshOfflineCache().then(function () {
            return self.skipWaiting();
        })
    );
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys.filter(function (key) {
                    return key.indexOf("ttable-offline") === 0 && key !== CACHE_NAME;
                }).map(function (key) {
                    return caches.delete(key);
                })
            );
        }).then(function () {
            return self.clients.claim();
        })
    );
});

self.addEventListener("fetch", function (event) {
    if (event.request.method !== "GET") {
        return;
    }
    if (event.request.mode === "navigate") {
        event.respondWith(
            fetch(event.request).catch(function () {
                return caches.match(OFFLINE_URL).then(function (cached) {
                    return cached || Promise.reject();
                });
            })
        );
        return;
    }
    if (
        event.request.destination !== "style"
        && event.request.destination !== "script"
        && event.request.destination !== "image"
    ) {
        return;
    }
    event.respondWith(
        fetch(event.request).catch(function () {
            return caches.match(event.request).then(function (cached) {
                return cached || Promise.reject();
            });
        })
    );
});
