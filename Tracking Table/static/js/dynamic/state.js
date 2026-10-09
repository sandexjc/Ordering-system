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
/** Timed-out or failed polls required before the offline toast. Each poll is cancelled at the sync interval. */
const ORDERS_SYNC_MISS_LIMIT = 2;
/** Longest wait between reconnect attempts after the connection is dropped. */
const ORDERS_SYNC_BACKOFF_MAX_MS = 30000;
const LOCAL_MUTATION_SKIP_MS = readDynamicContentInt("localMutationSkipMs", 60000);

let isOrdersListFetchInFlight = 0;
let ordersSyncTimer = null;
/** Wait before the next reconnect attempt. Grows from the sync interval to 10s, then 30s. */
let ordersSyncBackoffMs = ORDERS_SYNC_INTERVAL_MS;
/** Bumped when the tab hides so in-flight heartbeats cannot move `since`. */
let ordersSyncGeneration = 0;
let ordersSyncAbort = null;
/** Bumped at the start of each heartbeat tick so a superseded poll cannot update status. */
let ordersSyncTickId = 0;
/** True while a sync fetch has started and has not yet returned (or been aborted). */
let ordersSyncAwaitingResponse = false;
/** True when the current tick received at least one successful HTTP response. */
let ordersSyncFetchSucceededThisTick = false;
/** When the next heartbeat / reconnect attempt is scheduled. */
let ordersSyncNextTickAt = 0;
/**
 * Consecutive polls that timed out or failed.
 * Reset when a poll succeeds. The offline toast waits until this reaches the miss limit.
 */
let ordersSyncMissStreak = 0;
/** Optimistic until two polls in a row time out or fail; page load already talked to the server. */
let isServerConnected = true;
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

const NOF_ORDERS_INIT_LOAD = readDynamicContentInt("nofOrdersInitLoad", 300);
const NOF_ORDERS_SECONDARY_LOAD = readDynamicContentInt("nofOrdersSecondaryLoad", 50);
const RANGE_FILTER_DEBOUNCE_MS = readDynamicContentInt("rangeFilterDebounceMs", 300);
const SYNC_HIGHLIGHT_MS = readDynamicContentInt("syncHighlightMs", 120000);
let rangeFilterDebounceTimer = null;

/** True while the table summarize card is open (row click selects instead of expanding). */
let isSummarizeMode = false;
const summarizeSelectedIds = window.summarizeSelectedIds || new Set();
window.summarizeSelectedIds = summarizeSelectedIds;
