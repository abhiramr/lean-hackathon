/**
 * src/lib/api.js — API client for the Verified EDA backend.
 */

const BASE = '';  // Proxied via Vite in dev, same-origin in prod

export async function fetchHealth() {
  const res = await fetch(`${BASE}/api/health`);
  return res.json();
}

export async function fetchLeanStatus() {
  const res = await fetch(`${BASE}/api/lean/status`);
  return res.json();
}

export async function fetchDatasets() {
  const res = await fetch(`${BASE}/api/datasets`);
  return res.json();
}

export async function fetchDataset(name) {
  const res = await fetch(`${BASE}/api/datasets/${encodeURIComponent(name)}`);
  return res.json();
}

export async function runEDA(data, columns, datasetName = 'unnamed', bins = 12) {
  const res = await fetch(`${BASE}/api/eda/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data, columns, dataset_name: datasetName, bins }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function runVerification(data, columns, datasetName = 'unnamed', bins = 12) {
  const res = await fetch(`${BASE}/api/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data, columns, dataset_name: datasetName, bins }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchTheorems() {
  const res = await fetch(`${BASE}/api/theorems`);
  return res.json();
}

export async function checkLean(code) {
  const res = await fetch(`${BASE}/api/lean/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });
  return res.json();
}

export async function buildLean() {
  const res = await fetch(`${BASE}/api/lean/build`, { method: 'POST' });
  return res.json();
}

export async function uploadCSV(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/api/upload/csv`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/** WebSocket streaming verification */
export function streamVerification(data, columns, datasetName, bins, onMessage) {
  const ws = new WebSocket(`ws://${window.location.host}/ws/verify`);

  ws.onopen = () => {
    ws.send(JSON.stringify({ data, columns, dataset_name: datasetName, bins }));
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    onMessage(msg);
  };

  ws.onerror = (err) => {
    onMessage({ type: 'error', message: 'WebSocket error' });
  };

  ws.onclose = () => {
    onMessage({ type: 'close' });
  };

  return ws;
}
