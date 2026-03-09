/** Append cache-bust query param so the browser fetches icons again. */
export function getIconUrl(icon: string, bust?: number): string {
  if (!bust) return icon;
  return `${icon}${icon.includes('?') ? '&' : '?'}v=${bust}`;
}
