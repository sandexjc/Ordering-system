/*
 * dynamic/state.js
 * ----------------
 * Shared mutable state and constants for the dynamic orders page.
 *
 * Loaded first among dynamic/*.js from:
 *   - main/templates/dynamic/orders.html
 *
 * Consumed by all other dynamic/*.js modules (classic script globals).
 */

const viewOrdersCache = window.viewOrdersCache || new Map();
window.viewOrdersCache = viewOrdersCache;

let infiniteScrollObserver = null;
let isLoadingMore = false;
/** Bumped on every view switch / top-level render so stale async work cannot touch the wrong tab. */
let ordersRenderGeneration = 0;
let searchDebounceTimer = null;

const SEARCH_MIN_LENGTH = 2;
const SEARCH_DEBOUNCE_MS = 700;

/** Default list filters (newest by date, orders only, full id/balance range). */
const DEFAULT_ORDER_FILTERS = Object.freeze({
    sortBy: "date",
    sortDir: "desc",
    start: null,
    end: null,
    includeOrder: true,
    includeOffer: false,
    idMin: null,
    idMax: null,
    balanceMin: null,
    balanceMax: null,
});

const RANGE_FILTER_DEBOUNCE_MS = 300;
let rangeFilterDebounceTimer = null;
