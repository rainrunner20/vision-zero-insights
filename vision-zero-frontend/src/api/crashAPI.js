// Returns anonymized crash-location records from the research backend.
// Never put administrator tokens or database secrets in browser code.
const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/+$/, '');

export async function fetchCrashData() {
  const res = await fetch(BASE + '/api/crashes');
  if (!res.ok) throw new Error('Crash data is temporarily unavailable.');
  const data = await res.json();
  if (!Array.isArray(data)) throw new Error('The server returned an invalid crash list.');
  return data;
}
