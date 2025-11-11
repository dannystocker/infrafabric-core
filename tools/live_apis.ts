// tools/live_apis.ts - Minimal fetch helpers for live sources (node >=18)
import { readFileSync } from 'node:fs';

const BASE = new URL('.', import.meta.url);
function getConfig() {
  const txt = readFileSync(new URL('../config/live_sources.yaml', BASE), 'utf-8');
  // Minimal YAML parsing (naive) to avoid deps in example; replace with 'yaml' in production.
  return txt;
}

export async function fetchJSON(url: string): Promise<any> {
  const res = await fetch(url, { headers: { 'User-Agent': 'InfraFabric-Research/1.0' }});
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return await res.json();
}

export async function wikipediaSummary(title: string) {
  const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`;
  return fetchJSON(url);
}

export async function yahooQuote(symbol: string) {
  const url = `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${encodeURIComponent(symbol)}`;
  return fetchJSON(url);
}

export async function secCompanyFacts(cik: string) {
  const url = `https://data.sec.gov/api/xbrl/companyfacts/CIK${cik}.json`;
  return fetchJSON(url);
}

// Simple CLI
if (process.argv[2] === 'test') {
  const which = process.argv[3] || 'wikipedia';
  const arg = process.argv[4] || 'Epic Games';
  (async () => {
    if (which === 'wikipedia') console.log(await wikipediaSummary(arg));
    if (which === 'yahoo') console.log(await yahooQuote(arg));
    if (which === 'sec') console.log(await secCompanyFacts(arg));
  })().catch(e => { console.error(e); process.exit(1); });
}
