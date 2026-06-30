import { Component, type ReactNode } from "react";

interface Props { children: ReactNode; }
interface State { error: Error | null; }

const RECOVERY_KEY = "wv-asset-recovery";

// Top-level safety net. A blank (black) page means an uncaught error crashed the
// React root before anything rendered into #root. This boundary turns that into a
// recoverable screen, and auto-recovers once from stale-asset errors that follow
// a PWA update (a cached index.html referencing a purged hashed chunk).
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error) {
    const msg = error?.message || "";
    if (/(dynamically imported module|importing a module script failed|ChunkLoadError|Loading chunk)/i.test(msg)) {
      try {
        if (!sessionStorage.getItem(RECOVERY_KEY)) {
          sessionStorage.setItem(RECOVERY_KEY, String(Date.now()));
          void this.hardReload();
        }
      } catch {
        /* sessionStorage unavailable — fall through to the manual reload button */
      }
    }
  }

  hardReload = async () => {
    try {
      if (typeof caches !== "undefined" && caches.keys) {
        const keys = await caches.keys();
        await Promise.all(keys.map((k) => caches.delete(k)));
      }
      if (navigator.serviceWorker?.getRegistrations) {
        const regs = await navigator.serviceWorker.getRegistrations();
        await Promise.all(regs.map((r) => r.unregister()));
      }
    } catch {
      /* best effort — reload regardless */
    }
    location.reload();
  };

  render() {
    if (this.state.error) {
      return (
        <div className="center-screen">
          <div className="card" style={{ maxWidth: 420, textAlign: "center", gap: 14 }}>
            <h1 className="title">Something went wrong</h1>
            <p className="muted">The app hit an unexpected error. Reloading usually fixes it.</p>
            <button className="btn btn-primary" onClick={this.hardReload}>Reload</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
