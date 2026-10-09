/** Next catch-all route parameters are arrays, even for one encoded absolute path. */
export function decodeRoutePath(segments: string[]): string {
  return decodeURIComponent(segments.join('/'));
}
