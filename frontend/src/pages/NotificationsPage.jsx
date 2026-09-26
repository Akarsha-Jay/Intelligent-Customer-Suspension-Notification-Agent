import React, { useState, useEffect } from 'react';
import { Mail, MessageSquare, Eye, RefreshCw, Filter, CheckCircle2, Clock } from 'lucide-react';
import { fetchNotifications } from '../api';
import EmailModal from '../components/EmailModal';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [channelFilter, setChannelFilter] = useState('EMAIL'); // Default to Email view for zero customer repetition
  const [selectedNotif, setSelectedNotif] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchNotifications({
        status: statusFilter,
        channel: channelFilter,
        limit: 100,
      });
      setNotifications(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, channelFilter]);

  return (
    <div className="panel-card">
      <div className="panel-header">
        <div>
          <h2>Notification Dispatch Audit Log</h2>
          <div className="panel-subtitle">
            Historical trace of customer suspension notices organized by channel.
          </div>
        </div>

        <button className="btn-secondary" onClick={loadData}>
          <RefreshCw size={14} />
          <span>Refresh Logs</span>
        </button>
      </div>

      {/* Prominent Primary Channel Tabs (Solution 2) */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', flexWrap: 'wrap' }}>
        <button
          onClick={() => setChannelFilter('EMAIL')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 18px',
            borderRadius: 'var(--radius-md)',
            border: channelFilter === 'EMAIL' ? '1px solid #38bdf8' : '1px solid var(--border-color)',
            background: channelFilter === 'EMAIL' ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-elevated)',
            color: channelFilter === 'EMAIL' ? '#38bdf8' : 'var(--text-secondary)',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <Mail size={16} />
          <span>Email Dispatches</span>
        </button>

        <button
          onClick={() => setChannelFilter('WHATSAPP')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 18px',
            borderRadius: 'var(--radius-md)',
            border: channelFilter === 'WHATSAPP' ? '1px solid #25D366' : '1px solid var(--border-color)',
            background: channelFilter === 'WHATSAPP' ? 'rgba(37, 211, 102, 0.15)' : 'var(--bg-elevated)',
            color: channelFilter === 'WHATSAPP' ? '#25D366' : 'var(--text-secondary)',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <MessageSquare size={16} />
          <span>WhatsApp Dispatches</span>
        </button>

        <button
          onClick={() => setChannelFilter('')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 18px',
            borderRadius: 'var(--radius-md)',
            border: channelFilter === '' ? '1px solid var(--text-primary)' : '1px solid var(--border-color)',
            background: channelFilter === '' ? 'rgba(255, 255, 255, 0.1)' : 'var(--bg-elevated)',
            color: channelFilter === '' ? 'var(--text-primary)' : 'var(--text-secondary)',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <span>All Channels (Combined)</span>
        </button>
      </div>

      {/* Delivery Status Filter Pills */}
      <div className="filter-bar" style={{ marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Status:</span>
          <div className="filter-pills">
            <button
              className={`filter-pill ${statusFilter === '' ? 'active' : ''}`}
              onClick={() => setStatusFilter('')}
            >
              All Statuses ({notifications.length})
            </button>
            <button
              className={`filter-pill ${statusFilter === 'SENT' ? 'active' : ''}`}
              onClick={() => setStatusFilter('SENT')}
            >
              Sent
            </button>
            <button
              className={`filter-pill ${statusFilter === 'SIMULATED' ? 'active' : ''}`}
              onClick={() => setStatusFilter('SIMULATED')}
            >
              Simulated
            </button>
            <button
              className={`filter-pill ${statusFilter === 'SKIPPED' ? 'active' : ''}`}
              onClick={() => setStatusFilter('SKIPPED')}
            >
              Skipped
            </button>
            <button
              className={`filter-pill ${statusFilter === 'FAILED' ? 'active' : ''}`}
              onClick={() => setStatusFilter('FAILED')}
            >
              Failed
            </button>
          </div>
        </div>
      </div>

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Subscriber</th>
              <th>Landline</th>
              {channelFilter === '' && <th>Channel</th>}
              <th>{channelFilter === 'WHATSAPP' ? 'WhatsApp Phone' : 'Recipient Contact'}</th>
              <th>Category</th>
              <th>Subject / Title</th>
              <th>Delivery Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={channelFilter === '' ? 9 : 8} style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                  Loading dispatch history...
                </td>
              </tr>
            ) : notifications.length === 0 ? (
              <tr>
                <td colSpan={channelFilter === '' ? 9 : 8} style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                  No {channelFilter === 'EMAIL' ? 'email' : channelFilter === 'WHATSAPP' ? 'WhatsApp' : ''} notification records found in history.
                </td>
              </tr>
            ) : (
              notifications.map((n) => (
                <tr key={n.notification_id}>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {new Date(n.created_at).toLocaleString()}
                  </td>
                  <td style={{ fontWeight: 500 }}>{n.customer_name}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{n.land_number}</td>
                  {channelFilter === '' && (
                    <td>
                      <span
                        style={{
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          padding: '2px 8px',
                          borderRadius: '12px',
                          background: n.channel === 'WHATSAPP' ? 'rgba(37, 211, 102, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                          color: n.channel === 'WHATSAPP' ? '#25D366' : '#38bdf8',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        {n.channel === 'WHATSAPP' ? '💬 WhatsApp' : '✉️ Email'}
                      </span>
                    </td>
                  )}
                  <td style={{ fontSize: '0.8rem', color: n.channel === 'WHATSAPP' ? '#25D366' : 'var(--text-secondary)' }}>
                    {n.channel === 'WHATSAPP' ? (n.whatsapp_number || '—') : (n.email || '—')}
                  </td>
                  <td>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      {n.notification_type}
                    </span>
                  </td>
                  <td style={{ maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {n.subject}
                  </td>
                  <td>
                    <span className={`status-badge badge-${n.delivery_status.toLowerCase()}`}>
                      {n.delivery_status}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      className="btn-secondary"
                      style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                      onClick={() => setSelectedNotif(n)}
                      title="View complete generated notification"
                    >
                      <Eye size={13} />
                      <span>View Message</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedNotif && (
        <EmailModal
          notification={selectedNotif}
          onClose={() => setSelectedNotif(null)}
        />
      )}
    </div>
  );
}
