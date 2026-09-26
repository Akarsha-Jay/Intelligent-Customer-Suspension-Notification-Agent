/**
 * API Client for Intelligent Customer Suspension Notification Agent.
 */

const API_BASE = '/api';

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchCustomers({ status, search, limit = 100, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (search) params.append('search', search);
  params.append('limit', limit);
  params.append('offset', offset);

  const res = await fetch(`${API_BASE}/customers?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch customers');
  return res.json();
}

export async function fetchSuspendedCustomers() {
  const res = await fetch(`${API_BASE}/customers/suspended`);
  if (!res.ok) throw new Error('Failed to fetch suspended customers');
  return res.json();
}

export async function updateCustomerStatus(landNumber, updateData) {
  const res = await fetch(`${API_BASE}/customers/${landNumber}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updateData),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to update customer');
  }
  return res.json();
}

export async function testCustomerNotification(landNumber) {
  const res = await fetch(`${API_BASE}/customers/${landNumber}/test-notification`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to test notification');
  }
  return res.json();
}

export async function runAgent() {
  const res = await fetch(`${API_BASE}/agent/run`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to trigger agent run');
  }
  return res.json();
}

export async function fetchAgentStatus() {
  const res = await fetch(`${API_BASE}/agent/status`);
  if (!res.ok) throw new Error('Failed to fetch agent status');
  return res.json();
}

export async function fetchAgentRuns(limit = 50) {
  const res = await fetch(`${API_BASE}/agent/runs?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch agent runs');
  return res.json();
}

export async function fetchNotifications({ status, channel, limit = 100, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (channel) params.append('channel', channel);
  params.append('limit', limit);
  params.append('offset', offset);

  const res = await fetch(`${API_BASE}/notifications?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch notifications');
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function toggleEmailMode() {
  const res = await fetch(`${API_BASE}/settings/toggle-mode`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to toggle email mode');
  return res.json();
}

export async function toggleWhatsAppMode() {
  const res = await fetch(`${API_BASE}/settings/toggle-whatsapp-mode`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to toggle WhatsApp mode');
  return res.json();
}

export async function updateChannelStrategy(strategy) {
  const res = await fetch(`${API_BASE}/settings/channel-strategy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ strategy }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to update channel strategy');
  }
  return res.json();
}

export async function testWhatsApp(recipientNumber) {
  const res = await fetch(`${API_BASE}/settings/test-whatsapp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recipient_number: recipientNumber }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to send test WhatsApp message');
  }
  return res.json();
}

export async function clearDataset() {
  const res = await fetch(`${API_BASE}/dataset/clear`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to clear dataset');
  return res.json();
}

export async function resetDataset() {
  return clearDataset();
}

export async function uploadDataset(file, clearCache = true) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/dataset/upload?clear_cache=${clearCache}`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let errorMsg = 'Failed to upload dataset';
    try {
      const err = await res.json();
      if (typeof err.detail === 'string') {
        errorMsg = err.detail;
      } else if (Array.isArray(err.detail)) {
        errorMsg = err.detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
      } else if (err.message) {
        errorMsg = err.message;
      }
    } catch {
      const text = await res.text().catch(() => '');
      if (text) errorMsg = text.slice(0, 200);
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export async function clearSystemCache(options = {}) {
  const params = new URLSearchParams();
  if (options.clearNotifications) params.append('clear_notifications', 'true');
  if (options.clearRuns) params.append('clear_runs', 'true');

  const res = await fetch(`${API_BASE}/cache/clear?${params.toString()}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to clear cache');
  }
  return res.json();
}

export function getTemplateDownloadUrl() {
  return `${API_BASE}/dataset/template`;
}

