/** IndexedDB-backed persistence for the card catalog.
 *
 * One database, one store, one record (the latest fully-loaded catalog).
 * On every public method, IDB errors degrade silently to a console
 * warning + null/no-op return — the catalog still works without IDB,
 * we just lose the instant-paint optimization.
 */
import type { Card } from '../types/deck';

const DB_NAME = 'fireplace-catalog';
const DB_VERSION = 1;
const STORE = 'catalog';
const RECORD_KEY = 'latest';

export type CatalogRecord = {
  etag: string;
  cards: Card[];
  saved_at: number;
};

let _warnedUnavailable = false;

function warnOnce(msg: string) {
  if (!_warnedUnavailable) {
    _warnedUnavailable = true;
    // eslint-disable-next-line no-console
    console.warn(`[catalogStore] ${msg} — falling back to network-only`);
  }
}

function openDb(): Promise<IDBDatabase | null> {
  return new Promise((resolve) => {
    if (typeof indexedDB === 'undefined') {
      warnOnce('indexedDB unavailable');
      resolve(null);
      return;
    }
    let req: IDBOpenDBRequest;
    try {
      req = indexedDB.open(DB_NAME, DB_VERSION);
    } catch (e) {
      warnOnce(`open threw: ${(e as Error).message}`);
      resolve(null);
      return;
    }
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE);
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => {
      warnOnce(`open failed: ${req.error?.message ?? 'unknown'}`);
      resolve(null);
    };
    req.onblocked = () => {
      warnOnce('open blocked');
      resolve(null);
    };
  });
}

export async function get(): Promise<CatalogRecord | null> {
  const db = await openDb();
  if (!db) return null;
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(STORE, 'readonly');
      const req = tx.objectStore(STORE).get(RECORD_KEY);
      req.onsuccess = () => {
        const v = req.result as CatalogRecord | undefined;
        resolve(v ?? null);
      };
      req.onerror = () => {
        warnOnce(`get failed: ${req.error?.message ?? 'unknown'}`);
        resolve(null);
      };
    } catch (e) {
      warnOnce(`get threw: ${(e as Error).message}`);
      resolve(null);
    } finally {
      // db.close() is safe to call after the txn — it'll wait for txn end.
      db.close();
    }
  });
}

export async function put(record: CatalogRecord): Promise<void> {
  const db = await openDb();
  if (!db) return;
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).put(record, RECORD_KEY);
      tx.oncomplete = () => resolve();
      tx.onerror = () => {
        warnOnce(`put failed: ${tx.error?.message ?? 'unknown'}`);
        resolve();
      };
      tx.onabort = () => {
        warnOnce(`put aborted: ${tx.error?.message ?? 'quota?'}`);
        resolve();
      };
    } catch (e) {
      warnOnce(`put threw: ${(e as Error).message}`);
      resolve();
    } finally {
      db.close();
    }
  });
}

export async function clear(): Promise<void> {
  const db = await openDb();
  if (!db) return;
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).delete(RECORD_KEY);
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve();
    } catch {
      resolve();
    } finally {
      db.close();
    }
  });
}
