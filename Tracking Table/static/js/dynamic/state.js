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

function readDynamicContentInt(datasetKey, fallback)
{
    const root = document.getElementById("dynamic-orders-root");
    const value = Number.parseInt(root && root.dataset[datasetKey], 10);
    return Number.isFinite(value) ? value : fallback;
}

const SEARCH_MIN_LENGTH = readDynamicContentInt("searchMinLength", 2);
const SEARCH_DEBOUNCE_MS = readDynamicContentInt("searchDebounceMs", 700);
const ORDERS_SYNC_INTERVAL_MS = readDynamicContentInt("ordersSyncIntervalMs", 4000);
const LOCAL_MUTATION_SKIP_MS = readDynamicContentInt("localMutationSkipMs", 60000);

let isOrdersListFetchInFlight = 0;
let ordersSyncTimer = null;
let ordersSyncBackoffMs = ORDERS_SYNC_INTERVAL_MS;
const recentLocalOrderMutations = window.recentLocalOrderMutations || new Map();
window.recentLocalOrderMutations = recentLocalOrderMutations;
const ordersDetailsInFlight = window.ordersDetailsInFlight || new Set();
window.ordersDetailsInFlight = ordersDetailsInFlight;

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

const RANGE_FILTER_DEBOUNCE_MS = readDynamicContentInt("rangeFilterDebounceMs", 300);
let rangeFilterDebounceTimer = null;
