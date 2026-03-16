/** Append cache-bust query param so the browser fetches icons again. */
export function getIconUrl(icon: string, bust?: number): string {
  if (!bust) return icon;
  return `${icon}${icon.includes('?') ? '&' : '?'}v=${bust}`;
}

/** Resolve icon URL: use blob URL from icon bundle if available, else fall back to CDN path. */
export function getResolvedIconUrl(elementId: string, iconPath: string, bust?: number): string {
  // Dynamic import avoided — use the globally registered getter
  const blobUrl = _getIconBlobUrl?.(elementId);
  if (blobUrl) return blobUrl;
  return getIconUrl(iconPath, bust);
}

// Injected by loader.ts at startup to avoid circular imports
let _getIconBlobUrl: ((id: string) => string | null) | null = null;

export function registerIconBlobUrlGetter(getter: (id: string) => string | null): void {
  _getIconBlobUrl = getter;
}
