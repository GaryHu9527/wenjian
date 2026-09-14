export function readStored(key, fallback, valid = () => true) {
  try { const data = JSON.parse(localStorage.getItem(key)); return data !== null && valid(data) ? data : fallback } catch { return fallback }
}
export function writeStored(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); return true } catch { return false }
}
export function safeUrl(value) {
  try { const u = new URL(value); return ['http:', 'https:'].includes(u.protocol) ? u.href : null } catch { return null }
}
