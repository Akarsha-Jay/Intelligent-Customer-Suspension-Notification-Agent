import React, { useState, useEffect } from 'react';
import { 
  Users, UserCheck, UserX, Send, 
  Play, RefreshCw, Eye, ArrowRight, CheckCircle2, Clock, Mail, UploadCloud
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import EmailModal from '../components/EmailModal';
import { fetchNotifications } from '../api';

export default function DashboardPage({ 
  stats, 
  settingsData,
  onUpdateStrategy,
  onRefresh, 
  setActiveTab
}) {
  const [recentNotifications, setRecentNotifications] = useState([]);
  const [loadingRecent, setLoadingRecent] = useState(false);
  const [dashboardChannel, setDashboardChannel] = useState('EMAIL'); // Default to Email view so customers are not repeated
  const [selectedNotif, setSelectedNotif] = useState(null);

  const currentStrategy = settingsData?.channel_strategy || 'BOTH';

  const loadRecent = async () => {
    setLoadingRecent(true);
    try {
      const res = await fetchNotifications({ limit: 6, channel: dashboardChannel });
      setRecentNotifications(res.items || []);
    } catch (err) {
      console.error('Error fetching recent notifications:', err);
    } finally {
      setLoadingRecent(false);
    }
  };

  useEffect(() => {
    loadRecent();
  }, [stats?.notifications_sent, dashboardChannel]);

  const handleManualRefresh = () => {
    if (onRefresh) onRefresh();
    loadRecent();
  };

  const isBusy = stats?.agent_status === 'RUNNING';

  return (
    <div>
      {/* Enterprise Operational Control Bar */}
      <div className="agent-banner">
        <div className="agent-banner-info">
          <div className={`status-dot-pulse ${isBusy ? 'busy' : ''}`} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>
                Suspension Notification Service
              </h2>
              <span 
                style={{ 
                  fontSize: '0.72rem', 
                  padding: '2px 8px', 
                  borderRadius: 'var(--radius-sm)', 
                  fontWeight: 600,
                  background: isBusy ? 'rgba(0, 144, 208, 0.15)' : 'var(--mobitel-green-tint)',
                  color: isBusy ? 'var(--slt-cyan)' : 'var(--mobitel-green)',
                  border: `1px solid ${isBusy ? 'rgba(0, 144, 208, 0.3)' : 'var(--mobitel-green-border)'}`
                }}
              >
                {isBusy ? 'RUNNING BATCH' : 'READY'}
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Last Run: {stats?.last_agent_run?.completed_at ? new Date(stats.last_agent_run.completed_at).toLocaleString() : 'No execution logged in current session'}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                Active Channel:
              </span>
              <div style={{ display: 'inline-flex', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '2px', gap: '2px' }}>
                <button
                  type="button"
                  onClick={() => onUpdateStrategy && onUpdateStrategy('WHATSAPP_ONLY')}
                  style={{
                    padding: '2px 8px',
                    fontSize: '0.72rem',
                    fontWeight: currentStrategy === 'WHATSAPP_ONLY' ? 600 : 400,
                    borderRadius: '4px',
                    border: 'none',
                    cursor: 'pointer',
                    background: currentStrategy === 'WHATSAPP_ONLY' ? '#25D366' : 'transparent',
                    color: currentStrategy === 'WHATSAPP_ONLY' ? '#000' : 'var(--text-secondary)',
                  }}
                  title="Send suspension notices solely via WhatsApp"
                >
                  💬 WhatsApp Only
                </button>
                <button
                  type="button"
                  onClick={() => onUpdateStrategy && onUpdateStrategy('EMAIL_ONLY')}
                  style={{
                    padding: '2px 8px',
                    fontSize: '0.72rem',
                    fontWeight: currentStrategy === 'EMAIL_ONLY' ? 600 : 400,
                    borderRadius: '4px',
                    border: 'none',
                    cursor: 'pointer',
                    background: currentStrategy === 'EMAIL_ONLY' ? '#38bdf8' : 'transparent',
                    color: currentStrategy === 'EMAIL_ONLY' ? '#000' : 'var(--text-secondary)',
                  }}
                  title="Send suspension notices solely via Email"
                >
                  ✉️ Email Only
                </button>
                <button
                  type="button"
                  onClick={() => onUpdateStrategy && onUpdateStrategy('BOTH')}
                  style={{
                    padding: '2px 8px',
                    fontSize: '0.72rem',
                    fontWeight: currentStrategy === 'BOTH' ? 600 : 400,
                    borderRadius: '4px',
                    border: 'none',
                    cursor: 'pointer',
                    background: currentStrategy === 'BOTH' ? 'var(--primary-color)' : 'transparent',
                    color: currentStrategy === 'BOTH' ? '#fff' : 'var(--text-secondary)',
                  }}
                  title="Send suspension notices to both Email and WhatsApp"
                >
                  🔄 Both Channels
                </button>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button className="btn-secondary" onClick={handleManualRefresh} title="Refresh Statistics">
            <RefreshCw size={13} />
            <span>Refresh Dashboard</span>
          </button>
        </div>
      </div>

      {stats?.total_customers === 0 && (
        <div 
          style={{
            background: 'var(--bg-elevated)',
            border: '1px dashed var(--border-color)',
            borderRadius: 'var(--radius-lg)',
            padding: '20px 24px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
            flexWrap: 'wrap'
          }}
        >
          <div>
            <h3 style={{ fontSize: '0.98rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
              No Customer Dataset Loaded
            </h3>
            <p style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', margin: 0 }}>
              The system operates exclusively with your uploaded customer files. Click <strong>"Upload New CSV"</strong> in the left sidebar to import customer records.
            </p>
          </div>
        </div>
      )}

      {/* KPI Metric Cards */}
      <div className="metrics-grid">
        <MetricCard
          title="Total Monitored Accounts"
          value={stats?.total_customers ?? '—'}
          footer="Active and suspended subscriber records"
          icon={Users}
          color="blue"
        />
        <MetricCard
          title="Active Services"
          value={stats?.active_customers ?? '—'}
          footer="Normal operational status"
          icon={UserCheck}
          color="emerald"
        />
        <MetricCard
          title="Suspended Accounts"
          value={stats?.suspended_customers ?? '—'}
          footer="Pending suspension notification"
          icon={UserX}
          color="rose"
        />
        <MetricCard
          title="Notifications Dispatched"
          value={stats?.notifications_sent ?? '—'}
          footer={`${stats?.notifications_skipped ?? 0} duplicates skipped`}
          icon={Send}
          color="cyan"
        />
      </div>

      {/* Recent Dispatches Section */}
      <div className="panel-card">
        <div className="panel-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2>Recent Notification Dispatches</h2>
            <div className="panel-subtitle">
              Audit log of recently generated suspension notices by channel.
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {/* Solution 2: Channel Quick Switcher on Dashboard */}
            <div className="filter-pills">
              <button
                className={`filter-pill ${dashboardChannel === 'EMAIL' ? 'active' : ''}`}
                onClick={() => setDashboardChannel('EMAIL')}
                style={{ fontSize: '0.78rem', padding: '4px 10px' }}
              >
                ✉️ Email
              </button>
              <button
                className={`filter-pill ${dashboardChannel === 'WHATSAPP' ? 'active' : ''}`}
                onClick={() => setDashboardChannel('WHATSAPP')}
                style={{ fontSize: '0.78rem', padding: '4px 10px' }}
              >
                💬 WhatsApp
              </button>
              <button
                className={`filter-pill ${dashboardChannel === '' ? 'active' : ''}`}
                onClick={() => setDashboardChannel('')}
                style={{ fontSize: '0.78rem', padding: '4px 10px' }}
              >
                All
              </button>
            </div>

            <button 
              className="btn-ghost" 
              onClick={() => setActiveTab('notifications')}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}
            >
              <span>View All</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {recentNotifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '36px 20px', color: 'var(--text-muted)', fontSize: '0.86rem' }}>
            No {dashboardChannel === 'EMAIL' ? 'email' : dashboardChannel === 'WHATSAPP' ? 'WhatsApp' : ''} notifications recorded yet. Click <strong>"RUN AGENT"</strong> to evaluate suspended accounts.
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Account / Landline</th>
                  <th>Customer Name</th>
                  {dashboardChannel === '' && <th>Channel</th>}
                  <th>{dashboardChannel === 'WHATSAPP' ? 'WhatsApp Phone' : 'Recipient Contact'}</th>
                  <th>Delivery Status</th>
                  <th>Category</th>
                  <th>Dispatched At</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentNotifications.map((notif) => (
                  <tr key={notif.notification_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{notif.land_number}</td>
                    <td>{notif.customer_name}</td>
                    {dashboardChannel === '' && (
                      <td>
                        <span
                          style={{
                            fontSize: '0.72rem',
                            fontWeight: 600,
                            padding: '2px 8px',
                            borderRadius: '12px',
                            background: notif.channel === 'WHATSAPP' ? 'rgba(37, 211, 102, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                            color: notif.channel === 'WHATSAPP' ? '#25D366' : '#38bdf8',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                        >
                          {notif.channel === 'WHATSAPP' ? '💬 WhatsApp' : '✉️ Email'}
                        </span>
                      </td>
                    )}
                    <td style={{ fontSize: '0.8rem', color: notif.channel === 'WHATSAPP' ? '#25D366' : 'var(--text-secondary)' }}>
                      {notif.channel === 'WHATSAPP' ? (notif.whatsapp_number || '—') : (notif.email || '—')}
                    </td>
                    <td>
                      <span className={`status-badge badge-${(notif.delivery_status || 'simulated').toLowerCase()}`}>
                        {notif.delivery_status}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                        {notif.notification_type || 'STANDARD'}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      {notif.sent_at ? new Date(notif.sent_at).toLocaleTimeString() : 'Pending'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn-secondary"
                        onClick={() => setSelectedNotif(notif)}
                        style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                      >
                        <Eye size={13} />
                        <span>View Notice</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Email Preview Modal */}
      {selectedNotif && (
        <EmailModal
          notification={selectedNotif}
          onClose={() => setSelectedNotif(null)}
        />
      )}
    </div>
  );
}
